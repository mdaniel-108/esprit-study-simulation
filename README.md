# ESPRIT study simulation

Precision and power simulation for the study in the FWF ESPRIT proposal *From Interaction to Understanding: Measuring and Shaping How Learners Learn with AI* (TU Graz, Educational Technology), Section 4.2.

The study compares two AI assistance policies, **explanation-first** and **guided inquiry**, across six MOOC learning activities. In the preferred within-learner design, each learner receives each policy on three of the six activities. A by-learner design, in which each learner receives one policy throughout, is simulated for comparison.

The simulation answers three planning questions: how precisely the policy effect can be estimated, how much power the study has under realistic dropout and assistant use, and how many learners must be recruited.

## Running it

Requires Python 3.9 or later. Run all commands from the repository root.

```bash
pip install -r requirements.txt
python simulate.py --reps 2000 --out results   # writes results/results.csv and results/run_info.json
python check_equivalence.py                    # optional: compares the fast estimator with reference_slow.py
python make_tables.py                          # writes results/results.md and results/proposal_table.md
python make_figure.py                          # writes results/figure_power_uptake.png
```

`simulate.py` uses all CPU cores by default; set `--jobs` to change this. Each configuration has its own random stream derived from the fixed seed `20261025`, so results do not depend on the order or number of parallel jobs.

## Files

```
simulate.py                      simulation (fast implementation)
reference_slow.py                direct dummy-variable implementation, used only for verification
check_equivalence.py             checks that both implementations give identical estimates and standard errors
make_tables.py                   builds the summary and proposal tables from results.csv
make_figure.py                   draws power by assistant uptake from results.csv
requirements.txt                 Python packages
results/results.csv              all 182 configurations, all methods
results/results.md               summary tables
results/proposal_table.md        table for Section 4.2 of the proposal
results/figure_power_uptake.png  power by assistant uptake (Figure 2 of the proposal)
results/run_info.json            seed, replications, number of configurations
```

## Data-generating model

For learner *i* on activity *j* (latent standardized outcome, total variance about 1):

```
y_ij = a_j + u_i + d · GI_ij · Used_ij + carry_ij + g · GI_ij · z_i + e_ij
a_j ~ N(0, 0.3²)    activity difficulty, 6 activities in a fixed curricular order
u_i ~ N(0, ρ)       learner effect; e_ij ~ N(0, 1 − ρ); ρ = intraclass correlation (0.3 or 0.5)
z_i                 standardized prior-knowledge pre-test, correlated 0.71 with u_i
GI_ij               1 if the activity is assigned guided inquiry
Used_ij             1 if the assistant was used (always 1 unless non-use is simulated)
carry_ij            carryover from earlier guided-inquiry activities (sensitivity analyses only)
```

- **Scenarios:** conservative, moderate and optimistic scenarios are defined by the expected number of learners completing at least four activities (25, 40 and 60).
- **Assignment:** within-learner sequences are assigned in permuted blocks of all 20 possible 3 + 3 sequences, so each activity receives each policy equally often within every complete block.
- **Completion:** every randomized learner completes activity 1, then drops out after each activity with hazard *h* (0.15; 0.30 as a sensitivity analysis). With *h* = 0.15, 61% of learners complete four or more activities, so a target of 40 such learners requires 66 randomized learners.

## Analysis

- **Within-learner design (primary):** OLS with learner and activity fixed effects. Learner effects are absorbed by centring within learners, which is numerically identical to one dummy per learner (see `check_equivalence.py`). Model-based standard errors with residual degrees of freedom are primary, and CR2 cluster-robust standard errors with t(G − 1) are a robustness check.
- **By-learner design:** OLS with activity effects and CR2 cluster-robust standard errors, t(G − 2).
- **Comparison estimator:** CR0 standard errors scaled by n/(n − 1) with fixed critical values are computed on the same data and reported in the calibration table only.

## Simulated conditions

The 182 configurations each use 2,000 replications:

| Analysis | What varies |
|---|---|
| Calibration | True effect of zero, to check false-positive rates |
| Main grid | Effect size d = 0.2, 0.3, 0.5 in all scenarios and both designs |
| High attrition | Dropout hazard of 0.30 in the moderate scenario |
| Bounded scores | Observed 0–6 rubric scores instead of the continuous outcome |
| Carryover | Persistent, decaying and negative carryover of 0.15 SD |
| Assistant uptake | 90%, 70% and 50% random uptake, and 70% uptake that depends on prior knowledge, policy and activity difficulty |
| Policy-dependent dropout | Higher dropout after guided inquiry, with and without a link to ability |
| H3m | Policy × prior-knowledge interaction of 0 and 0.25 SD per SD |

## Main findings

Numbers are ranges over ρ = 0.3–0.5. See `results/results.md` for all tables.

1. **The tests are calibrated** under the simulated model. With a true effect of zero, model-based and CR2 tests reject 4.3–6.3% of the time across scenarios, and 95% confidence intervals cover the target about 94–96% of the time in the main grid. This holds under these data-generating assumptions, not under every possible outcome or missingness model.
2. **Recruitment.** The moderate scenario is 40 learners completing four or more activities. With a dropout hazard of 0.15, that is expected with 66 randomized learners but reached with 95% probability only with **76**. Allowing for uncertainty in consent, reaching the target with 95% probability from open enrollment takes about **409 enrollments** at a 20% consent rate. With a hazard of 0.30, it takes 142 randomized learners or about 737 enrollments. These figures assume that consent and completion are independent across learners.
3. **Power depends on assistant use.** With full use, the within-learner design in the moderate scenario has power 1.00 for d = 0.5, 0.80–0.91 for d = 0.3 and 0.47–0.59 for d = 0.2. At 70% uptake the intention-to-treat effect shrinks to about 0.7 d, and power for d = 0.3 falls to 0.52–0.62 (random non-use) or 0.45–0.58 (non-use that depends on prior knowledge, policy and difficulty). At 50% uptake it falls to 0.26–0.39. **Assistant uptake is therefore as important for the study as recruitment.**
4. **Bounded scores.** A latent effect of d = 0.3 corresponds to about 0.46 points on the 0–6 score (0.28 score SD). Power on the observed score is close to the continuous case (moderate: 0.77–0.88), and coverage of the score-scale target is about 94–96%.
5. **The by-learner design** needs roughly four times as many learners for the same precision.
6. **Carryover** of 0.15 SD shifts the assignment-based contrast by about 0.02–0.03 relative to the immediate effect (persistent and decaying carryover lower it, negative carryover raises it), with coverage of 92–95%. This is why the estimand is defined as assignment-based rather than history-free.
7. **Policy-dependent dropout**, with or without an ability link, leaves estimates unbiased in this model but reduces the number of learners completing four or more activities, costing up to about 11 points of power.
8. **H3m.** For an interaction of 0.25 SD per SD of prior knowledge, power is 0.42–0.54 (conservative), 0.63–0.76 (moderate) and 0.79–0.90 (optimistic). The size 0.25 is a planning assumption.

## Estimand and missing data

The estimand is the assignment-based contrast under the balanced sequence design, which can include effects of earlier assignments (carryover). With bounded scores, the target is the average change in observed score if every completed activity were learned under guided inquiry. With incomplete uptake, it is the intention-to-treat effect.

The analysis retains all available outcomes from randomized learners, but the within-learner contrast is informed by learners observed under both policies. A learner who completes only one activity has a zero row after within-learner centring and contributes nothing to any fitted coefficient. In the moderate scenario (66 randomized, hazard 0.15), on average about 10 learners complete only one activity, about 52 are observed under both policies, and about 40 complete four or more activities. Outcomes missing after dropout require a missing-at-random assumption, explored through sensitivity analyses. The analysis is therefore an available-case fixed-effects analysis, not a fully observed intention-to-treat analysis.

## Limitations

- Activity effects and the learner effect are additive and normal, and the bounded-score analysis covers only one threshold pattern.
- Dropout depends on policy and ability, not on unobserved outcomes. Outcome-dependent dropout can bias estimates in ways this simulation does not show.
- Non-use mechanisms are illustrative. Real help-seeking will be measured in the pilot, and the simulation re-run with those estimates.
- These figures are planning assumptions, not forecasts of the eventual sample.

## Licence

MIT. See `LICENSE`.
