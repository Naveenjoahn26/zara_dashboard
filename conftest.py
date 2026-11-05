"""
conftest.py — Shared pytest fixtures and configuration.
Automatically discovered by pytest in all test modules.
"""
import sys
import os
from pathlib import Path

# ──────────────────────────────────────────────────────
# Make sure the project root is on sys.path so all test
# modules can import backend modules without install.
# ──────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

