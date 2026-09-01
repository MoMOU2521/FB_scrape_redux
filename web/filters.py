# web.filters.py
from datetime import datetime, timezone

from db.db_core import core
from web.templates import FILTERS_TEMPLATE

# ============================================================================
# QUERIES
# ============================================================================


def is_phrase_filtered(text: str):
    core.cur.execute("SELECT phrase FROM filter_phrases")
    for (phrase,) in core.cur.fetchall():
        if phrase in text:
            return phrase
    return None


def add_filter_phrase(phrase: str):
    core.cur.execute(
        "INSERT OR IGNORE INTO filter_phrases (phrase, added_at) VALUES (?, ?)",
        (phrase, datetime.now(timezone.utc).isoformat()),
    )
    core.conn.commit()


def filter_phrase_exists(phrase: str) -> bool:
    row = core.cur.execute(
        "SELECT 1 FROM filter_phrases WHERE phrase = ?", (phrase,)
    ).fetchone()
    return row is not None


def delete_filter_phrase(phrase: str):
    core.cur.execute("DELETE FROM filter_phrases WHERE phrase = ?", (phrase,))
    core.conn.commit()


def get_filter_rows():
    return core.cur.execute(
        "SELECT phrase, added_at FROM filter_phrases ORDER BY added_at DESC"
    ).fetchall()


# ============================================================================
# PAGE ASSEMBLY
# ============================================================================


def build_filters_page():
    rows = get_filter_rows()

    if not rows:
        rows_html = '<tr><td colspan="3" class="empty-msg">No filter phrases.</td></tr>'
    else:
        rows_html = ""
        for phrase, added_at in rows:
            escaped_phrase = phrase.replace("'", "\\'").replace('"', '\\"')
            rows_html += f"""
            <tr>
                <td>{phrase}</td>
                <td>{added_at or 'N/A'}</td>
                <td><button class="delete-btn" onclick="deleteFilter('{escaped_phrase}')">Delete</button></td>
            </tr>
            """

    return FILTERS_TEMPLATE % {"rows": rows_html}
