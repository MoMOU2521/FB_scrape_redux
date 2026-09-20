# # web/http_helpers.py
# import json
# from http import HTTPStatus
# from db.exceptions import (
#     OwnerConflictError,
#     NoIdentifiableOwnerError,
#     BuildingConflictError,
#     BuildingNotFoundError,
# )


# def run_route(route_fn, request):
#     try:
#         data = parse_json_body(request)
#         status, payload = route_fn(data)
#         return json_response(status, payload)

#     except (
#         OwnerConflictError,
#         NoIdentifiableOwnerError,
#         BuildingConflictError,
#         BuildingNotFoundError,
#     ) as e:
#         return json_response(409, {"error": str(e)})

#     except Exception as e:
#         print("POST ERROR:", e)
#         return json_response(400, {"error": str(e)})


# def parse_json_body(request):
#     length = int(request["headers"].get("CONTENT_LENGTH", 0))
#     body = request["body"].read(length)
#     return json.loads(body)


# def html_response(html: str):
#     return "200 OK", [("Content-Type", "text/html")], html.encode()


# def json_response(status: int, payload: dict):
#     status_line = f"{status} {HTTPStatus(status).phrase}"
#     return (
#         status_line,
#         [("Content-Type", "application/json")],
#         json.dumps(payload).encode(),
#     )


# def redirect(location: str):
#     return "302 Found", [("Location", location)], b""
