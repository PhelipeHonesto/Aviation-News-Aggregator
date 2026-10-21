"""API smoke tests: the app boots on an empty database and core routes respond.

Runs offline. The scheduler is disabled so no sources are polled.
"""
import os
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("SCHEDULER_ENABLED", "false")
os.environ.setdefault(
    "DATABASE_URL", f"sqlite:///{Path(tempfile.mkdtemp()) / 'loudhawk-test.db'}"
)
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient  # noqa: E402

import main  # noqa: E402
from ingest import load_sources  # noqa: E402
from sources_loader import SourcesLoader  # noqa: E402


def client() -> TestClient:
    return TestClient(main.app)


def test_root_reports_active():
    with client() as c:
        r = c.get("/")
    assert r.status_code == 200
    assert r.json()["status"] == "active"


def test_liveness_and_health():
    with client() as c:
        assert c.get("/healthz").json()["status"] == "alive"
        health = c.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "healthy"


def test_source_catalog_and_active_list_load():
    assert len(SourcesLoader().load_from_csv()) == 74
    assert len(load_sources()) == 25


def test_news_on_empty_database():
    with client() as c:
        r = c.get("/news")
    assert r.status_code == 200
