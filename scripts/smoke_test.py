"""Smoke test for the CLI training path on a tiny synthetic DataFrame (no real data).

Builds two synthetic districts of daily spending, runs the same feature step as
run_pipeline.py, then train_and_evaluate_by_region, and checks the
chronological split: fit rows < early-stopping rows < validation rows in time,
with the validation rows never passed to CatBoost's fit or eval_set.

    python scripts/smoke_test.py

If catboost is not installed, a small recording stand-in replaces it so the
split logic can still be checked; the script says which one ran.
"""

from __future__ import annotations

import sys
import types
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from run_pipeline import add_time_features  # noqa: E402
from src.model_training import train_and_evaluate_by_region  # noqa: E402

FIT_CALLS: list[dict] = []


def install_stub_catboost() -> None:
    """Minimal CatBoost stand-in: predicts the training mean and records what it saw."""

    class Pool:
        def __init__(self, data, label=None, cat_features=None):
            self.data, self.label = data, label

    class CatBoostRegressor:
        def __init__(self, **params):
            self.params = params

        def fit(self, pool, eval_set=None):
            FIT_CALLS.append({"fit_index": pool.data.index, "stop_index": eval_set.data.index})
            self.mean_ = float(np.mean(pool.label))
            return self

        def predict(self, data):
            return np.full(len(data), self.mean_)

        def get_best_iteration(self):
            return 0

        def save_model(self, path):
            Path(path).write_text("stub")

    sys.modules["catboost"] = types.SimpleNamespace(CatBoostRegressor=CatBoostRegressor, Pool=Pool)


def synthetic_data(days: int = 60) -> pd.DataFrame:
    rng = np.random.default_rng(0)
    dates = pd.date_range("2023-01-01", periods=days, freq="D")
    frames = []
    for region, level in (("A-gu", 100.0), ("B-gu", 250.0)):
        trend = level + np.arange(days) * 0.5 + rng.normal(0, 5, days)
        frames.append(pd.DataFrame({"region": region, "date": dates, "spend": trend.round(1)}))
    return pd.concat(frames, ignore_index=True)


def main() -> None:
    try:
        import catboost  # noqa: F401
        backend = "catboost"
    except ImportError:
        install_stub_catboost()
        backend = "stub (catboost not installed)"

    features = add_time_features(synthetic_data(), "region", "date", "spend")
    metrics = train_and_evaluate_by_region(features, region_col="region", date_col="date", target_col="spend")
    print(f"backend: {backend}")
    print(metrics.to_string(index=False))

    assert (metrics["status"] == "trained").all()
    for row in metrics.itertuples():
        assert row.fit_rows + row.early_stopping_rows + row.validation_rows == row.rows
        assert row.early_stopping_rows >= 1 and row.validation_rows >= 1

    if FIT_CALLS:  # stub records the exact rows; check order and disjointness
        for call, (region, group) in zip(FIT_CALLS, features.groupby("region")):
            group = group.sort_values("date")
            fit_dates = group.loc[call["fit_index"], "date"]
            stop_dates = group.loc[call["stop_index"], "date"]
            used = call["fit_index"].union(call["stop_index"])
            valid_dates = group.loc[group.index.difference(used), "date"]
            assert fit_dates.max() < stop_dates.min() < valid_dates.min(), region
        print("split check: fit < early stopping < validation in time; validation unused in fit/eval_set")
    print("smoke test passed")


if __name__ == "__main__":
    main()
