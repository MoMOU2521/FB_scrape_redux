# #  web.server.py
# import json
# from http.server import BaseHTTPRequestHandler
# from urllib.parse import urlparse

# from web.routes import admin
# from web.routes import db_entry
# from web.routes import posts
# from web.routes import processed
# from web.routes import review
# from web.routes import review_building


# class Handler(BaseHTTPRequestHandler):

#     def do_GET(self):
#         path = urlparse(self.path).path

#         if path == "/stats":
#             return admin.stats(self)

#         if path == "/authors":
#             return admin.authors(self)

#         if path == "/blacklist":
#             return admin.blacklist(self)

#         if path == "/filters":
#             return admin.filters(self)

#         if path == "/post-lookup":
#             return posts.lookup(self)

#         if path == "/processed":
#             return processed.index(self)

#         if path.startswith("/processed/author/"):
#             return processed.author(self)

#         if path.startswith("/processed/"):
#             return processed.post(self)

#         if path == "/review-building":
#             return review_building.index(self)

#         if path.startswith("/review-building/"):
#             return review_building.post(self)

#         if path.startswith("/review"):
#             return review.post(self)

#         if path.startswith("/author/"):
#             return posts.author(self)

#         if path.startswith("/post/"):
#             return posts.post(self)

#         if path.startswith("/open-folder/"):
#             return posts.open_folder(self)

#         if path.startswith("/images/"):
#             return posts.image(self)

#         print("UNMATCHED GET:", self.path)
#         return self.send_error(404)

#     def do_POST(self):
#         routes = {
#             "/mark": posts.mark,
#             "/toggle-selected": posts.toggle_selected,
#             "/delete-post": posts.delete_post,
#             "/add-alias": admin.add_alias,
#             "/add-blacklist": admin.add_blacklist,
#             "/delete-blacklist": admin.delete_blacklist,
#             "/add-filter": admin.add_filter,
#             "/delete-filter": admin.delete_filter,
#             "/db-entry": db_entry.enter,
#             "/db-entry-building": db_entry.enter_building,
#             "/review-action": review.action,
#             "/assign-building": review_building.assign,
#             "/dismiss-building": review_building.dismiss,
#         }

#         route = routes.get(self.path)

#         if route is None:
#             self.send_error(404)
#             return

#         error_status_override = self.path in {
#             "/db-entry",
#             "/db-entry-building",
#         }

#         self._handle_post(
#             route,
#             error_status_override=error_status_override,
#         )

#     def _handle_post(self, route_fn, error_status_override=False):
#         try:
#             length = int(self.headers.get("Content-Length", 0))
#             body = self.rfile.read(length)
#             data = json.loads(body)

#             status, payload = route_fn(self, data)

#             self._send_json(status, payload)

#         except Exception as e:
#             print("POST ERROR:", e)

#             self._send_json(
#                 500 if error_status_override else 400,
#                 {"error": str(e)},
#             )

#     def _send_html(self, html: str):
#         self.send_response(200)
#         self.send_header("Content-type", "text/html")
#         self.end_headers()

#         try:
#             self.wfile.write(html.encode())
#         except BrokenPipeError:
#             pass

#     def _send_json(self, status: int, payload: dict):
#         self.send_response(status)
#         self.send_header("Content-type", "application/json")
#         self.end_headers()

#         try:
#             self.wfile.write(json.dumps(payload).encode())
#         except BrokenPipeError:
#             pass

#     def _send_redirect(self, location: str):
#         self.send_response(302)
#         self.send_header("Location", location)
#         self.end_headers()

#     def log_message(self, format, *args):
#         pass
