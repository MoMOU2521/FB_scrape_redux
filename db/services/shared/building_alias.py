# db.services.shared.building_alias.py
from sqlalchemy import text
from db.db_supabase import get_session


async def get_building_names() -> list[tuple[int, str]]:
    async with get_session() as session:
        result = await session.execute(text("""
            SELECT id, building_name
            FROM building_registry
            ORDER BY
                CASE WHEN building_name ILIKE 'the %%'
                     THEN substr(building_name, 5)
                     ELSE building_name
                END ASC
        """))
        return result.all()


async def add_building_alias(building_id: int, alias: str) -> bool:
    async with get_session() as session:
        try:
            await session.execute(
                text(
                    "INSERT INTO building_alias (building_id, alias) VALUES (:bid, :alias)"
                ),
                {"bid": building_id, "alias": alias},
            )
            await session.commit()
            return True
        except Exception as e:
            await session.rollback()
            print("ADD ALIAS ERROR:", e)
            return False
