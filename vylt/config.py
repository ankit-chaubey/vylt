import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CONF = REPO_ROOT / ".vylt.json"

DEFAULT = {
    "threads": 1,
    "seal_meta": False,
    "reuse_data_password_for_meta": True,
    "password_from_env": None,
    "max_password_attempts": 5,
    "benchmark_size_mb": 100
}

class VyltConfig:
    @staticmethod
    def load():
        if not CONF.exists():
            return DEFAULT.copy()
        try:
            cfg = json.loads(CONF.read_text())
            if not isinstance(cfg, dict):
                return DEFAULT.copy()
            out = DEFAULT.copy()
            out.update(cfg)
            return out
        except Exception:
            return DEFAULT.copy()
