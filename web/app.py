#  web.app.py
from web.routes import routes


def app(environ, start_response):
    request = {
        "method": environ["REQUEST_METHOD"],
        "path": environ.get("PATH_INFO", ""),
        "query": environ.get("QUERY_STRING", ""),
        "headers": environ,
        "body": environ["wsgi.input"],
    }

    response = routes(request)

    status, headers, body = response

    start_response(status, headers)
    return [body]
