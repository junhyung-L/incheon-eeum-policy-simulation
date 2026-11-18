# Incheon e-Eum Cashback Policy Simulation

[한국어](README.ko.md) · [Case study](PORTFOLIO.md)

This project forecasts daily e-Eum card spending for each district of Incheon
and uses those forecasts to compare cashback schedules under a fixed budget.
(e-Eum is Incheon's local-currency payment card; cashback is the city's
spending incentive.)

**Decision question.** If a KRW 200 billion budget allows a higher cashback
rate in only two months of 2024, which two months buy the most consumption per
won of cashback?

**Headline finding.** The simulation scored all C(12,2) = 66 two-month
combinations. Every one of the top five includes April, June, or September.
April + June ranked first (report ROI index 76.433, against 73.293 for fifth
place). These are report-stated simulation outputs. The top five are within
about 4% of each other, and the forecasts behind them have MAPE between 8.06%
and 66.22% depending on district and condition. Treat the ranking as a
shortlist of candidate months, not a measured policy effect.

**Recognition and role.** Gold Prize, 2025 Industry-Academic Capstone Design
Competition, Incheon National University (1 Jul 2025). This was a four-student
team project; the final report lists me as team lead.

## Data and assumptions

- Daily payment totals per district (10 districts), joined with age-band
  population, category spending, CD yield, consumer-sentiment (CSI) indices,
  cashback rates, and top-up/payment counts. The report covers 2020–2023
  training data. Raw data is not included in this repository.
- A low-pass filter (LPF) separates trend from short-term noise. Hurst exponents
  of 0.79–0.86 across districts (notebook `03_feature_engineering`) indicate
  persistent series, which supports using lagged trend features.
- Context for the problem: after the cashback rate was cut from 10% to 5% in
  July 2022, August spending fell 24.92% month on month (report figure). This
  is a descriptive before/after change, not a causal estimate.

## Scenario design

1. Two LightGBM models per district, one per cashback condition. The report
   calls them the "5%" and "10%" models; in the data these are the merchant
   rate pairs 10%/5% and 10%/10%.
2. For each of the 66 combinations, the two raised months use the 10% model
   and the other ten months use the 5% model. Each month's prediction feeds
   the next month.
3. Cashback paid is deducted from the KRW 200 billion budget. The report's ROI
   index compares predicted spending growth with cashback paid, scaled by the
   share of budget remaining.

## Findings

Top five combinations (final report, section 3.7):

| Rank | Raised months | Report ROI index |
|---:|---|---:|
| 1 | April, June | 76.433 |
| 2 | April, September | 76.154 |
| 3 | May, June | 75.817 |
| 4 | June, September | 74.305 |
| 5 | June, November | 73.293 |

Forecast error behind the simulation (LightGBM, trained on days before 2024 and
scored on 2024 days; report table, notebook `99_draft_2`):

| Scope | MAPE |
|---|---|
| 20 district × condition segments | 8.06% to 66.22% |
| Segments at or below 15% | 13 of 20 |
| Largest errors (10%/10% condition) | Ganghwa-gun 66.22%, Yeonsu-gu 44.26% |

The report summarises this as "within 10–15% for most regions". The full table
shows that some districts are much less reliable, so district-level
recommendations there carry more uncertainty.

![Incheon e-Eum spending, budget, and sign-up trend](images/problem_definition.png)

*Figure 1. Spending, budget, and new sign-ups, 2020–2024, from the final
report. The 24.92% drop follows the July 2022 cashback cut. It is a
descriptive change, not a causal estimate.*

![Actual versus predicted daily spending for one exploratory configuration](images/05_20.png)

*Figure 2. Earlier exploratory CatBoost model for Bupyeong-gu under the
10%/10% condition (notebook `05_prediction`): RMSE 173,590,932.20 (KRW per
day) and MAPE 5.66% on the last 20% of that series. The same window was used
for early stopping, so the score is optimistic. This is one of 40 exploratory
configurations, not the report's LightGBM model.*

## What this does not show

- **Not causal.** The models learn from observed spending under past rates.
  The 66-scenario ranking assumes the 10%-condition model describes what would
  happen if the rate were raised. No counterfactual design tests that.
- **Inputs known only after the fact.** The forecasting features include
  same-day payment and top-up counts. MAPE therefore measures fit given that
  day's activity, not a forecast made in advance.
- **Small gaps at the top.** The top five ROI values are within about 4% of
  each other, which is smaller than most segment-level forecast errors.
- **Not reproduced here.** The ROI table comes from the final report. The ROI
  notebooks are retained, but the raw data is not, so the table cannot be
  regenerated from this checkout.

## Run

The maintained CLI is a portable baseline: a per-district CatBoost model on a
chronological 80/20 split. It does not reproduce the report's LightGBM models
or the ROI simulation.

```powershell
pip install -r requirements.txt

python run_pipeline.py `
  --input-csv data\merged.csv `
  --region-col "<region column>" `
  --date-col "<date column>" `
  --target-col "<spending target column>"
```

It writes generated features, per-district metrics, and model files under
`results/`. `python run_pipeline.py --help` lists all options. Without the
merged CSV, only the help output can be checked.

## Repository layout

```text
run_pipeline.py            # Maintained CLI entry point
src/                       # Preprocessing, features, per-district CatBoost training
notebooks/                 # Original analysis: 03 features/Hurst, 05 and 99_draft_2 models, 06 ROI
reports/                   # Final report and presentation (Korean)
images/                    # Figures exported from notebooks and the report
docs/PROJECT_REVIEW.md     # Method review and priorities
```

## Links

- [Case study: decisions and trade-offs](PORTFOLIO.md)
- [Project review](docs/PROJECT_REVIEW.md)
- Final report (Korean): `reports/2025년 산학 캡스톤디자인 최종 결과보고서_산경만지회.pdf`

No licence file is included, so the code is all rights reserved by default.
The report PDFs are team competition documents.
