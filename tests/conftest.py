"""Ensure working directory is repo root so data/ paths resolve in tests."""
import os
import pytest


@pytest.fixture(autouse=True)
def set_repo_root(monkeypatch):
    repo_root = os.path.join(os.path.dirname(__file__), "..")
    monkeypatch.chdir(os.path.abspath(repo_root))
