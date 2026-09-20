# # web.routes.post.py
# from web.routes import posts
# from web.routes import admin
# from web.routes import db_entry
# from web.routes import review
# from web.routes import review_building

# ROUTES = {
#     "/mark": posts.mark,
#     "/toggle-selected": posts.toggle_selected,
#     "/delete-post": posts.delete_post,
#     "/add-alias": admin.add_alias,
#     "/add-blacklist": admin.add_blacklist,
#     "/delete-blacklist": admin.delete_blacklist,
#     "/add-filter": admin.add_filter,
#     "/delete-filter": admin.delete_filter,
#     "/db-entry": db_entry.enter,
#     "/db-entry-building": db_entry.enter_building,
#     "/review-action": review.action,
#     "/assign-building": review_building.assign,
#     "/dismiss-building": review_building.dismiss,
# }


# def routes(request):
#     handler = ROUTES.get(request["path"])

#     if handler is None:
#         return (
#             "404 Not Found",
#             [("Content-Type", "text/plain")],
#             b"Not Found",
#         )

#     return handler(request)
