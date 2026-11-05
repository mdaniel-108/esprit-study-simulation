"""ESPRIT precision and power simulation: direct dummy-variable implementation.

Used only by check_equivalence.py to verify the fast implementation in simulate.py.

Data-generating model (latent standardized outcome, total variance about 1):
  y_ij = a_j + u_i + d*GI_ij*Used_ij + carry_ij + g*GI_ij*z_i + e_ij
  a_j ~ N(0, 0.3^2), u_i ~ N(0, rho), e_ij ~ N(0, 1-rho); rho = intraclass correlation
  z_i  standardized prior-knowledge pre-test, correlated 0.71 with u_i
"""
import argparse, csv, json, os, itertools
from multiprocessing import Pool
import numpy as np
from scipy import stats

K = 6
SEED = 20261024
SEQS = np.array([s for s in itertools.product([0, 1], repeat=K) if sum(s) == K // 2])  # 20 sequences
THRESH = np.array([-1.5, -0.9, -0.3, 0.3, 0.9, 1.5])  # latent -> 0..6 rubric score

def p_at_least(k, h):
    return (1 - h) ** (k - 1)

def n_randomized(a4, h):
    return int(np.ceil(a4 / p_at_least(4, h)))

def assign(rng, n, design):
    if design == 'within':
        blocks = int(np.ceil(n / len(SEQS)))
        idx = np.concatenate([rng.permutation(len(SEQS)) for _ in range(blocks)])[:n]
        return SEQS[idx]
    blocks = int(np.ceil(n / 2))
    g = np.concatenate([rng.permutation(2) for _ in range(blocks)])[:n]
    return np.repeat(g[:, None], K, axis=1)

def cr2_se(X, res, cl, XtX_inv, idx):
    meat = np.zeros((X.shape[1],) * 2)
    for g in np.unique(cl):
        m = cl == g
        Xg = X[m]
        M = np.eye(m.sum()) - Xg @ XtX_inv @ Xg.T
        w, Q = np.linalg.eigh((M + M.T) / 2)
        inv_sqrt = np.where(w > 1e-8, 1.0 / np.sqrt(np.clip(w, 1e-12, None)), 0.0)
        ug = (Q * inv_sqrt) @ Q.T @ res[m]
        s = Xg.T @ ug
        meat += np.outer(s, s)
    V = XtX_inv @ meat @ XtX_inv
    return np.sqrt(V[idx, idx])

def cr0_se(X, res, cl, XtX_inv, idx, n):
    meat = np.zeros((X.shape[1],) * 2)
    for g in np.unique(cl):
        m = cl == g
        s = X[m].T @ res[m]
        meat += np.outer(s, s)
    V = XtX_inv @ meat @ XtX_inv * n / (n - 1)
    return np.sqrt(V[idx, idx])

def one_trial(rng, p):
    n, h, rho, d, design = p['n'], p['h'], p['rho'], p['d'], p['design']
    u = rng.normal(0, np.sqrt(rho), n)
    z = np.sqrt(0.5) * u / np.sqrt(rho) + np.sqrt(0.5) * rng.normal(0, 1, n)
    act = rng.normal(0, 0.3, K)
    seq = assign(rng, n, design)
    rows = []
    for i in range(n):
        last = 1
        while last < K:
            hz = h + (p.get('gi_drop', 0.0) * (2.0 if (p.get('mnar') and u[i] < 0) else 1.0) if seq[i, last - 1] == 1 else 0.0)
            if rng.random() < hz:
                break
            last += 1
        for j in range(last):
            rows.append((i, j))
    r = np.array(rows); i_, j_ = r[:, 0], r[:, 1]
    t_ = seq[i_, j_]
    # carryover
    carry = np.zeros(len(r))
    c, form = p.get('c', 0.0), p.get('carry_form', 'none')
    if c != 0.0:
        prev = np.where(j_ > 0, seq[i_, np.maximum(j_ - 1, 0)], 0)
        anyprior = np.array([seq[a, :b].sum() > 0 for a, b in zip(i_, j_)])
        if form == 'persistent':
            carry = c * anyprior
        elif form == 'decaying':
            carry = c * prev
        elif form == 'negative':
            carry = -c * anyprior
    # non-use
    used = np.ones(len(r))
    nu = p.get('nonuse', 0.0)
    if nu > 0:
        if p.get('nonuse_dep'):
            prob = np.clip(nu + 0.2 * (z[i_] > 0) + 0.1 * t_ - 0.15, 0, 1)
        else:
            prob = np.full(len(r), nu)
        used = (rng.random(len(r)) >= prob).astype(float)
    gint = p.get('g', 0.0)
    y = act[j_] + u[i_] + d * t_ * used + carry + gint * t_ * z[i_] + rng.normal(0, np.sqrt(1 - rho), len(r))
    if p.get('bounded'):
        y = np.digitize(y, THRESH).astype(float)
    itt_target = d * used[t_ == 1].mean() if (t_ == 1).any() else d
    # design matrix
    if design == 'within':
        cols = [t_]
        if p.get('test') == 'interaction':
            cols.append(t_ * z[i_])
        X = np.column_stack(cols + [np.eye(n)[i_], np.eye(K)[j_][:, 1:]])
        idx = 1 if p.get('test') == 'interaction' else 0
        df_cr2 = n - 1
    else:
        cols = [np.ones(len(r)), t_]
        if p.get('test') == 'interaction':
            cols += [t_ * z[i_], z[i_]]
        X = np.column_stack(cols + [np.eye(K)[j_][:, 1:]])
        idx = 2 if p.get('test') == 'interaction' else 1
        df_cr2 = n - 2
    XtX_inv = np.linalg.pinv(X.T @ X)
    beta = XtX_inv @ X.T @ y
    res = y - X @ beta
    rank = np.linalg.matrix_rank(X)
    out = dict(est=beta[idx], itt=itt_target, n_obs=len(r), a4=float(np.mean(np.bincount(i_, minlength=n) >= 4) * n))
    out['se_cr2'] = cr2_se(X, res, i_, XtX_inv, idx); out['df_cr2'] = df_cr2
    out['se_cr0'] = cr0_se(X, res, i_, XtX_inv, idx, n)
    if design == 'within':
        s2 = res @ res / (len(r) - rank)
        out['se_model'] = np.sqrt(s2 * XtX_inv[idx, idx]); out['df_model'] = len(r) - rank
    return out

def run_config(args):
    cid, p, reps, seed = args
    rng = np.random.default_rng(seed)
    cr0crit = 2.06 if p['n'] <= 25 else (2.02 if p['n'] <= 40 else 2.0)
    est, itt, nobs, a4 = [], [], [], []
    se = {'cr2': [], 'model': [], 'cr0': []}; crit = {'cr2': [], 'model': [], 'cr0': []}
    for _ in range(reps):
        o = one_trial(rng, p)
        est.append(o['est']); itt.append(o['itt']); nobs.append(o['n_obs']); a4.append(o['a4'])
        se['cr2'].append(o['se_cr2']); crit['cr2'].append(stats.t.ppf(0.975, o['df_cr2']))
        se['cr0'].append(o['se_cr0']); crit['cr0'].append(cr0crit)
        if 'se_model' in o:
            se['model'].append(o['se_model']); crit['model'].append(stats.t.ppf(0.975, o['df_model']))
    est = np.array(est)
    if p.get('test') == 'interaction':
        target = p.get('g', 0.0)
    elif p.get('nonuse'):
        target = float(np.mean(itt))
    else:
        target = p['d']
    res = dict(cid=cid, mean_est=round(float(est.mean()), 4), target=round(target, 4),
               mean_obs=round(float(np.mean(nobs)), 1), mean_a4=round(float(np.mean(a4)), 1))
    for m in ('cr2', 'model', 'cr0'):
        if not se[m]:
            continue
        sm, cm = np.array(se[m]), np.array(crit[m])
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
    for name, a4 in SCEN[1:]:                   # 6. non-use: random vs ability- and policy-dependent
        for rho in (0.3, 0.5):
            for dep in (False, True):
                yield dict(analysis='nonuse', scenario=name, a4=a4, h=H, rho=rho, d=0.5, design='within', nonuse=0.3, nonuse_dep=dep)
    for name, a4 in SCEN[1:]:                   # 7. policy-dependent dropout
        for rho in (0.3, 0.5):
            for mnar in (False, True):
                yield dict(analysis='diff_dropout', scenario=name, a4=a4, h=H, rho=rho, d=0.3, design='within', gi_drop=0.10, mnar=mnar)
    for name, a4 in SCEN:                       # 8. H3m: policy x prior-knowledge interaction
        for rho in (0.3, 0.5):
            for gval in (0.0, 0.25):
                yield dict(analysis='h3m', scenario=name, a4=a4, h=H, rho=rho, d=0.3, design='within', g=gval, test='interaction')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--reps', type=int, default=2000)
    ap.add_argument('--out', default='results')
    ap.add_argument('--jobs', type=int, default=2)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    configs = list(grid())
    for p in configs:
        p['n'] = n_randomized(p['a4'], p['h'])
    seeds = np.random.SeedSequence(SEED).spawn(len(configs))
    jobs = [(i, p, a.reps, s) for i, (p, s) in enumerate(zip(configs, seeds))]
    with Pool(a.jobs) as pool:
        rows = pool.map(run_config, jobs, chunksize=1)
    keys = sorted({k for r in rows for k in r}, key=lambda k: (k not in ('cid', 'analysis', 'scenario'), k))
    with open(os.path.join(a.out, 'results.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=keys); w.writeheader()
        for r in sorted(rows, key=lambda r: r['cid']):
            w.writerow(r)
    json.dump(dict(seed=SEED, reps=a.reps, K=K, configs=len(configs)), open(os.path.join(a.out, 'run_info.json'), 'w'), indent=1)
    print('done', len(rows))

if __name__ == '__main__':
    main()
