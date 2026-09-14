# enter_all.py
import asyncio

from ai.config import TRANSLITERATE_MODEL
from ai.groq_ai_client import GroqAIClient

from db.database import LocalDatabase
from db.services.db_entry.process_single_row import process_single_row


async def main():
    db = LocalDatabase("posts.db")

    try:
        # Fetch all unprocessed posts with extraction data
        rows = db.cur.execute("""
            SELECT id,
                   author,
                   post_url,
                   text,
                   scraped_at,
                   extraction_result_json
            FROM posts
            WHERE processed = 0
              AND extraction_result_json IS NOT NULL
              AND extraction_result_json != ''
            ORDER BY id
            """).fetchall()

        if not rows:
            print("No posts to process.")
            return

        # AI only needed for building resolution fallback
        transliterate_ai = GroqAIClient(model=TRANSLITERATE_MODEL)

        success = 0
        failed = 0

        for row in rows:
            print(f"\n========Processing ID: {row['id']}========")

            result = await process_single_row(
                row,
                transliterate_ai,
                db,
            )

            if result:
                success += 1
            else:
                failed += 1

        print(f"\nDone. success={success} failed={failed}")

    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
