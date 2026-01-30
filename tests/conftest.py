from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from fastapi_stellody.app import app


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)
