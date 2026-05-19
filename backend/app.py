from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.ask import router as ask_router
from services.db_service import init_db
from services.vector_service import vector_service
from services.rag import rag_service
from utils.logger import get_logger

logger = get_logger("backend.app")

app = FastAPI(
    title="AI Shopping Copilot",
    description="FastAPI backend for an AI-powered shopping assistant.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting AI Shopping Copilot backend...")
    await init_db()
    await vector_service.initialize()
    await rag_service.initialize()
    logger.info("Startup complete.")

app.include_router(ask_router, prefix="/api")
