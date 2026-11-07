import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from emporio_agent.config import settings
from emporio_agent.db.seed import seed_database
from emporio_agent.rag.ingest_policy import ingest_policies
from emporio_agent.api.routes import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event: auto-seed relational database and index policies if needed on startup."""
    logger.info("Initializing Empório da Música backend...")
    try:
        seed_database()
        ingest_policies()
        logger.info("Database and vector store ready.")
    except Exception as e:
        logger.error(f"Error during startup data initialization: {e}")
    yield
    logger.info("Shutting down Empório da Música backend.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend API with AI Agent (Gemini + Qdrant RAG + SQLite) for Empório da Música.",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list + ["*"],  # Allow localhost dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)


@app.get("/")
def root():
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs_url": "/docs",
        "health_url": "/api/health",
        "description": "Agent API ready. Send POST requests to /api/chat."
    }


def start():
    """Entry point for running with uvicorn via CLI or script."""
    import uvicorn
    uvicorn.run("emporio_agent.api.main:app", host=settings.HOST, port=settings.PORT, reload=True)


if __name__ == "__main__":
    start()
