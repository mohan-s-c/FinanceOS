"""Service configuration. Secrets/URLs come from the environment (see infra/.env.example)."""
from __future__ import annotations

import os


class Settings:
    # CORS: the Vite dev server origin(s). Comma-separated.
    cors_origins: list[str]
    # Global kill switch: when true, agents must always escalate (no auto-action).
    suggest_only: bool
    sod_limit: float

    def __init__(self) -> None:
        raw = os.getenv("FINANCEOS_CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174")
        self.cors_origins = [o.strip() for o in raw.split(",") if o.strip()]
        self.suggest_only = os.getenv("FINANCEOS_SUGGEST_ONLY", "true").lower() in {"1", "true", "yes"}
        # Segregation-of-duties: resolving an exception at/above this amount needs Controller.
        self.sod_limit = float(os.getenv("FINANCEOS_SOD_LIMIT", "20000"))


settings = Settings()
