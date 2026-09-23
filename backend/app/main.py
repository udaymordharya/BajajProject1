import asyncio

from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routes.sheets import router as sheets_router
from app.services.google_sheets import GoogleSheetsService
from app.services.sync_service import SyncService


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    try:
        app.state.sheets = GoogleSheetsService(settings)
        app.state.sync = SyncService(app.state.sheets, settings)
        app.state.sync.task = asyncio.create_task(
            app.state.sync.run()
        )

    except RuntimeError:
        app.state.sheets = None
        app.state.sync = None

    yield

    if app.state.sync:
        app.state.sync.task.cancel()

        try:
            await app.state.sync.task
        except asyncio.CancelledError:
            pass


settings = get_settings()

app = FastAPI(
    title="Google Sheet Sync API",
    version="1.0.0",
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=True,
    allow_methods=["GET", "PUT", "POST", "OPTIONS"],
    allow_headers=["*"],
)


app.include_router(sheets_router)


@app.get("/", tags=["Health"])
async def root():
    return {
        "message": "Google Sheet Sync API is running"
    }


@app.get("/health", tags=["Health"])
async def health():
    return {
        "status": "healthy"
    }