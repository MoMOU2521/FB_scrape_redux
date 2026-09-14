#  web.routes.__init__.py
from web.routes import get
from web.routes import post


def routes(request):
    method = request["method"]

    if method == "GET":
        return get.routes(request)

    if method == "POST":
        return post.routes(request)

    return (
        "405 Method Not Allowed",
        [("Content-Type", "text/plain")],
        b"Method Not Allowed",
    )
