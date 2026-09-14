# db.db_supabase.py
import os
from uuid import uuid4
from contextlib import asynccontextmanager
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv

load_dotenv()

ASYNC_DB_URL = os.environ["ASYNC_DB_URL"]

engine = create_async_engine(ASYNC_DB_URL)

# ASYNC_DB_URL = (
#     "postgresql+asyncpg://proppro_app.przrtyroapjuanzmgfme:"
#     "TM54-46jo56709@aws-1-ap-northeast-2.pooler.supabase.com:6543/postgres"
# )

ORG_ID = "2b954e6c-4663-461a-b6b5-e2bf1cae7203"

# engine = create_async_engine(
#     ASYNC_DB_URL + "?prepared_statement_cache_size=0",
#     poolclass=NullPool,
#     connect_args={
#         "statement_cache_size": 0,
#         "prepared_statement_name_func": lambda: f"__asyncpg_{uuid4()}__",
#     },
# )

SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


@asynccontextmanager
async def get_session():
    async with SessionLocal() as session:
        await session.execute(
            text("SELECT set_config('app.current_org_id', :org_id, false)"),
            {"org_id": ORG_ID},
        )
        try:
            yield session
        finally:
            pass
