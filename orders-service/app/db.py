from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.settings import settings
from sqlalchemy.orm import declarative_base

engine = create_async_engine(settings.DATABASE_URL, echo=True, future=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()

async def get_session() -> AsyncSession:
    async with SessionLocal() as s:
        yield s
