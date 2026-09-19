# server/services/stats.py
import server.queries.stats as queries


def get_group_stats():
    rows = queries.get_group_stats()
    groups = []
    total_posts = 0
    total_selected = 0

    for group_name, total, selected in rows:
        if total is None:
            continue
        selected = selected or 0
        rate = (selected / total * 100) if total > 0 else 0
        total_posts += total
        total_selected += selected
        groups.append(
            {
                "group_name": group_name,
                "total": total,
                "selected": selected,
                "rate": round(rate, 1),
            }
        )

    total_rate = (total_selected / total_posts * 100) if total_posts > 0 else 0

    return {
        "groups": groups,
        "total_posts": total_posts,
        "total_selected": total_selected,
        "total_rate": round(total_rate, 1),
    }


def get_authors_by_unprocessed_count(min_count=2):
    rows = queries.get_authors_by_unprocessed_count(min_count)
    return [
        {"author": author, "count": count, "first_unprocessed_id": row_id}
        for author, count, row_id in rows
    ]
