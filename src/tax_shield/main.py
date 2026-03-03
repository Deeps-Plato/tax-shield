import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from tax_shield.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Auto-seed on first start if DB is empty
    from sqlalchemy import select

    from tax_shield.database import async_session
    from tax_shield.models.db_models import Category
    from tax_shield.services.seed_service import seed_all

    async with async_session() as db:
        result = await db.execute(select(Category).limit(1))
        if not result.scalar_one_or_none():
            try:
                counts = await seed_all(db)
                print(f"Auto-seeded: {counts}")
            except Exception as e:
                print(f"Auto-seed failed (run 'alembic upgrade head' first): {e}")

    yield


app = FastAPI(
    title="Tax Shield",
    description="Private tax deduction cross-reference and form generation tool",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
origins = [o.strip() for o in settings.CORS_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
from tax_shield.routes import (  # noqa: E402
    admin,
    analysis,
    auth,
    categories,
    items,
    plaid,
    search,
    strategies,
    tax_forms,
    tax_records,
    transactions,
    user_items,
)

app.include_router(auth.router)
app.include_router(items.router)
app.include_router(categories.router)
app.include_router(strategies.router)
app.include_router(search.router)
app.include_router(user_items.router)
app.include_router(transactions.router)
app.include_router(analysis.router)
app.include_router(tax_records.router)
app.include_router(tax_forms.router)
app.include_router(plaid.router)
app.include_router(admin.router)


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok", "version": "0.1.0"}


# Static files (frontend) — must be last, catches all non-API routes
static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "static")
if os.path.isdir(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
