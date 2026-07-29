from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.core.config import settings
from src.core.exceptions import register_exception_handlers
from src.modules.billing.presentation.routes import router as billing_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="ClaimVision_Pay",
    version="1.0.0",
    lifespan=lifespan,
)

register_exception_handlers(app)
app.include_router(billing_router, prefix="/api/v1/pay", tags=["v1 · Pay"])


@app.get("/health")
async def health():
    return {"status": "ok", "service": "ClaimVision_Pay"}
