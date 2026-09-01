# web.blacklist.py
from db.db_core import core, normalize_author
from web.templates import BLACKLIST_TEMPLATE

# ============================================================================
# QUERIES
# ============================================================================


def is_blacklisted(author: str) -> bool:
    author = normalize_author(author)
    row = core.cur.execute(
        "SELECT count FROM blacklist WHERE author = ?", (author,)
    ).fetchone()
    return row is not None


def increment_blacklist(author: str):
    author = normalize_author(author)
    core.cur.execute(
        "INSERT INTO blacklist (author, count) VALUES (?, 1) "
        "ON CONFLICT(author) DO UPDATE SET count = count + 1",
        (author,),
    )
    core.conn.commit()


def add_blacklist(author: str):
    author = normalize_author(author)
    core.cur.execute(
        "INSERT OR IGNORE INTO blacklist (author, count) VALUES (?, 0)",
        (author,),
    )
    inserted = core.cur.rowcount > 0
    core.cur.execute(
        "UPDATE posts SET processed = 1 WHERE author = ? AND (processed = 0 OR processed IS NULL)",
        (author,),
    )
    updated = core.cur.rowcount
    core.conn.commit()
    return inserted, updated


def get_blacklist_counts(authors):
    authors = [normalize_author(a) for a in authors]
    placeholders = ",".join("?" * len(authors))
    rows = core.cur.execute(
        f"SELECT author, count FROM blacklist WHERE author IN ({placeholders})",
        tuple(authors),
    ).fetchall()
    return {author: count for author, count in rows}


def get_blacklist_rows(sort="count"):
    if sort == "alpha":
        query = "SELECT author, count FROM blacklist ORDER BY author"
    else:
        query = "SELECT author, count FROM blacklist ORDER BY count DESC, author"
    return core.cur.execute(query).fetchall()


def delete_blacklist(author: str):
    core.cur.execute("DELETE FROM blacklist WHERE author = ?", (author,))
    core.conn.commit()


# ============================================================================
# PAGE ASSEMBLY
# ============================================================================


def build_blacklist_page(sort="count"):
    rows = get_blacklist_rows(sort)

    if not rows:
        rows_html = (
            '<tr><td colspan="3" class="empty-msg">No blacklisted authors.</td></tr>'
        )
    else:
        rows_html = ""
        for author, count in rows:
            escaped_author = author.replace("'", "\\'").replace('"', '\\"')
            rows_html += f"""
            <tr>
                <td>{author}</td>
                <td>{count}</td>
                <td><button class="delete-btn" onclick="deleteBlacklist('{escaped_author}')">Delete</button></td>
            </tr>
            """

    return BLACKLIST_TEMPLATE % {"rows": rows_html}
