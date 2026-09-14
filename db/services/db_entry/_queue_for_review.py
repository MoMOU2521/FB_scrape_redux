# db.services.db_entry._queue_for_review.py
from datetime import datetime, timezone

from db.database import LocalDatabase


def _queue_for_review(row, candidate_property_id=None):
    LocalDatabase.cur.execute(
        """
        INSERT INTO entry_review_queue
        (
            post_id,
            candidate_property_id,
            reviewed,
            created_at
        )
        VALUES (?, ?, 0, ?)
        """,
        (
            row["id"],
            candidate_property_id,
            datetime.now(timezone.utc).isoformat(),
        ),
    )
    LocalDatabase.conn.commit()
