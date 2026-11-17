import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Make "app" importable whether pytest runs from the repo root or from demo-cicd/.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.main import app, articles


@pytest.fixture
def client():
    articles.clear()
    return TestClient(app)
