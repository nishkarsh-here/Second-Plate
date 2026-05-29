"""Serialization + in-process cache for the trained surplus model.

The model (joblib) and its metadata (JSON: features, importances, training
means for explainability, metrics, timestamp) live in ``settings.model_dir``.
Loaded once and cached so request-time prediction never hits disk.
"""
from __future__ import annotations

import json
from pathlib import Path

import joblib

from app.core.config import settings

MODEL_VERSION = "gbr-v1"

_ARTIFACT_DIR = Path(settings.model_dir)
MODEL_PATH = _ARTIFACT_DIR / "surplus_model.joblib"
META_PATH = _ARTIFACT_DIR / "model_meta.json"

_cache: dict = {"model": None, "meta": None, "loaded": False}


def save(model, meta: dict) -> None:
    _ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    META_PATH.write_text(json.dumps(meta, indent=2))
    _cache.update(model=model, meta=meta, loaded=True)


def load(force: bool = False):
    """Return ``(model, meta)``; both ``None`` if nothing has been trained."""
    if _cache["loaded"] and not force:
        return _cache["model"], _cache["meta"]
    if MODEL_PATH.exists() and META_PATH.exists():
        _cache.update(
            model=joblib.load(MODEL_PATH),
            meta=json.loads(META_PATH.read_text()),
            loaded=True,
        )
    else:
        _cache.update(model=None, meta=None, loaded=True)
    return _cache["model"], _cache["meta"]


def is_loaded() -> bool:
    model, _ = load()
    return model is not None


def get_meta() -> dict | None:
    _, meta = load()
    return meta
