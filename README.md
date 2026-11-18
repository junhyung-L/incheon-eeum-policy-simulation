# Incheon e-Eum Cashback Policy Simulation

[한국어](README.ko.md) · [Case study](PORTFOLIO.md)

Forecasts daily e-Eum card spending per Incheon district and compares
cashback schedules under a fixed budget. (e-Eum is Incheon's local-currency
payment card; cashback is the city's spending incentive.)

**Problem.** If a KRW 200 billion budget allows a higher cashback rate in only
two months of 2024, which two months buy the most consumption per won of
cashback?

**Result.** Compares all C(12,2) = 66 two-month combinations. Every one of the
top five includes April, June, or September; April + June ranks first (ROI
index 76.433, against 73.293 for fifth place). It is a shortlist of candidate
months, not a measured policy effect.

**Recognition and role.** Gold Prize, 2025 Industry-Academic Capstone Design
Competition, Incheon National University (1 Jul 2025). Team lead of a
four-person team.

## Data and assumptions

- Daily payment totals for 10 districts, joined with age-band population,
  category spending, CD yield, consumer-sentiment (CSI) indices, cashback
  rates, and top-up/payment counts; 2020–2023 training data (not included).
- A low-pass filter (LPF) separates trend from noise. Hurst exponents of
  0.79–0.86 across districts (notebook `03_feature_engineering`) indicate
  persistent series, supporting lagged trend features.
- Context: after the July 2022 cashback cut from 10% to 5%, August spending
  fell 24.9% month on month.

## Scenario design

1. Trains two LightGBM models per district, one per cashback condition. The
   report calls them the "5%" and "10%" models; in the data these are the
   merchant rate pairs 10%/5% and 10%/10%.
2. For each of the 66 combinations, applies the 10% model to the two raised
   months and the 5% model to the other ten; each month feeds the next.
3. Deducts cashback paid from the KRW 200 billion budget. The ROI index
   compares predicted spending growth with cashback paid, scaled by the share
   of budget remaining.

## Results

Top five combinations:

| Rank | Raised months | ROI index |
|---:|---|---:|
| 1 | April, June | 76.433 |
| 2 | April, September | 76.154 |
| 3 | May, June | 75.817 |
| 4 | June, September | 74.305 |
| 5 | June, November | 73.293 |

Forecast error behind the simulation (LightGBM, trained on days before 2024 and
scored on 2024 days; notebook `99_draft_2`):

| Scope | MAPE |
|---|---|
| 20 district × condition segments | 8.1% to 66.2% |
| Segments at or below 15% | 13 of 20 |
| Largest errors (10%/10% condition) | Ganghwa-gun 66.2%, Yeonsu-gu 44.3% |

The report summarizes this as "within 10–15% for most regions".

![Incheon e-Eum spending, budget, and sign-up trend](images/problem_definition.png)

*Figure 1. Spending, budget, and new sign-ups, 2020–2024.*

![Actual versus predicted daily spending for one exploratory configuration](images/05_20.png)

*Figure 2. Exploratory CatBoost, Bupyeong-gu, 10%/10% condition (notebook
`05_prediction`): RMSE ≈ KRW 174M per day, MAPE 5.7% on the last 20% of the
series. One of 40 exploratory configurations, not the LightGBM models above;
the same window was used for early stopping and scoring, so the score is
optimistic.*

## How to run

The CLI is a baseline pipeline that runs on new data as is (per-district
CatBoost, chronological 80/20 split), not the LightGBM models or ROI
simulation above.

```powershell
pip install -r requirements.txt

python run_pipeline.py `
  --input-csv data\merged.csv `
  --region-col "<region column>" `
  --date-col "<date column>" `
  --target-col "<spending target column>"
```

Writes features, per-district metrics, and models to `results/`; `--help`
lists all options.

## Repository layout

```text
run_pipeline.py            # CLI entry point
src/                       # Preprocessing, features, per-district CatBoost training
notebooks/                 # Original analysis: 03 features/Hurst, 05 and 99_draft_2 models, 06 ROI
reports/                   # Final report and presentation (Korean)
images/                    # Figures exported from notebooks and the report
```

## Limitations

- Not causal: the ranking assumes the 10%-condition model describes a rate increase; the 24.9% drop is a before/after change.
- Features include same-day payment and top-up counts, so MAPE measures fit given that day's activity, not an advance forecast.
- The top five ROI values are within about 4% of each other, smaller than most segment-level forecast errors.
- The merged training data is not included, so the ROI table cannot be regenerated from this repository.

## Links

- [Case study: decisions and trade-offs](PORTFOLIO.md)
- Final report (Korean): `reports/2025년 산학 캡스톤디자인 최종 결과보고서_산경만지회.pdf`
