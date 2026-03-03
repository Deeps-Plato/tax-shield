import asyncio
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from tax_shield.config import settings
from tax_shield.database import get_db
from tax_shield.main import app
from tax_shield.models.db_models import Base
from tax_shield.security import create_access_token, hash_password

# Use a separate test database
TEST_DB_URL = settings.DATABASE_URL.replace("/tax_shield", "/tax_shield_test")

engine = create_async_engine(TEST_DB_URL, echo=False)
test_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    async with test_session() as session:
        yield session


@pytest_asyncio.fixture
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db: AsyncSession) -> dict:
    from tax_shield.models.db_models import User
    import uuid

    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        password_hash=hash_password("testpass123"),
        name="Test User",
        role="user",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = create_access_token(user.id, user.role)
    return {"user": user, "token": token, "headers": {"Authorization": f"Bearer {token}"}}


@pytest_asyncio.fixture
async def admin_user(db: AsyncSession) -> dict:
    from tax_shield.models.db_models import User
    import uuid

    user = User(
        id=uuid.uuid4(),
        email="admin@example.com",
        password_hash=hash_password("adminpass123"),
        name="Admin User",
        role="admin",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = create_access_token(user.id, user.role)
    return {"user": user, "token": token, "headers": {"Authorization": f"Bearer {token}"}}


@pytest_asyncio.fixture
async def sample_category(db: AsyncSession):
    from tax_shield.models.db_models import Category

    cat = Category(name="Home Office", description="Home office deductions", sort_order=1)
    db.add(cat)
    await db.commit()
    await db.refresh(cat)
    return cat


@pytest_asyncio.fixture
async def sample_item(db: AsyncSession, sample_category):
    from tax_shield.models.db_models import Item

    item = Item(
        name="Home Office Deduction (Simplified)",
        description="Deduct $5 per square foot of home office, up to 300 sq ft ($1,500 max)",
        category_id=sample_category.id,
        deduction_type="deduction",
        filing_types=["self_employed", "individual"],
        irs_reference="Publication 587",
        max_amount=1500,
        tax_year=2025,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item
