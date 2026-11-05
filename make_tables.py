"""Build results/results.md and results/proposal_table.md from results/results.csv."""
import csv, collections, sys
import numpy as np
from decimal import Decimal, ROUND_HALF_UP

sys.stdout.reconfigure(encoding='utf-8')
PRIMARY = {'within': 'model', 'by_learner': 'cr2'}   # calibrated method used for reported power
rows = list(csv.DictReader(open('results/results.csv')))

def q(v, nd=2):
    return str(Decimal(str(v)).quantize(Decimal('1.' + '0' * nd), rounding=ROUND_HALF_UP))

def rng(vals, nd=2, pct=False):
    vals = [float(v) for v in vals if v not in ('', None)]
    if pct:
        vals = [v * 100 for v in vals]; nd = 1
    s = sorted({q(v, nd) for v in vals}, key=float)
    if not s:
        return '–'
    return (s[0] if len(s) == 1 else f"{s[0]}–{s[-1]}") + ('%' if pct else '')

def sel(**kw):
    return [r for r in rows if all(str(r.get(k)) == str(v) for k, v in kw.items())]

def prim(r, metric):
    return r[f"{metric}_{PRIMARY[r['design']]}"]

SC = ['Conservative', 'Moderate', 'Optimistic']
out = ["# ESPRIT simulation results", "",
       "Values are ranges over the intraclass correlation ρ = 0.3 and 0.5; 2,000 replications per configuration "
       "(Monte Carlo error: about ±1 percentage point for a 5% rate, about ±2 for power near 50%). "
       "Scenarios are defined by the expected number of learners completing at least four of six activities (A4); "
       "with a per-activity dropout hazard of 0.15, this requires N randomized learners, all of whom are analysed. "
       f"Reported power uses the calibrated method: model-based standard errors for the within-learner design and CR2 cluster-robust standard errors for the by-learner design.", ""]

out += ["## 1. Calibration: false-positive rate when the true effect is zero (target 5%)", "",
        "| Scenario | N randomized | Learners with 4+ | Design | CR0, fixed critical values | Model-based | CR2 |", "|---|---|---|---|---|---|---|"]
for s in SC:
    for d in ('within', 'by_learner'):
        v = sel(analysis='calibration', scenario=s, design=d)
        out.append(f"| {s} | {v[0]['n']} | {rng([x['mean_a4'] for x in v], 0)} | {d} | {rng([x['reject_cr0'] for x in v], pct=True)} | "
                   f"{rng([x.get('reject_model') for x in v], pct=True)} | {rng([x['reject_cr2'] for x in v], pct=True)} |")

out += ["", "## 2. Main grid: precision and power (dropout hazard 0.15)", "",
        "| Scenario | N randomized | Learners with 4+ | Design | 95% CI half-width (SD) | Power d = 0.2 | Power d = 0.3 | Power d = 0.5 | Coverage |",
        "|---|---|---|---|---|---|---|---|---|"]
for s in SC:
    for d in ('within', 'by_learner'):
        v = sel(analysis='main', scenario=s, design=d)
        pw = {dd: rng([prim(x, 'reject') for x in v if float(x['d']) == dd]) for dd in (0.2, 0.3, 0.5)}
        out.append(f"| {s} | {v[0]['n']} | {rng([x['mean_a4'] for x in v], 0)} | {d} | {rng([prim(x, 'ci_half') for x in v])} | "
                   f"{pw[0.2]} | {pw[0.3]} | {pw[0.5]} | {rng([prim(x, 'cover') for x in v], pct=True)} |")

out += ["", "## 3. High attrition (hazard 0.30), moderate scenario", "",
        "| Design | N randomized | Learners with 4+ | False positives (d = 0) | Power d = 0.3 | Power d = 0.5 |", "|---|---|---|---|---|---|"]
for d in ('within', 'by_learner'):
    v = sel(analysis='high_attrition', design=d)
    f = lambda dd: rng([prim(x, 'reject') for x in v if float(x['d']) == dd], pct=(dd == 0.0)) if dd == 0.0 else rng([prim(x, 'reject') for x in v if float(x['d']) == dd])
    out.append(f"| {d} | {v[0]['n']} | {rng([x['mean_a4'] for x in v], 0)} | {f(0.0)} | {f(0.3)} | {f(0.5)} |")

out += ["", "## 4. Bounded 0–6 rubric scores (within-learner design)", "",
        "Effects are generated on the latent scale (d) and analysed on the observed 0–6 score. The target is the average change in score points if every completed activity were learned under guided inquiry; coverage is checked against that target. The standardized target divides it by the SD of scores under explanation-first.", "",
        "| Scenario | Latent d | Target (score points) | Standardized target | Mean estimate | Coverage of target | Power (d > 0) / false positives (d = 0) |", "|---|---|---|---|---|---|---|"]
for s_ in SC:
    for dd in (0.0, 0.3, 0.5):
        v = [x for x in sel(analysis='bounded', scenario=s_) if float(x['d']) == dd]
        std = rng([float(x['target']) / float(x['score_sd']) for x in v]) if dd > 0 else '0.00'
        pw = rng([x['reject_model'] for x in v], pct=(dd == 0))
        out.append(f"| {s_} | {dd} | {rng([x['target'] for x in v])} | {std} | {rng([x['mean_est'] for x in v])} | {rng([x['cover_model'] for x in v], pct=True)} | {pw} |")

out += ["", "## 5. Carryover forms (within-learner design, true immediate effect d = 0.3, carryover 0.15 SD)", "",
        "| Scenario | Carryover form | Mean estimate | Coverage of 0.3 | Power |", "|---|---|---|---|---|"]
for s in SC[1:]:
    for form in ('persistent', 'decaying', 'negative'):
        v = sel(analysis='carryover', scenario=s, carry_form=form)
        out.append(f"| {s} | {form} | {rng([x['mean_est'] for x in v])} | {rng([x['cover_model'] for x in v], pct=True)} | {rng([x['reject_model'] for x in v])} |")

out += ["", "## 6. Assistant uptake below 100% (within-learner design)", "",
        "d is the effect when the assistant is used. The intention-to-treat (ITT) target is d times the share of guided-inquiry activities on which the assistant is used. In the dependent variant, help-seeking is lower for learners with above-average prior knowledge, under guided inquiry and on easier activities, with the same 70% average uptake.", "",
        "| Scenario | Uptake | d | ITT target | Mean estimate | Coverage of target | Power |", "|---|---|---|---|---|---|---|"]
for s_ in SC:
    for up, dep in (('1.0', None), ('0.9', 'False'), ('0.7', 'False'), ('0.5', 'False'), ('0.7', 'True')):
        for dd in (0.2, 0.3, 0.5):
            if up == '1.0':
                v = [x for x in sel(analysis='main', scenario=s_, design='within') if float(x['d']) == dd]
                lab = '100%'
            else:
                v = [x for x in sel(analysis='uptake', scenario=s_, uptake=up, nonuse_dep=dep) if float(x['d']) == dd]
                lab = f"{float(up):.0%}" + (' (dependent)' if dep == 'True' else '')
            out.append(f"| {s_} | {lab} | {dd} | {rng([x['target'] for x in v])} | {rng([x['mean_est'] for x in v])} | {rng([x['cover_model'] for x in v], pct=True)} | {rng([x['reject_model'] for x in v])} |")

out += ["", "## 7. Policy-dependent dropout (within-learner design, d = 0.3)", "",
        "Hazard rises by 0.10 after guided-inquiry activities; in the ability-related variant, by 0.20 for below-average learners.", "",
        "| Scenario | Ability-related | Learners with 4+ | Mean estimate | Coverage of 0.3 | Power |", "|---|---|---|---|---|---|"]
for s in SC[1:]:
    for mn in ('False', 'True'):
        v = sel(analysis='diff_dropout', scenario=s, mnar=mn)
        out.append(f"| {s} | {'yes' if mn == 'True' else 'no'} | {rng([x['mean_a4'] for x in v], 0)} | {rng([x['mean_est'] for x in v])} | "
                   f"{rng([x['cover_model'] for x in v], pct=True)} | {rng([x['reject_model'] for x in v])} |")

out += ["", "## 8. H3m: policy × prior-knowledge interaction (within-learner design)", "",
        "| Scenario | False positives (g = 0) | Power for g = 0.25 SD per SD |", "|---|---|---|"]
for s in SC:
    v = sel(analysis='h3m', scenario=s)
    out.append(f"| {s} | {rng([x['reject_model'] for x in v if float(x['g']) == 0], pct=True)} | {rng([x['reject_model'] for x in v if float(x['g']) == 0.25])} |")

from scipy.stats import binom
def n_for_prob(a4, h, prob, consent=1.0):
    p4 = consent * (1 - h) ** 3
    n = a4
    while binom.sf(a4 - 1, n, p4) < prob:
        n += 1
    return n
out += ["", "## 9. Recruitment: randomized learners needed to reach the completer target", "",
        "Each randomized learner completes four or more activities with probability (1 − h)³. The expected-value N gives the target on average; the other columns give the N needed to reach it with 80% or 95% probability (binomial model). Enrollment columns include uncertainty in consent: each enrollee consents with probability 0.20, independently of completion, so the target is reached with the stated probability from that many enrollments.", "",
        "| Completers with 4+ | Hazard h | N randomized (expected) | P(reach target) at that N | N randomized for 80% | N randomized for 95% | Enrollments for 80% at 20% consent | Enrollments for 95% at 20% consent |", "|---|---|---|---|---|---|---|---|"]
for a4, h in ((25, 0.15), (40, 0.15), (60, 0.15), (40, 0.30)):
    ne = int(np.ceil(a4 / (1 - h) ** 3)); pr = binom.sf(a4 - 1, ne, (1 - h) ** 3)
    n95 = n_for_prob(a4, h, 0.95)
    out.append(f"| {a4} | {h} | {ne} | {pr:.0%} | {n_for_prob(a4, h, 0.80)} | {n95} | {n_for_prob(a4, h, 0.80, 0.2)} | {n_for_prob(a4, h, 0.95, 0.2)} |")
open('results/results.md', 'w', encoding='utf-8').write('\n'.join(out) + '\n')

# Proposal-ready table (Section 4.2)
pt = ["| Scenario | Learners: with 4+ activities / randomized | 95% CI half-width (SD): within / by learner | Power, d = 0.3: within / by learner | Power, d = 0.3, 70% uptake: within | Power, d = 0.2: within |",
      "|---|---|---|---|---|---|"]
for s in SC:
    w = sel(analysis='main', scenario=s, design='within'); b = sel(analysis='main', scenario=s, design='by_learner')
    pw = lambda v, dd: rng([prim(x, 'reject') for x in v if float(x['d']) == dd])
    u70 = [x for x in sel(analysis='uptake', scenario=s, uptake='0.7') if float(x['d']) == 0.3]
    pt.append(f"| {s} | {rng([x['mean_a4'] for x in w], 0)} / {w[0]['n']} | {rng([prim(x, 'ci_half') for x in w])} / {rng([prim(x, 'ci_half') for x in b])} | "
              f"{pw(w, 0.3)} / {pw(b, 0.3)} | {rng([x['reject_model'] for x in u70])} | {pw(w, 0.2)} |")
open('results/proposal_table.md', 'w', encoding='utf-8').write('\n'.join(pt) + '\n')
print('\n'.join(out)); print(); print('\n'.join(pt))
