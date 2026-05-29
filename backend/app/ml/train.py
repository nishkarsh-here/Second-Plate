"""Train the surplus forecaster.

A GradientBoostingRegressor predicts next-day servings per donor from calendar,
lag and rolling features. The split is *temporal* (earliest 80% train, latest
20% test) — the honest setup for a forecasting task — and we report MAE / RMSE
/ R2 on the held-out tail.
"""
from __future__ import annotations

from datetime import datetime, timezone

import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sqlalchemy.orm import Session

from app.core.config import settings
from app.ml import model_store
from app.ml.features import FEATURES, build_training_matrix
from app.schemas.prediction import RetrainMetrics


def train(db: Session) -> RetrainMetrics:
    frame = build_training_matrix(db)
    if frame.empty or len(frame) < 100:
        raise ValueError(
            "Not enough donation history to train. Seed the database first "
            "(python -m app.seed.seed)."
        )

    frame = frame.sort_values("date").reset_index(drop=True)
    split = int(len(frame) * 0.8)
    train_df, test_df = frame.iloc[:split], frame.iloc[split:]

    x_train, y_train = train_df[FEATURES], train_df["servings"]
    x_test, y_test = test_df[FEATURES], test_df["servings"]

    model = GradientBoostingRegressor(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=3,
        subsample=0.9,
        random_state=settings.seed_random_state,
    )
    model.fit(x_train, y_train)

    pred = model.predict(x_test)
    mae = float(mean_absolute_error(y_test, pred))
    rmse = float(np.sqrt(mean_squared_error(y_test, pred)))
    r2 = float(r2_score(y_test, pred))

    importances = {f: float(i) for f, i in zip(FEATURES, model.feature_importances_)}
    # Training means power the per-donor ablation explanations at predict time.
    feature_means = {f: float(x_train[f].mean()) for f in FEATURES}
    trained_at = datetime.now(timezone.utc)

    meta = {
        "model_version": model_store.MODEL_VERSION,
        "trained_at": trained_at.isoformat(),
        "features": FEATURES,
        "feature_importances": importances,
        "feature_means": feature_means,
        "metrics": {
            "mae": round(mae, 2),
            "rmse": round(rmse, 2),
            "r2": round(r2, 3),
            "n_train": len(train_df),
            "n_test": len(test_df),
            "n_features": len(FEATURES),
        },
    }
    model_store.save(model, meta)

    return RetrainMetrics(
        mae=round(mae, 2),
        rmse=round(rmse, 2),
        r2=round(r2, 3),
        n_train=len(train_df),
        n_test=len(test_df),
        n_features=len(FEATURES),
        feature_importances={k: round(v, 4) for k, v in importances.items()},
        trained_at=trained_at,
        model_version=model_store.MODEL_VERSION,
    )


def main() -> None:
    from app.db.session import SessionLocal

    db = SessionLocal()
    try:
        metrics = train(db)
        print("Model trained:")
        print(f"  MAE  : {metrics.mae}")
        print(f"  RMSE : {metrics.rmse}")
        print(f"  R^2  : {metrics.r2}")
        print(f"  train/test rows: {metrics.n_train}/{metrics.n_test}")
        print("  top features:")
        ranked = sorted(metrics.feature_importances.items(), key=lambda kv: kv[1], reverse=True)
        for name, imp in ranked[:6]:
            print(f"    {name:<14} {imp:.3f}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
