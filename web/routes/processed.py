# web/routes/processed.py
from web.http_helpers import html_response, redirect
import web.processed as processed


def index(request):
    first_id = processed.get_first_processed_id()
    if first_id:
        return redirect(f"/processed/{first_id}")
    return html_response("<h2>No processed posts.</h2>")


def post(request):
    row_id = int(request["path"].split("/processed/")[1])
    p, all_rows = processed.get_post(row_id)
    if not p:
        return redirect("/processed")
    html = processed.build_page(p, all_rows, mode="processed")
    if html is None:
        return redirect("/processed")
    return html_response(html)


def author(request):
    id_part = request["path"][len("/processed/author/") :].split("/")[0]
    if not id_part.isdigit():
        return "404 Not Found", [("Content-Type", "text/plain")], b"Not Found"
    row_id = int(id_part)

    author_name, p, all_rows = processed.get_author_posts_by_row_id(row_id)
    if author_name is None:
        return "404 Not Found", [("Content-Type", "text/plain")], b"Not Found"
    if p is None or not all_rows:
        return html_response(f"<h2>No processed posts for author: {author_name}</h2>")

    html = processed.build_page(p, all_rows, mode="author", author_name=author_name)
    if html is None:
        return redirect("/processed")
    return html_response(html)
