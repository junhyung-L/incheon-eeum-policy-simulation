# Incheon e-Eum Cashback Policy Simulation

[한국어](README.ko.md) · [Case study](PORTFOLIO.md)

Forecasts daily e-Eum card spending per Incheon district and compares
cashback schedules under a fixed budget. (e-Eum is Incheon's local-currency
payment card; cashback is the city's spending incentive.)

**Problem.** If a KRW 200 billion budget allows a higher cashback rate in only
two months of 2024, which two months buy the most consumption per won of
cashback?

**Result.** Compares all C(12,2) = 66 two-month combinations. Every one of the
top five includes April, June, or September; April + June ranks first with an
ROI index (predicted spending growth relative to cashback paid, scaled by the
share of budget remaining) of 76.433, against 73.293 for fifth place.

**Scope.** A shortlist of candidate months, not a measured policy effect; the
top-five spread (about 4%) is below every segment's forecast error (MAPE 8.1%
to 66.2%). Training data not included; `python run_pipeline.py --help` shows
the baseline CatBoost CLI, not the ROI simulation.

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
CatBoost), not the LightGBM models or ROI simulation above. Each district's
days are split in time order: the last 20% is scored (RMSE, MAPE) and is not
used for training or early stopping; the last 10% of the remaining training
period is the early-stopping set, and the model fits on the rest. Unlike the
Figure 2 exploration, its scores are therefore not tuned on the scoring window.

```powershell
pip install -r requirements.txt

python scripts/smoke_test.py   # synthetic two-district run, checks the split

python run_pipeline.py `
  --input-csv data\merged.csv `
  --region-col "<region column>" `
  --date-col "<date column>" `
  --target-col "<spending target column>"
```

Writes features, per-district metrics (row counts per split, best iteration,
RMSE, MAPE), and models to `results/`; `--help` lists all options. The smoke
test needs no data and falls back to a recording stand-in when catboost is not
installed. The notebooks ran on Google Colab (Python 3.11: `02`, `03`,
`99_draft_2`) and a local Python 3.12.4 environment (`01`, `04`–`08`).
`requirements.txt` pins numpy, scipy, and scikit-learn to the versions the
`03` notebook records; pandas is pinned to the 2026-11 review environment and
catboost is unpinned, because their original versions were not recorded.

## Repository layout

```text
run_pipeline.py            # CLI entry point
scripts/smoke_test.py      # Synthetic-data check of the CLI training split
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

## License

No open-source license: the code and documents are public for review; reuse requires permission.
