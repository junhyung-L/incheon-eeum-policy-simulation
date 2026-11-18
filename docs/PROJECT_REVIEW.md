# Project Review

| Area | Assessment | Evidence and caveat |
|---|---:|---|
| Problem framing | 7/10 | The cashback/spending policy question is explicit. |
| Feature engineering | 7/10 | LPF, rolling, lag, seasonality, and cashback-change features are implemented. |
| Modelling | 6/10 | Per-region time-ordered CatBoost validation with early stopping is implemented. |
| Evaluation | 4/10 | The report's LightGBM table (2024 holdout, notebook `99_draft_2`) spans MAPE 8.06% to 66.22% across 20 district × condition segments; an exploratory CatBoost chart shows MAPE 5.66% for one configuration (`images/05_20.png`) but used its scoring window for early stopping. Same-day activity counts are inputs, and there is no naive baseline or counterfactual design. |
| Reproducibility | 3/10 | Modules exist, but paths, dependencies, raw inputs, and an end-to-end runner are incomplete. |

## Priorities

1. Add a schema/fixture and a configuration-driven runner that writes metrics and scenario artifacts.
2. Retain date-based backtests by region and an explicit naive baseline.
3. Separate demand forecasting from causal claims about cashback-policy effects.
