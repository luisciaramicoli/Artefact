import pytest
from fastapi.testclient import TestClient
from emporio_agent.api.main import app
from emporio_agent.db.seed import seed_database
from emporio_agent.rag.ingest_policy import ingest_policies


@pytest.fixture(scope="module", autouse=True)
def setup_all():
    seed_database()
    ingest_policies()


client = TestClient(app)


def test_api_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["total_products"] >= 65
    assert data["total_indexed_policies"] >= 10


def test_api_products():
    res = client.get("/api/products?category=Guitarras")
    assert res.status_code == 200
    data = res.json()
    assert data["found"] is True
    assert len(data["products"]) > 0


def test_api_conversations():
    res = client.get("/api/conversations")
    assert res.status_code == 200
    assert isinstance(res.json(), list)
