import os
os.environ["TESTING"] = "1"
import pathlib
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.main import app
from app.core.database import Base, get_db

# SYNTHETIC TEST FIXTURE (Hermetic isolated database per QAS-031 & G2/G3)
TEST_DB_FILE = pathlib.Path(__file__).parent / "test_hermetic.db"
TEST_DATABASE_URL = f"sqlite+aiosqlite:///{TEST_DB_FILE.as_posix()}"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


from app.core.config import settings


@pytest.fixture(autouse=True)
async def setup_database():
    """Create all tables before each test and clean them after."""
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
async def db_session():
    """Async database session fixture for direct test setup."""
    async with TestSessionLocal() as session:
        yield session


@pytest.fixture
async def client():
    """Async test client with ASGI transport (no backdoor headers)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


async def get_test_link_token(email: str) -> str:
    """Convenience testing helper for obtaining a single-use magic link token."""
    from app.testing import issue_link
    async with TestSessionLocal() as session:
        return await issue_link(session, email)


async def get_test_session_token(email: str) -> str:
    """Convenience testing helper for obtaining a server-side session token."""
    from app.testing import make_session
    async with TestSessionLocal() as session:
        return await make_session(session, email)


async def get_test_auth_headers(email: str) -> dict:
    """Convenience testing helper for obtaining Authorization headers."""
    tok = await get_test_session_token(email)
    return {"Authorization": f"Bearer {tok}"}
