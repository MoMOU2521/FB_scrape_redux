# web.stats.py
from db.db_core import core
from web.templates import STATS_TEMPLATE, AUTHOR_LIST_TEMPLATE
from web.posts import get_first_unprocessed_id_for_author

# ============================================================================
# QUERIES
# ============================================================================


def get_group_stats():
    rows = core.cur.execute("""
        SELECT
            group_name,
            COUNT(*) as total,
            SUM(selected) as selected
        FROM posts
        WHERE group_name IS NOT NULL
        GROUP BY group_name
        ORDER BY group_name
    """).fetchall()
    return rows


def get_authors_by_unprocessed_count(min_count=2):
    core.cur.execute(
        """
        SELECT
            author,
            COUNT(*) as unprocessed_count
        FROM posts
        WHERE (processed = 0 OR processed IS NULL)
        GROUP BY author
        HAVING COUNT(*) > ?
        ORDER BY unprocessed_count DESC
    """,
        (min_count,),
    )
    return core.cur.fetchall()


def get_next_unprocessed_ai():
    row = core.cur.execute("""
        SELECT id, author, group_name, timestamp, post_url, text
        FROM posts
        WHERE ai_processed = 0 OR ai_processed IS NULL
        ORDER BY id LIMIT 1
        """).fetchone()
    return dict(row) if row else None


def mark_ai_processed(row_id: int):
    core.cur.execute("UPDATE posts SET ai_processed = 1 WHERE id = ?", (row_id,))
    core.conn.commit()


# ============================================================================
# PAGE ASSEMBLY
# ============================================================================


def build_stats_page():
    rows = get_group_stats()
    total_posts = 0
    total_selected = 0
    row_html = ""

    for group_name, total, selected in rows:
        if total is None:
            continue
        selected = selected or 0
        rate = (selected / total * 100) if total > 0 else 0
        total_posts += total
        total_selected += selected
        row_html += f"""
        <tr>
            <td>{group_name}</td>
            <td>{total}</td>
            <td>{selected}</td>
            <td>{rate:.1f}%</td>
        </tr>
        """

    total_rate = (total_selected / total_posts * 100) if total_posts > 0 else 0

    return STATS_TEMPLATE % {
        "rows": row_html,
        "total_posts": total_posts,
        "total_selected": total_selected,
        "total_rate": f"{total_rate:.1f}",
    }


def build_authors_page():
    rows = get_authors_by_unprocessed_count(min_count=2)

    if not rows:
        rows_html = '<tr><td colspan="4" class="empty-msg">No authors with more than 1 unprocessed post.</td></tr>'
    else:
        rows_html = ""
        for idx, (author, count) in enumerate(rows, 1):
            row_id = get_first_unprocessed_id_for_author(author)
            if row_id:
                rows_html += f"""
                <tr>
                    <td>{idx}</td>
                    <td>{author}</td>
                    <td><span class="count-badge">{count}</span></td>
                    <td><a href="/author/{row_id}" class="author-link">View posts →</a></td>
                </tr>
                """

    return AUTHOR_LIST_TEMPLATE % {"rows": rows_html}
