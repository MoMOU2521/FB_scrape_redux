# web.pages.stats.py
import web.queries.stats as queries
from web.templates import STATS_TEMPLATE, AUTHOR_LIST_TEMPLATE


def build_stats_page():
    rows = queries.get_group_stats()
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
    rows = queries.get_authors_by_unprocessed_count(min_count=2)

    if not rows:
        rows_html = '<tr><td colspan="4" class="empty-msg">No authors with more than 1 unprocessed post.</td></tr>'
    else:
        rows_html = ""
        for idx, (author, count, row_id) in enumerate(rows, 1):
            rows_html += f"""
            <tr>
                <td>{idx}</td>
                <td>{author}</td>
                <td><span class="count-badge">{count}</span></td>
                <td><a href="/author/{row_id}" class="author-link">View posts →</a></td>
            </tr>
            """

    return AUTHOR_LIST_TEMPLATE % {"rows": rows_html}
