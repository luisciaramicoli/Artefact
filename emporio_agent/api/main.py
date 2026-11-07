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

# Mount frontend build if available
frontend_dist = settings.BASE_DIR / "frontend" / "dist"
if frontend_dist.exists():
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse

    app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="assets")

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        # Don't intercept API routes
        if full_path.startswith("api/"):
            return None
        file_path = frontend_dist / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(frontend_dist / "index.html")
else:
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
