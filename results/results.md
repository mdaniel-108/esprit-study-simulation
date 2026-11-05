# ESPRIT simulation results

Values are ranges over the intraclass correlation ρ = 0.3 and 0.5; 2,000 replications per configuration (Monte Carlo error: about ±1 percentage point for a 5% rate, about ±2 for power near 50%). Scenarios are defined by the expected number of learners completing at least four of six activities (A4); with a per-activity dropout hazard of 0.15, this requires N randomized learners, all of whom are analysed. Reported power uses the calibrated method: model-based standard errors for the within-learner design and CR2 cluster-robust standard errors for the by-learner design.

## 1. Calibration: false-positive rate when the true effect is zero (target 5%)

| Scenario | N randomized | Learners with 4+ | Design | CR0, fixed critical values | Model-based | CR2 |
|---|---|---|---|---|---|---|
| Conservative | 41 | 25 | within | 6.2–6.3% | 5.0% | 4.9–5.5% |
| Conservative | 41 | 25 | by_learner | 5.2–5.6% | – | 4.3–5.1% |
| Moderate | 66 | 41 | within | 6.2–6.4% | 5.9% | 5.8–6.3% |
| Moderate | 66 | 40–41 | by_learner | 5.5–6.1% | – | 5.2–5.6% |
| Optimistic | 98 | 60 | within | 4.6–5.4% | 4.3–5.1% | 4.5–5.2% |
| Optimistic | 98 | 60 | by_learner | 4.9–5.5% | – | 4.8–5.4% |

## 2. Main grid: precision and power (dropout hazard 0.15)

| Scenario | N randomized | Learners with 4+ | Design | 95% CI half-width (SD) | Power d = 0.2 | Power d = 0.3 | Power d = 0.5 | Coverage |
|---|---|---|---|---|---|---|---|---|
| Conservative | 41 | 25 | within | 0.23–0.27 | 0.30–0.43 | 0.59–0.75 | 0.95–0.99 | 94.6–95.6% |
| Conservative | 41 | 25 | by_learner | 0.45–0.54 | 0.11–0.15 | 0.20–0.26 | 0.44–0.57 | 93.8–95.6% |
| Moderate | 66 | 40–41 | within | 0.18–0.21 | 0.47–0.59 | 0.80–0.91 | 1.00 | 94.8–95.8% |
| Moderate | 66 | 41 | by_learner | 0.36–0.42 | 0.15–0.19 | 0.28–0.37 | 0.65–0.78 | 94.4–95.5% |
| Optimistic | 98 | 60 | within | 0.14–0.17 | 0.63–0.77 | 0.93–0.98 | 1.00 | 93.7–95.7% |
| Optimistic | 98 | 60 | by_learner | 0.29–0.34 | 0.20–0.26 | 0.40–0.52 | 0.82–0.92 | 94.6–95.7% |

## 3. High attrition (hazard 0.30), moderate scenario

| Design | N randomized | Learners with 4+ | False positives (d = 0) | Power d = 0.3 | Power d = 0.5 |
|---|---|---|---|---|---|
| within | 117 | 40 | 4.8–5.2% | 0.83–0.93 | 1.00 |
| by_learner | 117 | 40 | 5.1–5.9% | 0.43–0.51 | 0.80–0.91 |

## 4. Bounded 0–6 rubric scores (within-learner design)

Effects are generated on the latent scale (d) and analysed on the observed 0–6 score. The target is the average change in score points if every completed activity were learned under guided inquiry; coverage is checked against that target. The standardized target divides it by the SD of scores under explanation-first.

| Scenario | Latent d | Target (score points) | Standardized target | Mean estimate | Coverage of target | Power (d > 0) / false positives (d = 0) |
|---|---|---|---|---|---|---|
| Conservative | 0.0 | 0.00 | 0.00 | -0.01–-0.00 | 95.2–95.3% | 4.7–4.9% |
| Conservative | 0.3 | 0.46 | 0.28 | 0.46 | 94.5–95.2% | 0.56–0.69 |
| Conservative | 0.5 | 0.76 | 0.47 | 0.76 | 95.4% | 0.94–0.98 |
| Moderate | 0.0 | 0.00 | 0.00 | -0.00 | 94.2–95.1% | 4.9–5.8% |
| Moderate | 0.3 | 0.46 | 0.28 | 0.46 | 94.8–95.9% | 0.77–0.88 |
| Moderate | 0.5 | 0.76 | 0.47 | 0.75–0.76 | 94.2–94.8% | 0.99–1.00 |
| Optimistic | 0.0 | 0.00 | 0.00 | 0.00–-0.00 | 93.8–94.9% | 5.1–6.2% |
| Optimistic | 0.3 | 0.46 | 0.28 | 0.46 | 94.4–95.3% | 0.91–0.97 |
| Optimistic | 0.5 | 0.76 | 0.47 | 0.75 | 95.1–95.3% | 1.00 |

## 5. Carryover forms (within-learner design, true immediate effect d = 0.3, carryover 0.15 SD)

| Scenario | Carryover form | Mean estimate | Coverage of 0.3 | Power |
|---|---|---|---|---|
| Moderate | persistent | 0.28 | 94.8–95.3% | 0.73–0.88 |
| Moderate | decaying | 0.27 | 93.5–94.4% | 0.70–0.84 |
| Moderate | negative | 0.32 | 94.1–95.2% | 0.85–0.93 |
| Optimistic | persistent | 0.28 | 93.2–95.1% | 0.89–0.96 |
| Optimistic | decaying | 0.27 | 92.3–94.1% | 0.87–0.95 |
| Optimistic | negative | 0.32 | 93.9–94.6% | 0.95–0.99 |

## 6. Assistant uptake below 100% (within-learner design)

d is the effect when the assistant is used. The intention-to-treat (ITT) target is d times the share of guided-inquiry activities on which the assistant is used. In the dependent variant, help-seeking is lower for learners with above-average prior knowledge, under guided inquiry and on easier activities, with the same 70% average uptake.

| Scenario | Uptake | d | ITT target | Mean estimate | Coverage of target | Power |
|---|---|---|---|---|---|---|
| Conservative | 100% | 0.2 | 0.20 | 0.20 | 94.8–95.6% | 0.30–0.43 |
| Conservative | 100% | 0.3 | 0.30 | 0.30 | 95.1–95.2% | 0.59–0.75 |
| Conservative | 100% | 0.5 | 0.50 | 0.50 | 94.6–95.0% | 0.95–0.99 |
| Conservative | 90% | 0.2 | 0.18 | 0.18 | 94.8–95.0% | 0.26–0.33 |
| Conservative | 90% | 0.3 | 0.27 | 0.27 | 94.8–95.2% | 0.51–0.63 |
| Conservative | 90% | 0.5 | 0.45 | 0.45 | 95.0–95.1% | 0.90–0.96 |
| Conservative | 70% | 0.2 | 0.14 | 0.14 | 94.3–95.8% | 0.18–0.23 |
| Conservative | 70% | 0.3 | 0.21 | 0.21 | 94.6–95.3% | 0.36–0.45 |
| Conservative | 70% | 0.5 | 0.35 | 0.35 | 94.4–95.2% | 0.72–0.84 |
| Conservative | 50% | 0.2 | 0.10 | 0.10 | 95.9–96.2% | 0.09–0.13 |
| Conservative | 50% | 0.3 | 0.15 | 0.15 | 95.3–95.9% | 0.19–0.26 |
| Conservative | 50% | 0.5 | 0.25 | 0.25 | 95.3–95.9% | 0.43–0.58 |
| Conservative | 70% (dependent) | 0.2 | 0.13 | 0.13 | 95.3% | 0.16–0.19 |
| Conservative | 70% (dependent) | 0.3 | 0.20 | 0.19–0.20 | 95.0–95.8% | 0.29–0.39 |
| Conservative | 70% (dependent) | 0.5 | 0.32–0.33 | 0.32–0.33 | 94.9–95.4% | 0.65–0.78 |
| Moderate | 100% | 0.2 | 0.20 | 0.20 | 94.9–95.1% | 0.47–0.59 |
| Moderate | 100% | 0.3 | 0.30 | 0.30 | 95.0–95.8% | 0.80–0.91 |
| Moderate | 100% | 0.5 | 0.50 | 0.50 | 94.8–95.1% | 1.00 |
| Moderate | 90% | 0.2 | 0.18 | 0.18 | 94.8–95.0% | 0.38–0.51 |
| Moderate | 90% | 0.3 | 0.27 | 0.27 | 95.3–95.4% | 0.71–0.83 |
| Moderate | 90% | 0.5 | 0.45 | 0.45 | 94.3–95.2% | 0.98–1.00 |
| Moderate | 70% | 0.2 | 0.14 | 0.14–0.15 | 95.2–95.5% | 0.27–0.32 |
| Moderate | 70% | 0.3 | 0.21 | 0.21 | 94.4–94.5% | 0.52–0.62 |
| Moderate | 70% | 0.5 | 0.35 | 0.35 | 95.0–95.1% | 0.89–0.97 |
| Moderate | 50% | 0.2 | 0.10 | 0.10 | 94.8–95.7% | 0.16–0.19 |
| Moderate | 50% | 0.3 | 0.15 | 0.14–0.15 | 94.8–95.9% | 0.26–0.39 |
| Moderate | 50% | 0.5 | 0.25 | 0.25 | 94.2–95.5% | 0.63–0.76 |
| Moderate | 70% (dependent) | 0.2 | 0.13 | 0.13 | 94.6–94.7% | 0.24–0.30 |
| Moderate | 70% (dependent) | 0.3 | 0.19–0.20 | 0.19 | 94.1–94.9% | 0.45–0.58 |
| Moderate | 70% (dependent) | 0.5 | 0.33 | 0.33 | 94.6–95.6% | 0.86–0.94 |
| Optimistic | 100% | 0.2 | 0.20 | 0.20 | 95.0–95.7% | 0.63–0.77 |
| Optimistic | 100% | 0.3 | 0.30 | 0.30 | 93.7–94.7% | 0.93–0.98 |
| Optimistic | 100% | 0.5 | 0.50 | 0.50 | 94.0–95.3% | 1.00 |
| Optimistic | 90% | 0.2 | 0.18 | 0.18 | 94.9–96.4% | 0.55–0.68 |
| Optimistic | 90% | 0.3 | 0.27 | 0.27 | 94.5–95.1% | 0.87–0.94 |
| Optimistic | 90% | 0.5 | 0.45 | 0.45 | 94.5–95.2% | 1.00 |
| Optimistic | 70% | 0.2 | 0.14 | 0.14 | 95.0–95.4% | 0.35–0.48 |
| Optimistic | 70% | 0.3 | 0.21 | 0.21 | 94.7–95.9% | 0.66–0.82 |
| Optimistic | 70% | 0.5 | 0.35 | 0.35 | 94.8–94.9% | 0.97–1.00 |
| Optimistic | 50% | 0.2 | 0.10 | 0.10 | 94.0–94.7% | 0.19–0.27 |
| Optimistic | 50% | 0.3 | 0.15 | 0.15 | 94.9–95.1% | 0.41–0.51 |
| Optimistic | 50% | 0.5 | 0.25 | 0.25 | 94.8–95.2% | 0.81–0.92 |
| Optimistic | 70% (dependent) | 0.2 | 0.13 | 0.13 | 95.2–95.5% | 0.32–0.41 |
| Optimistic | 70% (dependent) | 0.3 | 0.19–0.20 | 0.19–0.20 | 95.3–95.6% | 0.59–0.73 |
| Optimistic | 70% (dependent) | 0.5 | 0.33 | 0.32–0.33 | 94.4–94.5% | 0.95–0.99 |

## 7. Policy-dependent dropout (within-learner design, d = 0.3)

Hazard rises by 0.10 after guided-inquiry activities; in the ability-related variant, by 0.20 for below-average learners.

| Scenario | Ability-related | Learners with 4+ | Mean estimate | Coverage of 0.3 | Power |
|---|---|---|---|---|---|
| Moderate | no | 34 | 0.30 | 94.9–95.4% | 0.73–0.85 |
| Moderate | yes | 31 | 0.30 | 95.0–95.6% | 0.69–0.83 |
| Optimistic | no | 50 | 0.30 | 94.1–95.7% | 0.89–0.96 |
| Optimistic | yes | 45–46 | 0.30 | 94.0–95.3% | 0.85–0.95 |

## 8. H3m: policy × prior-knowledge interaction (within-learner design)

| Scenario | False positives (g = 0) | Power for g = 0.25 SD per SD |
|---|---|---|
| Conservative | 4.8–5.9% | 0.42–0.54 |
| Moderate | 5.0% | 0.63–0.76 |
| Optimistic | 4.7–5.2% | 0.79–0.90 |

## 9. Recruitment: randomized learners needed to reach the completer target

Each randomized learner completes four or more activities with probability (1 − h)³. The expected-value N gives the target on average; the other columns give the N needed to reach it with 80% or 95% probability (binomial model). Enrollment columns include uncertainty in consent: each enrollee consents with probability 0.20, independently of completion, so the target is reached with the stated probability from that many enrollments.

| Completers with 4+ | Hazard h | N randomized (expected) | P(reach target) at that N | N randomized for 80% | N randomized for 95% | Enrollments for 80% at 20% consent | Enrollments for 95% at 20% consent |
|---|---|---|---|---|---|---|---|
| 25 | 0.15 | 41 | 59% | 45 | 50 | 235 | 270 |
| 40 | 0.15 | 66 | 61% | 70 | 76 | 365 | 409 |
| 60 | 0.15 | 98 | 56% | 104 | 111 | 537 | 590 |
| 40 | 0.3 | 117 | 54% | 129 | 142 | 656 | 737 |
