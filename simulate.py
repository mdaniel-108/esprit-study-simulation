"""ESPRIT precision and power simulation (fast implementation).

Design:
  * Scenarios are defined by the expected number of learners who complete at least four of
    six activities (A4 = 25, 40, 60). Completion follows a per-activity dropout hazard, so the
    number of randomized learners N is larger than A4 and is reported.
  * Policy sequences are assigned in permuted blocks of all 20 possible 3+3 sequences, so each
    activity receives each policy equally often within every complete block.
  * Inference is calibrated: every scenario is also run with a true effect of zero. Three
    standard errors are computed on the same simulated data:
      - 'cr0'   : CR0 x n/(n-1) with fixed critical values, for comparison;
      - 'model' : model-based OLS standard error with residual degrees of freedom
                  (within design; equivalent to the fixed-effects analysis);
      - 'cr2'   : bias-reduced cluster-robust (CR2) standard error with t(G-1) critical values
                  (G-2 for the by-learner design).
  * Coverage for bounded 0-6 scores is checked against the effect on the observed score scale.
  * Sensitivity analyses: bounded 0-6 rubric scores, three carryover forms, assistant uptake of
    90%, 70% and 50% (and 70% with help-seeking that depends on prior knowledge, policy and
    activity difficulty), policy-dependent dropout, and the policy x prior-knowledge interaction (H3m).

Implementation: learner fixed effects are absorbed by centring within learners (Frisch-Waugh-Lovell),
which gives exactly the same estimates and standard errors as including one dummy per learner;
CR2 adjustments are computed in batches of learners with the same number of completed activities.
`reference_slow.py` contains the direct (dummy-variable) implementation used to verify this.

Data-generating model (latent standardized outcome, total variance about 1):
  y_ij = a_j + u_i + d*GI_ij*Used_ij + carry_ij + g*GI_ij*z_i + e_ij
  a_j ~ N(0, 0.3^2), u_i ~ N(0, rho), e_ij ~ N(0, 1-rho); rho = intraclass correlation
  z_i  standardized prior-knowledge pre-test, correlated 0.71 with u_i

Run:  python simulate.py --reps 2000 --out results --jobs 4
"""
import argparse, csv, json, os, itertools, time
from functools import lru_cache
from multiprocessing import Pool
import numpy as np
from scipy import stats

K = 6
SEED = 20261025
SEQS = np.array([s for s in itertools.product([0, 1], repeat=K) if sum(s) == K // 2])  # 20 sequences
THRESH = np.array([-1.5, -0.9, -0.3, 0.3, 0.9, 1.5])  # latent score -> 0..6 rubric score

@lru_cache(maxsize=None)
def tcrit(df):
    return float(stats.t.ppf(0.975, df))

def n_randomized(a4, h):
    return int(np.ceil(a4 / (1 - h) ** 3))   # P(complete >= 4 activities) = (1-h)^3

def assign(rng, n, design):
    if design == 'within':
        blocks = -(-n // len(SEQS))
        idx = np.concatenate([rng.permutation(len(SEQS)) for _ in range(blocks)])[:n]
        return SEQS[idx]
    blocks = -(-n // 2)
    g = np.concatenate([rng.permutation(2) for _ in range(blocks)])[:n]
    return np.repeat(g[:, None], K, axis=1)

def simulate_data(rng, p):
    """Return one simulated study as flat arrays (rows sorted by learner, then activity)."""
    n, h, rho, d = p['n'], p['h'], p['rho'], p['d']
    u = rng.normal(0, np.sqrt(rho), n)
    z = np.sqrt(0.5) * u / np.sqrt(rho) + np.sqrt(0.5) * rng.normal(0, 1, n)
    act = rng.normal(0, 0.3, K)
    seq = assign(rng, n, p['design'])
    # dropout after activity j (j = 0..4), with optional extra hazard after guided inquiry
    haz = np.full((n, K - 1), h)
    gd = p.get('gi_drop', 0.0)
    if gd > 0:
        mult = np.where(u < 0, 2.0, 1.0) if p.get('mnar') else np.ones(n)
        haz = haz + gd * mult[:, None] * seq[:, :K - 1]
    cont = rng.random((n, K - 1)) >= haz
    last = 1 + np.cumprod(cont, axis=1).sum(axis=1)
    mask = np.arange(K)[None, :] < last[:, None]
    i_, j_ = np.nonzero(mask)
    t_ = seq[i_, j_].astype(float)
    carry = np.zeros(len(i_))
    c, form = p.get('c', 0.0), p.get('carry_form')
    if c:
        prior_count = np.cumsum(seq, axis=1) - seq
        anyprior = (prior_count > 0)[i_, j_]
        prev = np.concatenate([np.zeros((n, 1), int), seq[:, :-1]], axis=1)[i_, j_]
        carry = {'persistent': c * anyprior, 'decaying': c * prev, 'negative': -c * anyprior}[form]
    used = np.ones(len(i_))
    nu = p.get('nonuse', 0.0)
    if nu > 0:
        if p.get('nonuse_dep'):
            raw = 0.2 * (z[i_] > 0) + 0.1 * t_ + 0.1 * (act[j_] < 0)   # knowledgeable learners, guided inquiry, easier activities
            prob = np.clip(raw - raw.mean() + nu, 0, 1)
        else:
            prob = np.full(len(i_), nu)
        used = (rng.random(len(i_)) >= prob).astype(float)
    y0 = act[j_] + u[i_] + carry + p.get('g', 0.0) * t_ * z[i_] + rng.normal(0, np.sqrt(1 - rho), len(i_))
    y = y0 + d * t_ * used
    obs_target, sd0 = None, None
    if p.get('bounded'):
        # estimand on the observed 0-6 scale: average change in score if every completed activity
        # were learned under guided inquiry rather than explanation-first
        s0 = np.digitize(y0, THRESH).astype(float)
        obs_target = float(np.mean(np.digitize(y0 + d, THRESH) - s0))
        sd0 = float(np.std(s0))
        y = np.digitize(y, THRESH).astype(float)
    itt = d * used[t_ == 1].mean() if (t_ == 1).any() else d
    return dict(n=n, i=i_, j=j_, t=t_, z=z, y=y, last=last, itt=itt, obs_target=obs_target, sd0=sd0)

def _cr2_meat(Xd, e, M, starts, sizes, centred):
    """Sum over clusters of s_g s_g' with CR2 adjustment; clusters batched by size."""
    k = Xd.shape[1]
    meat = np.zeros((k, k))
    for s in np.unique(sizes):
        g = np.nonzero(sizes == s)[0]
        idx = starts[g][:, None] + np.arange(s)[None, :]           # (G_s, s)
        Xs, es = Xd[idx], e[idx]                                    # (G_s, s, k), (G_s, s)
        A = np.eye(s)[None] - np.einsum('gak,kl,gbl->gab', Xs, M, Xs)
        if centred:
            A = A - 1.0 / s
        w, Q = np.linalg.eigh((A + np.swapaxes(A, 1, 2)) / 2)
        inv = np.where(w > 1e-8, 1.0 / np.sqrt(np.clip(w, 1e-12, None)), 0.0)
        adj = np.einsum('gab,gb,gcb,gc->ga', Q, inv, Q, es)
        sc = np.einsum('gak,ga->gk', Xs, adj)
        meat += sc.T @ sc
    return meat

def estimate(D, p):
    """Fit the analysis model; return estimate and the three standard errors with their df."""
    n, i_, j_, t_, z, y = D['n'], D['i'], D['j'], D['t'], D['z'], D['y']
    inter = p.get('test') == 'interaction'
    act = np.eye(K)[j_][:, 1:]
    counts = np.bincount(i_, minlength=n)
    starts = np.concatenate([[0], np.cumsum(counts)[:-1]])
    if p['design'] == 'within':
        W = np.column_stack([t_] + ([t_ * z[i_]] if inter else []) + [act])
        def centre(a):
            sums = np.zeros((n,) + a.shape[1:])
            np.add.at(sums, i_, a)
            return a - (sums / counts.reshape((-1,) + (1,) * (a.ndim - 1)))[i_]
        Xd, yd = centre(W), centre(y)
        idx = 1 if inter else 0
        centred, df_cr2 = True, n - 1
    else:
        Xd = np.column_stack([np.ones(len(y)), t_] + ([t_ * z[i_], z[i_]] if inter else []) + [act])
        yd = y
        idx = 2 if inter else 1
        centred, df_cr2 = False, n - 2
    M = np.linalg.pinv(Xd.T @ Xd)
    beta = M @ Xd.T @ yd
    e = yd - Xd @ beta
    out = dict(est=beta[idx], df_cr2=df_cr2)
    # CR0 x n/(n-1)
    sc = np.zeros((n, Xd.shape[1])); np.add.at(sc, i_, Xd * e[:, None])
    out['se_cr0'] = np.sqrt((M @ (sc.T @ sc) @ M)[idx, idx] * n / (n - 1))
    # CR2
    out['se_cr2'] = np.sqrt((M @ _cr2_meat(Xd, e, M, starts, counts, centred) @ M)[idx, idx])
    # model-based (within design)
    if p['design'] == 'within':
        r = np.linalg.matrix_rank(Xd)
        df = len(y) - n - r
        out['se_model'] = np.sqrt(e @ e / df * M[idx, idx]); out['df_model'] = df
    return out

def run_config(args):
    cid, p, reps, seed = args
    rng = np.random.default_rng(seed)
    cr0c = 2.06 if p['n'] <= 25 else (2.02 if p['n'] <= 40 else 2.0)
    est, itt, nobs, a4, obs_t, sd0 = [], [], [], [], [], []
    se = {'cr2': [], 'model': [], 'cr0': []}; cr = {'cr2': [], 'model': [], 'cr0': []}
    for _ in range(reps):
        D = simulate_data(rng, p)
        o = estimate(D, p)
        est.append(o['est']); itt.append(D['itt']); nobs.append(len(D['y'])); a4.append(int((D['last'] >= 4).sum()))
        if D['obs_target'] is not None:
            obs_t.append(D['obs_target']); sd0.append(D['sd0'])
        se['cr2'].append(o['se_cr2']); cr['cr2'].append(tcrit(o['df_cr2']))
        se['cr0'].append(o['se_cr0']); cr['cr0'].append(cr0c)
        if 'se_model' in o:
            se['model'].append(o['se_model']); cr['model'].append(tcrit(o['df_model']))
    est = np.array(est)
    if p.get('test') == 'interaction':
        target = p.get('g', 0.0)
    elif p.get('bounded'):
        target = float(np.mean(obs_t))
    elif p.get('nonuse'):
        target = float(np.mean(itt))
    else:
        target = p['d']
    res = dict(cid=cid, mean_est=round(float(est.mean()), 4), target=round(target, 4),
               score_sd=round(float(np.mean(sd0)), 4) if sd0 else '',
               mean_obs=round(float(np.mean(nobs)), 1), mean_a4=round(float(np.mean(a4)), 1))
    for m in ('cr2', 'model', 'cr0'):
        if not se[m]:
            continue
        sm, cm = np.array(se[m]), np.array(cr[m])
        res[f'reject_{m}'] = round(float(np.mean(np.abs(est / sm) > cm)), 4)
        res[f'cover_{m}'] = round(float(np.mean(np.abs(est - target) <= cm * sm)), 4)
        res[f'ci_half_{m}'] = round(float(np.median(cm * sm)), 4)
    return {**p, **res}

SCEN = [('Conservative', 25), ('Moderate', 40), ('Optimistic', 60)]

def grid():
    H = 0.15
    for name, a4 in SCEN:                       # 1. calibration at d = 0
        for rho in (0.3, 0.5):
            for design in ('within', 'by_learner'):
                yield dict(analysis='calibration', scenario=name, a4=a4, h=H, rho=rho, d=0.0, design=design)
    for name, a4 in SCEN:                       # 2. main power and precision grid
        for rho in (0.3, 0.5):
            for d in (0.2, 0.3, 0.5):
                for design in ('within', 'by_learner'):
                    yield dict(analysis='main', scenario=name, a4=a4, h=H, rho=rho, d=d, design=design)
    for rho in (0.3, 0.5):                      # 3. high attrition (hazard 0.30), moderate scenario
        for d in (0.0, 0.3, 0.5):
            for design in ('within', 'by_learner'):
                yield dict(analysis='high_attrition', scenario='Moderate', a4=40, h=0.30, rho=rho, d=d, design=design)
    for name, a4 in SCEN:                       # 4. bounded 0-6 rubric scores
        for rho in (0.3, 0.5):
            for d in (0.0, 0.3, 0.5):
                yield dict(analysis='bounded', scenario=name, a4=a4, h=H, rho=rho, d=d, design='within', bounded=True)
    for name, a4 in SCEN[1:]:                   # 5. carryover forms
        for rho in (0.3, 0.5):
            for form in ('persistent', 'decaying', 'negative'):
                yield dict(analysis='carryover', scenario=name, a4=a4, h=H, rho=rho, d=0.3, design='within', c=0.15, carry_form=form)
    for name, a4 in SCEN:                       # 6. assistant uptake below 100%
        for rho in (0.3, 0.5):
            for d in (0.2, 0.3, 0.5):
                for uptake, dep in ((0.9, False), (0.7, False), (0.5, False), (0.7, True)):
                    yield dict(analysis='uptake', scenario=name, a4=a4, h=H, rho=rho, d=d, design='within',
                               nonuse=round(1 - uptake, 2), nonuse_dep=dep, uptake=uptake)
    for name, a4 in SCEN[1:]:                   # 7. policy-dependent dropout
        for rho in (0.3, 0.5):
            for mnar in (False, True):
                yield dict(analysis='diff_dropout', scenario=name, a4=a4, h=H, rho=rho, d=0.3, design='within', gi_drop=0.10, mnar=mnar)
    for name, a4 in SCEN:                       # 8. H3m: policy x prior-knowledge interaction
        for rho in (0.3, 0.5):
            for gval in (0.0, 0.25):
                yield dict(analysis='h3m', scenario=name, a4=a4, h=H, rho=rho, d=0.3, design='within', g=gval, test='interaction')

def configs():
    cs = list(grid())
    for p in cs:
        p['n'] = n_randomized(p['a4'], p['h'])
    return cs

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--reps', type=int, default=2000)
    ap.add_argument('--out', default='results')
    ap.add_argument('--jobs', type=int, default=os.cpu_count() or 1)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    cs = configs()
    seeds = np.random.SeedSequence(SEED).spawn(len(cs))
    jobs = [(i, p, a.reps, s) for i, (p, s) in enumerate(zip(cs, seeds))]
    rows, t0 = [], time.time()
    with Pool(a.jobs) as pool:
        for k, r in enumerate(pool.imap_unordered(run_config, jobs), 1):
            rows.append(r)
            print(f"[{k}/{len(jobs)}] {r['analysis']:<14} {r['scenario']:<12} {r['design']:<10} d={r['d']} "
                  f"elapsed {time.time() - t0:5.0f}s", flush=True)
    keys = sorted({k for r in rows for k in r}, key=lambda k: (k not in ('cid', 'analysis', 'scenario'), k))
    with open(os.path.join(a.out, 'results.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=keys); w.writeheader()
        for r in sorted(rows, key=lambda r: r['cid']):
            w.writerow(r)
    json.dump(dict(seed=SEED, reps=a.reps, K=K, configs=len(cs)), open(os.path.join(a.out, 'run_info.json'), 'w'), indent=1)
    print('done', len(rows), f'{time.time() - t0:.0f}s')

if __name__ == '__main__':
    main()
