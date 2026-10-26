import os
os.environ["TESTING"] = "1"
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.main import app
from app.core.database import Base, get_db

# SYNTHETIC TEST FIXTURE (Isolated in-memory database per G2 & G3)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,
)
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


from app.core.config import settings


@pytest.fixture(autouse=True)
async def setup_database():
    """Create all tables before each test and drop them after."""
    orig_mode = settings.ACCESS_MODE
    settings.ACCESS_MODE = "multi_user"
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    settings.ACCESS_MODE = orig_mode
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db():
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
async def client():
    """Async test client with ASGI transport."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", headers={"X-Test-Echo-Token": "1"}) as ac:
        yield ac
