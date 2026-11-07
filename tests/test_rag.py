import pytest
from emporio_agent.rag.ingest_policy import ingest_policies
from emporio_agent.rag.vector_store import get_vector_store


@pytest.fixture(scope="module", autouse=True)
def setup_vector_store():
    ingest_policies()


def test_qdrant_policy_search_return():
    vs = get_vector_store()
    results = vs.search("Qual o prazo para devolver por arrependimento?", limit=2)
    assert len(results) > 0
    top = results[0]
    assert top["score"] > 0.4
    assert "4.1" in top["section"] or "Direito de Arrependimento" in top["title"]
