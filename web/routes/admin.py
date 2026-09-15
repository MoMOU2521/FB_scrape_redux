# web/routes/admin.py
import asyncio

from web.http_helpers import html_response, run_route
import web.pages.stats as stats_pages
import web.queries.blacklist as blacklist_queries
import web.pages.blacklist as blacklist_pages
import web.queries.filters as filters_queries
import web.pages.filters as filters_pages
from web.building_alias import add_building_alias
from db.helpers import normalize_author


def stats(request):
    return html_response(stats_pages.build_stats_page())


def authors(request):
    return html_response(stats_pages.build_authors_page())


def blacklist(request):
    query = request["query"]
    params = dict(p.split("=", 1) for p in query.split("&") if "=" in p)
    sort = params.get("sort", "count")
    return html_response(blacklist_pages.build_blacklist_page(sort))


def filters(request):
    return html_response(filters_pages.build_filters_page())


def add_alias(request):
    def _do(data):
        building_id = int(data["building_id"])
        alias = data.get("alias", "").strip()
        if not alias:
            raise ValueError("Missing alias")
        ok = asyncio.run(add_building_alias(building_id, alias))
        return (200 if ok else 500), {"ok": ok}

    return run_route(_do, request)


def add_blacklist(request):
    def _do(data):
        author = data.get("author", "").strip()
        if not author:
            raise ValueError("Missing author")
        author = normalize_author(author)
        inserted, updated = blacklist_queries.add_blacklist(author)
        return 200, {"ok": True, "inserted": inserted, "skipped": updated}

    return run_route(_do, request)


def delete_blacklist(request):
    def _do(data):
        author = data.get("author", "").strip()
        if not author:
            raise ValueError("Missing author")
        author = normalize_author(author)
        blacklist_queries.delete_blacklist(author)
        return 200, {"ok": True}

    return run_route(_do, request)


def add_filter(request):
    def _do(data):
        phrase = data.get("phrase", "").strip()
        if not phrase:
            raise ValueError("Missing phrase")
        if filters_queries.filter_phrase_exists(phrase):
            return 200, {"ok": True, "already_exists": True}
        filters_queries.add_filter_phrase(phrase)
        return 200, {"ok": True, "already_exists": False}

    return run_route(_do, request)


def delete_filter(request):
    def _do(data):
        phrase = data.get("phrase", "").strip()
        if not phrase:
            raise ValueError("Missing phrase")
        filters_queries.delete_filter_phrase(phrase)
        return 200, {"ok": True}

    return run_route(_do, request)
