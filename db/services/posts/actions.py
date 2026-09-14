# db/services/posts/actions.py

from db.database import db


def toggle_selected(row_id: int, selected: int) -> None:
    db.conn.execute(
        "UPDATE posts SET selected = ? WHERE id = ?",
        (selected, row_id),
    )
    db.conn.commit()


def delete_post(row_id: int) -> bool:
    row = db.conn.execute("SELECT id FROM posts WHERE id = ?", (row_id,)).fetchone()
    if not row:
        return False

    db.conn.execute("DELETE FROM posts WHERE id = ?", (row_id,))
    db.conn.commit()
    return True
