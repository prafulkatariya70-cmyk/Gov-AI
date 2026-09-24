import sys
from pathlib import Path

# Vercel loads this file from the repository root. The application itself
# remains in backend/ so local development and the existing project layout
# stay unchanged.
ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.main import app  # noqa: E402,F401

__all__ = ["app"]
