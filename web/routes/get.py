# # web.routes.get.py
# from web.routes import posts
# from web.routes import processed
# from web.routes import review
# from web.routes import review_building
# from web.routes import admin


# def routes(request):
#     path = request["path"]

#     if path == "/stats":
#         return admin.stats(request)

#     if path == "/post-lookup":
#         return posts.lookup(request)

#     if path == "/processed":
#         return processed.index(request)

#     if path.startswith("/processed/author/"):
#         return processed.author(request)

#     if path.startswith("/processed/"):
#         return processed.post(request)

#     if path == "/review-building":
#         return review_building.index(request)

#     if path.startswith("/review-building/"):
#         return review_building.post(request)

#     if path == "/blacklist":
#         return admin.blacklist(request)

#     if path == "/filters":
#         return admin.filters(request)

#     if path == "/authors":
#         return admin.authors(request)

#     if path.startswith("/open-folder/"):
#         return posts.open_folder(request)

#     if path.startswith("/author/"):
#         return posts.author(request)

#     if path.startswith("/post/"):
#         return posts.post(request)

#     if path.startswith("/images/"):
#         return posts.image(request)

#     if path == "/review":
#         return review.index(request)

#     if path.startswith("/review/"):
#         return review.post(request)

#     return posts.index(request)
