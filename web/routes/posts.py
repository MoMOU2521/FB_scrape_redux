# web/routes/posts.py
import os
import subprocess
from urllib.parse import unquote

from web.http_helpers import html_response, redirect, run_route
import web.queries.posts as queries
import web.pages.posts as pages
from web.pages.look_up import build_lookup_page
from db.services.posts.actions import (
    toggle_selected as _toggle_selected,
    delete_post as _delete_post,
)


def _attach_images(post):
    post_dir = f"images/{post.get('post_id')}"
    if os.path.isdir(post_dir):
        post["images"] = sorted(
            os.path.join(post_dir, f)
            for f in os.listdir(post_dir)
            if f.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".webp"))
        )
    else:
        post["images"] = []


def _get_post(row_id):
    p = queries.get_post_by_id(row_id)
    if p:
        _attach_images(p)
        p["unprocessed_count"] = queries.count_unprocessed_by_author(p["author"])
    else:
        p = {}
    return p, queries.get_unprocessed_ids()


def _get_author_posts(row_id):
    author = queries.get_author_of_post(row_id)
    if author is None:
        return None, None, []

    all_posts = queries.get_posts_by_author_unprocessed(author)
    if not all_posts:
        return author, None, []

    author_name = all_posts[0]["author"]
    target = next((p for p in all_posts if p["id"] == row_id), all_posts[0])
    _attach_images(target)
    target["unprocessed_count"] = len(all_posts)

    return author_name, target, [(p["id"], p["processed"]) for p in all_posts]


def index(request):
    row_id = queries.get_first_unprocessed_id()
    if row_id:
        return redirect(f"/post/{row_id}")
    return html_response("<h2>All posts processed.</h2>")


def post(request):
    row_id = int(request["path"].split("/post/")[1])
    p, all_rows = _get_post(row_id)
    if not p:
        return redirect("/")
    html = pages.build_page(p, all_rows, mode="fifo")
    if html is None:
        return redirect("/")
    return html_response(html)


def author(request):
    id_part = request["path"][len("/author/") :].split("/")[0]
    if not id_part.isdigit():
        return "404 Not Found", [("Content-Type", "text/plain")], b"Not Found"
    row_id = int(id_part)

    author_name, p, all_rows = _get_author_posts(row_id)
    if author_name is None:
        return "404 Not Found", [("Content-Type", "text/plain")], b"Not Found"
    if p is None or not all_rows:
        return html_response(f"<h2>No unprocessed posts for author: {author_name}</h2>")

    html = pages.build_page(p, all_rows, mode="author", author_name=author_name)
    if html is None:
        return redirect("/")
    return html_response(html)


def lookup(request):
    query = request["query"]
    params = dict(p.split("=", 1) for p in query.split("&") if "=" in p)
    raw_id = unquote(params.get("id", "")).strip()

    if not raw_id:
        return html_response(build_lookup_page())
    if not raw_id.isdigit():
        return html_response(
            build_lookup_page(
                searched_id=raw_id, error="Please enter a valid SQLite row ID."
            )
        )

    row_id = int(raw_id)
    p = queries.get_post_for_lookup(row_id)
    if not p:
        return html_response(
            build_lookup_page(
                searched_id=row_id,
                error=f"No scraped post found with SQLite row ID {row_id}.",
            )
        )

    _attach_images(p)
    return html_response(build_lookup_page(post=p, searched_id=row_id))


def open_folder(request):
    post_id = unquote(request["path"][len("/open-folder/") :])
    folder = os.path.abspath(f"images/{post_id}")
    if os.path.isdir(folder):
        subprocess.Popen(["xdg-open", folder])
    return html_response(
        "<html><body>Opening... <a href='javascript:history.back()'>Go back</a></body></html>"
    )


def image(request):
    filepath = unquote(request["path"].lstrip("/"))
    if os.path.exists(filepath):
        with open(filepath, "rb") as f:
            body = f.read()
        return "200 OK", [("Content-Type", "image/jpeg")], body
    return "404 Not Found", [("Content-Type", "text/plain")], b"Not Found"


def mark(request):
    def _do(data):
        queries.update_processed(int(data["id"]), int(data["processed"]))
        return 200, {"ok": True}

    return run_route(_do, request)


def toggle_selected(request):
    def _do(data):
        _toggle_selected(int(data["id"]), int(data["selected"]))
        return 200, {"ok": True}

    return run_route(_do, request)


def delete_post(request):
    def _do(data):
        return 200, {"ok": _delete_post(int(data["id"]))}

    return run_route(_do, request)
