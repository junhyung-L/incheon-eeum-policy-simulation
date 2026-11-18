# Incheon e-Eum Cashback Policy Simulation: Comparing 66 Budget-Constrained Policies

[English](PORTFOLIO.md) | [한국어](PORTFOLIO.ko.md) · [README](README.md)

## Summary

Incheon's e-Eum card cashback raises local spending, but the budget keeps
shrinking. The team forecast daily spending for each of Incheon's 10 districts
and simulated every way of choosing two higher-cashback months under a KRW 200
billion budget: C(12,2) = 66 combinations. Every one of the top five includes
April, June, or September; April + June ranks first (report ROI index 76.433).
Gold Prize, 2025 Industry-Academic Capstone Design Competition, Incheon
National University (1 Jul 2025). Team lead of four students (final report
cover).

## Challenge

- **Shrinking budget.** After the cashback cut from 10% to 5% in July 2022,
  August spending fell 24.92% month on month. A uniform rate was becoming
  unaffordable, so the question became *when* to spend, not *how much*.
- **Indirect data.** Individual transactions and merchant-level sales were not
  available; the analysis uses district totals plus demographic, category, and
  macro indicators.
- **Uneven districts.** Large districts and rural counties (Ganghwa-gun,
  Ongjin-gun) behave differently, so one average response would mislead.

## Decisions

**1. One model with a rate feature, or separate models per cashback condition.**
Choice: separate LightGBM models for the 10%/5% and 10%/10% merchant-rate
conditions. Why: spending responds differently under each condition, a single
model would average those responses, and the data held only a few discrete
rate regimes, too few to learn a smooth rate effect. Cost: less training data
per model. MAPE ranges from 8.06% to 66.22% across the 20 district × condition
segments, worst for Ganghwa-gun (66.22%) and Yeonsu-gu (44.26%) under 10%/10%.

**2. Pick the peak-spending months, or enumerate all combinations.**
Choice: score all 66 pairs. Why: each month's prediction feeds the next and
every raised month uses up budget, so months interact. Cost: the ranking
depends on the 10%-condition model being right about months it never saw at
that rate.

**3. Rank by spending, or by spending per cashback won.**
Choice: the report's ROI index, which divides predicted spending growth by
cashback paid and scales it by the share of budget left. Why: it answers the
budget-holder's question better than gross spending. Cost: a custom index that
is hard to compare with other studies, and close calls: the top five are
within about 4% of each other.

**4. Validate forecasts chronologically.** The final models train on days
before 2024 and score on 2024 days, so no future days leak into training. An
earlier CatBoost exploration (RMSE 173,590,932.20 and MAPE 5.66% for
Bupyeong-gu under 10%/10%) used the same window for early stopping and
scoring, so it is shown only as a labelled exploratory figure.

## Results

| Item | Value | Context |
|---|---|---|
| Combinations simulated | 66 | C(12,2), KRW 200 billion budget, report |
| Top combination | April + June, ROI index 76.433 | Report section 3.7 |
| Fifth combination | June + November, ROI index 73.293 | Report section 3.7 |
| Forecast MAPE | 8.06% to 66.22%; 13 of 20 segments at or below 15% | LightGBM, 2024 holdout, report table |
| Hurst exponent | 0.79 to 0.86 across districts | Notebook `03_feature_engineering` |

The report summarises forecast error as "within 10–15% for most regions"; the
table gives the full spread.

## Limitations

- Not causal: the simulation assumes the 10%-condition model describes a counterfactual rate increase; no experiment or quasi-experiment tested that.
- Same-day payment and top-up counts are inputs, so MAPE describes fit given that day's activity, not an advance forecast.
- Top-five gaps are smaller than most segment-level errors; the holiday-adjacent and district-differentiated suggestions are hypotheses to test.
- The ROI table is report-stated and not regenerated here; the raw data is not in the repository.

## Next steps

- Remove same-day activity counts and re-score as a true forecast, against a
  seasonal-naive baseline (same day last year).
- Bootstrap forecast residuals through the simulation to put intervals on each
  combination's ROI, and check whether the top five actually differ.
- Use the 2023 May and September temporary increases as a difference-in-
  differences check of the "raise before a rebound" hypothesis.

## Evidence

- Final report (Korean): `reports/2025년 산학 캡스톤디자인 최종 결과보고서_산경만지회.pdf`
- Notebooks: `notebooks/03_feature_engineering.ipynb` (Hurst),
  `notebooks/99_draft_2.ipynb` (condition models and MAPE table),
  `notebooks/05_prediction.ipynb` (CatBoost exploration)
- [Project review](docs/PROJECT_REVIEW.md)
