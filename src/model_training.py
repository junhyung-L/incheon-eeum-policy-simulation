"""Chronological, per-region CatBoost training utilities."""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error

from .config import EARLY_STOPPING_FRACTION, RANDOM_SEED, VALIDATION_FRACTION


def _safe_name(value: object) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", str(value)).strip("_") or "region"


def train_and_evaluate_by_region(
    data: pd.DataFrame,
    *,
    region_col: str,
    date_col: str,
    target_col: str,
    output_model_dir: Path | None = None,
) -> pd.DataFrame:
    """Fit one chronological CatBoost holdout model per region and return metrics.

    Each region's rows are sorted by date and split in time order:
    fit (first ~72%) | early stopping (last 10% of the training period, ~8%) |
    validation (last 20%). Early stopping sees only the early-stopping slice, so
    RMSE/MAPE on the validation slice come from rows that neither the fit nor
    early stopping saw.
    """
    try:
        from catboost import CatBoostRegressor, Pool
    except ImportError as exc:
        raise ImportError("Install project dependencies with `pip install -r requirements.txt`.") from exc

    rows: list[dict[str, object]] = []
    excluded = {region_col, date_col, target_col}
    for region, group in data.groupby(region_col, dropna=False):
        group = group.sort_values(date_col).dropna(subset=[target_col]).copy()
        if len(group) < 10 or group[target_col].nunique() <= 1:
            rows.append({"region": region, "status": "skipped_insufficient_data", "rows": len(group)})
            continue
        features = [column for column in group.columns if column not in excluded]
        categorical = group[features].select_dtypes(include=["object", "string", "category"]).columns.tolist()
        split = int(len(group) * (1 - VALIDATION_FRACTION))
        train, valid = group.iloc[:split], group.iloc[split:]
        stop_rows = max(1, int(len(train) * EARLY_STOPPING_FRACTION))
        fit, stop = train.iloc[:-stop_rows], train.iloc[-stop_rows:]
        model = CatBoostRegressor(
            iterations=1000, learning_rate=0.03, depth=6, loss_function="RMSE",
            eval_metric="RMSE", random_seed=RANDOM_SEED, early_stopping_rounds=50, verbose=False,
        )
        model.fit(
            Pool(fit[features], fit[target_col], cat_features=categorical),
            eval_set=Pool(stop[features], stop[target_col], cat_features=categorical),
        )
        prediction = model.predict(valid[features])
        actual = valid[target_col].to_numpy()
        nonzero = actual != 0
        rows.append({
            "region": region, "status": "trained", "rows": len(group), "fit_rows": len(fit),
            "early_stopping_rows": len(stop), "validation_rows": len(valid),
            "best_iteration": model.get_best_iteration(), "rmse": mean_squared_error(actual, prediction) ** 0.5,
            "mape_percent": float(np.mean(np.abs((actual[nonzero] - prediction[nonzero]) / actual[nonzero])) * 100) if nonzero.any() else np.nan,
        })
        if output_model_dir:
            output_model_dir.mkdir(parents=True, exist_ok=True)
            model.save_model(output_model_dir / f"catboost_{_safe_name(region)}.cbm")
    return pd.DataFrame(rows)
