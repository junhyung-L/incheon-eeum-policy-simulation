# Incheon e-Eum Cashback Policy Simulation: Comparing 66 Budget-Constrained Policies

[English](PORTFOLIO.md) | [한국어](PORTFOLIO.ko.md) · [README](README.md)

## Summary

Incheon's e-Eum card cashback raises local spending, but the budget keeps
shrinking. Our team forecast daily spending for each of Incheon's 10 districts
and simulated every way of choosing two higher-cashback months under a KRW 200
billion budget: C(12,2) = 66 combinations. In the report, every one of the top
five combinations includes April, June, or September, and April + June ranks
first (ROI index 76.433). The project received the Gold Prize at the 2025
Industry-Academic Capstone Design Competition, Incheon National University
(1 Jul 2025). It is a scenario comparison, not causal policy evidence.

## Challenge

- **Shrinking budget.** After the cashback cut from 10% to 5% in July 2022,
  August spending fell 24.92% month on month. A uniform rate was becoming
  unaffordable, so the question became *when* to spend, not *how much*.
- **Indirect data.** Individual transactions and merchant-level sales were not
  available. The analysis relies on district totals plus demographic, category,
  and macro indicators, as the report itself notes.
- **Uneven districts.** Large districts and rural counties (Ganghwa-gun,
  Ongjin-gun) behave differently, so one average response would mislead.

## My contribution

Four-student team; the final report lists me as team lead. The report does not
record a per-person split of the analysis, so this page describes team
decisions.

## Decisions

**1. One model with a rate feature, or separate models per cashback condition.**
Options: a single model with cashback rate as an input, or one model per
condition. We chose separate LightGBM models for the 10%/5% and 10%/10%
merchant-rate conditions. The report's reasoning: spending responds
differently under different policy conditions, and a single model would average
those responses together. The data also held only a few discrete rate regimes,
so a smooth rate effect could not be learned. The cost
is less training data per model, which shows in the error spread: MAPE ranges
from 8.06% to 66.22% across the 20 district × condition segments, worst for
Ganghwa-gun (66.22%) and Yeonsu-gu (44.26%) under 10%/10%.

**2. Pick the peak-spending months, or enumerate all combinations.**
Options: raise cashback in the months with the highest forecast spending, or
score every two-month pair. We enumerated all 66 because the outcome depends on
interactions. Each month's prediction feeds the next, and every raised month
uses up budget. The cost is that the ranking now depends on the 10%-condition
model being right about months it never saw at that rate.

**3. Rank by spending, or by spending per cashback won.**
Options: total predicted spending, or a return ratio. The report's ROI index
divides predicted spending growth by cashback paid and scales it by the share
of budget left. That fits the budget-holder's question better than gross
spending. The cost is a custom index that is hard to compare with other studies.
It also produces close calls: the top five are within about 4% of each other.

**4. How to validate the forecasts.** The final models were trained on days
before 2024 and scored on 2024 days. A random split would mix future days into
training. An earlier CatBoost exploration (RMSE 173,590,932.20 and MAPE 5.66%
for Bupyeong-gu under 10%/10%) used the same window for early stopping and
scoring, so its score is optimistic. I keep it only as a labelled exploratory
figure.

## Results

| Item | Value | Context |
|---|---|---|
| Combinations simulated | 66 | C(12,2), KRW 200 billion budget, report |
| Top combination | April + June, ROI index 76.433 | Report section 3.7 |
| Fifth combination | June + November, ROI index 73.293 | Report section 3.7 |
| Forecast MAPE | 8.06% to 66.22%; 13 of 20 segments at or below 15% | LightGBM, 2024 holdout, report table |
| Hurst exponent | 0.79 to 0.86 across districts | Notebook `03_feature_engineering` |

The report summarises forecast error as "within 10–15% for most regions". The
table above gives the full spread.

## What the result does not show

- No causal effect: the simulation assumes the 10%-condition model describes a
  counterfactual rate increase. No experiment or quasi-experiment tested that.
- Same-day payment and top-up counts are model inputs, so MAPE describes fit
  given that day's activity, not an advance forecast.
- The top-five gaps are smaller than most segment-level errors. The holiday-
  adjacent and district-differentiated suggestions are hypotheses to test.
- The raw data is not in the repository, so the ROI table is report-stated and
  not regenerated here.

## What I would do next

- Remove same-day activity counts and re-score as a true forecast, with a
  seasonal-naive baseline (same day last year) for comparison.
- Bootstrap the forecast residuals through the simulation to put intervals on
  each combination's ROI, and check whether the top five actually differ.
- Use the 2023 May and September temporary increases as a difference-in-
  differences check of the "raise before a rebound" hypothesis.

## Evidence

- Final report (Korean): `reports/2025년 산학 캡스톤디자인 최종 결과보고서_산경만지회.pdf`
- Notebooks: `notebooks/03_feature_engineering.ipynb` (Hurst),
  `notebooks/99_draft_2.ipynb` (condition models and MAPE table),
  `notebooks/05_prediction.ipynb` (CatBoost exploration)
- [Project review](docs/PROJECT_REVIEW.md)
