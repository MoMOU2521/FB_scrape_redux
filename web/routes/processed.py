# # web/routes/processed.py
# from web.http_helpers import html_response, redirect
# import web.queries.processed as queries
# import web.pages.processed as pages


# def index(request):
#     first_id = queries.get_first_processed_id()
#     if first_id:
#         return redirect(f"/processed/{first_id}")
#     return html_response("<h2>No processed posts.</h2>")


# def post(request):
#     row_id = int(request["path"].split("/processed/")[1])
#     p, all_rows = queries.get_post_with_context(row_id)
#     if not p:
#         return redirect("/processed")
#     html = pages.build_page(p, all_rows, mode="processed")
#     if html is None:
#         return redirect("/processed")
#     return html_response(html)


# def author(request):
#     id_part = request["path"][len("/processed/author/") :].split("/")[0]
#     if not id_part.isdigit():
#         return "404 Not Found", [("Content-Type", "text/plain")], b"Not Found"
#     row_id = int(id_part)

#     author_name, p, all_rows = queries.get_author_context(row_id)
#     if author_name is None:
#         return "404 Not Found", [("Content-Type", "text/plain")], b"Not Found"
#     if p is None or not all_rows:
#         return html_response(f"<h2>No processed posts for author: {author_name}</h2>")

#     html = pages.build_page(p, all_rows, mode="author", author_name=author_name)
#     if html is None:
#         return redirect("/processed")
#     return html_response(html)
