# web/routes/review.py
from web.http_helpers import html_response, redirect, run_route
import web.review as review


def index(request):
    first_id = review.get_first_pending_id()
    if first_id:
        return redirect(f"/review/{first_id}")
    return html_response("<h2>No pending reviews.</h2>")


def post(request):
    review_id = int(request["path"].split("/review/")[1])
    all_ids = review.get_pending_review_ids()
    if review_id not in all_ids:
        return redirect("/review")
    html = review.build_page(review_id, all_ids)
    if html is None:
        return redirect("/review")
    return html_response(html)


def action(request):
    def _do(data):
        review_id = int(data["id"])
        act = data["action"]

        if act == "approve":
            property_id = review.approve(review_id)
            return 200, {"ok": True, "property_id": property_id}
        if act == "reject":
            review.reject(review_id)
            return 200, {"ok": True, "rejected": True}
        if act == "dismiss":
            review.dismiss(review_id)
            return 200, {"ok": True, "dismissed": True}
        raise ValueError(f"unknown action: {act}")

    return run_route(_do, request)
