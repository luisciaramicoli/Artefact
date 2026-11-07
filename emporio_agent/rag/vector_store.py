from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct, ScoredPoint
from emporio_agent.config import settings
from emporio_agent.rag.embeddings import get_embedder


class QdrantVectorStore:
    """Vector database interface backed by Qdrant (embedded or remote)."""

    def __init__(
        self,
        collection_name: Optional[str] = None,
        storage_path: Optional[str] = None,
        url: Optional[str] = None,
    ):
        self.collection_name = collection_name or settings.QDRANT_COLLECTION_NAME
        self.storage_path = storage_path or settings.QDRANT_STORAGE_PATH
        self.url = url or settings.QDRANT_URL

        # Initialize Qdrant client
        if self.url:
            self.client = QdrantClient(url=self.url)
        else:
            self.client = QdrantClient(path=self.storage_path)

        self.embedder = get_embedder()
        self._ensure_collection()

    def _ensure_collection(self):
        """Create the collection if it does not already exist."""
        collections = [c.name for c in self.client.get_collections().collections]
        if self.collection_name not in collections:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.embedder.dimension,
                    distance=Distance.COSINE
                ),
            )

    def upsert_documents(self, documents: List[Dict[str, Any]]):
        """
        Upsert a list of document chunks.
        Each document dict must have:
          - id: int or str
          - text: str
          - metadata: dict
        """
        points = []
        for doc in documents:
            vector = self.embedder.embed_text(doc["text"])
            payload = {
                "text": doc["text"],
                **(doc.get("metadata") or {})
            }
            points.append(
                PointStruct(
                    id=doc["id"],
                    vector=vector,
                    payload=payload
                )
            )

        if points:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )

    def search(
        self,
        query: str,
        limit: int = 4,
        score_threshold: float = 0.3
    ) -> List[Dict[str, Any]]:
        """Perform semantic search for relevant policy documents."""
        query_vector = self.embedder.embed_text(query)
        scored_points: List[ScoredPoint] = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=limit,
            score_threshold=score_threshold,
        ).points

        results = []
        for pt in scored_points:
            results.append({
                "id": pt.id,
                "score": float(pt.score),
                "text": pt.payload.get("text", ""),
                "section": pt.payload.get("section", ""),
                "title": pt.payload.get("title", ""),
                "page": pt.payload.get("page", None),
            })
        return results

    def count(self) -> int:
        """Count total indexed points."""
        return self.client.count(collection_name=self.collection_name).count


# Singleton instance
_vector_store = None


def get_vector_store() -> QdrantVectorStore:
    global _vector_store
    if _vector_store is None:
        _vector_store = QdrantVectorStore()
    return _vector_store
