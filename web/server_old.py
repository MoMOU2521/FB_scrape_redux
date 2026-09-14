# web/server.py
import json
import os
import subprocess
import asyncio
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, unquote
from datetime import datetime, timezone

from db.db_core import core, normalize_author
from web.building_alias import add_building_alias
import web.posts as posts
import web.blacklist as blacklist
import web.filters as filters
import web.stats as stats
import db.db_entry as db_entry
import web.processed as processed
import web.review as review
import web.review_building as review_building


class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        path = urlparse(self.path).path

        if path == "/stats":
            self._send_html(stats.build_stats_page())
            return

        if path == "/post-lookup":
            query = urlparse(self.path).query
            params = dict(p.split("=", 1) for p in query.split("&") if "=" in p)

            raw_id = params.get("id", "").strip()

            if not raw_id:
                from web.templates.post_lookup import render_post_lookup_page

                self._send_html(render_post_lookup_page())
                return

            if not raw_id.isdigit():
                from web.templates.post_lookup import render_post_lookup_page

                self._send_html(
                    render_post_lookup_page(
                        searched_id=raw_id,
                        error="Please enter a valid SQLite row ID.",
                    )
                )
                return

            row_id = int(raw_id)
            post = posts.get_post_for_lookup(row_id)
            from web.templates.post_lookup import render_post_lookup_page

            if not post:
                self._send_html(
                    render_post_lookup_page(
                        searched_id=row_id,
                        error=f"No scraped post found with SQLite row ID {row_id}.",
                    )
                )
                return

            self._send_html(
                render_post_lookup_page(
                    post=post,
                    searched_id=row_id,
                )
            )
            return

        if path == "/processed":
            first_id = processed.get_first_processed_id()

            if first_id:
                self._send_redirect(f"/processed/{first_id}")
            else:
                self._send_html("<h2>No processed posts.</h2>")

            return

        if path == "/review-building":
            first_id = review_building.get_first_pending_building_id()

            if first_id:
                self._send_redirect(f"/review-building/{first_id}")
            else:
                self._send_html("<h2>No pending building reviews.</h2>")

            return

        if path.startswith("/review-building/"):
            try:
                review_id = int(path.split("/review-building/")[1])
            except ValueError:
                self.send_error(404)
                return

            all_ids = review_building.get_pending_building_ids()

            if review_id not in all_ids:
                self._send_redirect("/review-building")
                return

            html = review_building.build_page(
                review_id,
                all_ids,
            )

            if html is None:
                self._send_redirect("/review-building")
                return

            self._send_html(html)
            return

        if path.startswith("/processed/author/"):
            id_part = path[len("/processed/author/") :].split("/")[0]

            if not id_part.isdigit():
                self.send_error(404)
                return

            row_id = int(id_part)

            author_name, post, all_rows = processed.get_author_posts_by_row_id(row_id)

            if author_name is None:
                self.send_error(404)
                return

            if post is None or not all_rows:
                self._send_html(
                    f"<h2>No processed posts for author: " f"{author_name}</h2>"
                )
                return

            html = processed.build_page(
                post,
                all_rows,
                mode="author",
                author_name=author_name,
            )

            if html is None:
                self._send_redirect("/processed")
                return

            self._send_html(html)
            return

        if path.startswith("/processed/"):
            try:
                row_id = int(path.split("/processed/")[1])
            except ValueError:
                self.send_error(404)
                return

            post, all_rows = processed.get_post(row_id)

            if not post:
                self._send_redirect("/processed")
                return

            html = processed.build_page(
                post,
                all_rows,
                mode="processed",
            )

            if html is None:
                self._send_redirect("/processed")
                return

            self._send_html(html)
            return

        if path == "/blacklist":
            query = urlparse(self.path).query

            params = dict(p.split("=") for p in query.split("&") if "=" in p)

            sort = params.get("sort", "count")

            self._send_html(blacklist.build_blacklist_page(sort))
            return

        if path == "/filters":
            self._send_html(filters.build_filters_page())
            return

        if path == "/authors":
            self._send_html(stats.build_authors_page())
            return

        if path.startswith("/open-folder/"):
            post_id = unquote(path[len("/open-folder/") :])

            folder = os.path.abspath(f"images/{post_id}")

            if os.path.isdir(folder):
                subprocess.Popen(["xdg-open", folder])

            self._send_html(
                "<html><body>Opening... "
                "<a href='javascript:history.back()'>"
                "Go back</a>"
                "</body></html>"
            )
            return

        if path.startswith("/author/"):
            id_part = path[len("/author/") :].split("/")[0]

            if not id_part.isdigit():
                self.send_error(404)
                return

            row_id = int(id_part)

            author_name, post, all_rows = posts.get_author_posts_by_row_id(row_id)

            if author_name is None:
                self.send_error(404)
                return

            if post is None or not all_rows:
                self._send_html(
                    f"<h2>No unprocessed posts for author: " f"{author_name}</h2>"
                )
                return

            html = posts.build_page(
                post,
                all_rows,
                mode="author",
            )

            if html is None:
                self._send_redirect("/")
                return

            self._send_html(html)
            return

        if path.startswith("/post/"):
            try:
                row_id = int(path.split("/post/")[1])
            except ValueError:
                self.send_error(404)
                return

            post, all_rows = posts.get_post(row_id)

            if not post:
                self._send_redirect("/")
                return

            html = posts.build_page(
                post,
                all_rows,
                mode="fifo",
            )

            if html is None:
                self._send_redirect("/")
                return

            self._send_html(html)
            return

        if path.startswith("/images/"):
            filepath = unquote(path.lstrip("/"))

            if os.path.exists(filepath):
                self.send_response(200)
                self.send_header(
                    "Content-type",
                    "image/jpeg",
                )
                self.end_headers()

                with open(filepath, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404)

            return

        if path == "/review":
            first_id = review.get_first_pending_id()

            if first_id:
                self._send_redirect(f"/review/{first_id}")
            else:
                self._send_html("<h2>No pending reviews.</h2>")

            return

        if path.startswith("/review/"):
            try:
                review_id = int(path.split("/review/")[1])
            except ValueError:
                self.send_error(404)
                return

            all_ids = review.get_pending_review_ids()

            if review_id not in all_ids:
                self._send_redirect("/review")
                return

            html = review.build_page(
                review_id,
                all_ids,
            )

            if html is None:
                self._send_redirect("/review")
                return

            self._send_html(html)
            return

        row_id = posts.get_first_unprocessed_id()

        if row_id:
            self._send_redirect(f"/post/{row_id}")
        else:
            self._send_html("<h2>All posts processed.</h2>")

    def do_POST(self):
        if self.path == "/mark":
            self._handle_post(self._route_mark)
            return

        if self.path == "/toggle-selected":
            self._handle_post(self._route_toggle_selected)
            return

        if self.path == "/add-alias":
            self._handle_post(self._route_add_alias)
            return

        if self.path == "/add-blacklist":
            self._handle_post(self._route_add_blacklist)
            return

        if self.path == "/add-filter":
            self._handle_post(self._route_add_filter)
            return

        if self.path == "/delete-blacklist":
            self._handle_post(self._route_delete_blacklist)
            return

        if self.path == "/delete-filter":
            self._handle_post(self._route_delete_filter)
            return

        if self.path == "/db-entry":
            self._handle_post(
                self._route_db_entry,
                error_status_override=True,
            )
            return

        if self.path == "/db-entry-building":
            self._handle_post(
                self._route_db_entry_building,
                error_status_override=True,
            )
            return

        if self.path == "/delete-post":
            self._handle_post(self._route_delete_post)
            return

        if self.path == "/review-action":
            self._handle_post(self._route_review_action)
            return

        if self.path == "/assign-building":
            self._handle_post(self._route_assign_building)
            return

        if self.path == "/dismiss-building":
            self._handle_post(self._route_dismiss_building)
            return

        self.send_error(404)

    # ------------------------------------------------------------------
    # Route implementations
    # ------------------------------------------------------------------

    def _route_mark(self, data):
        row_id = int(data["id"])
        processed = int(data["processed"])

        posts.mark_processed(
            row_id,
            processed,
        )

        return 200, {"ok": True}

    def _route_toggle_selected(self, data):
        row_id = int(data["id"])
        selected = int(data["selected"])

        posts.toggle_selected(
            row_id,
            selected,
        )

        return 200, {"ok": True}

    def _route_add_alias(self, data):
        building_id = int(data["building_id"])

        alias = data["alias"].strip()

        if not alias:
            raise ValueError("Missing alias")

        ok = asyncio.run(
            add_building_alias(
                building_id,
                alias,
            )
        )

        return (
            200 if ok else 500,
            {"ok": ok},
        )

    def _route_add_blacklist(self, data):
        author = data.get(
            "author",
            "",
        ).strip()

        if not author:
            raise ValueError("Missing author")

        author = normalize_author(author)

        inserted, updated = blacklist.add_blacklist(author)

        return 200, {
            "ok": True,
            "inserted": inserted,
            "skipped": updated,
        }

    def _route_add_filter(self, data):
        phrase = data.get(
            "phrase",
            "",
        ).strip()

        if not phrase:
            raise ValueError("Missing phrase")

        if filters.filter_phrase_exists(phrase):
            return 200, {
                "ok": True,
                "already_exists": True,
            }

        filters.add_filter_phrase(phrase)

        return 200, {
            "ok": True,
            "already_exists": False,
        }

    def _route_delete_post(self, data):
        row_id = int(data["id"])

        deleted = posts.delete_post(row_id)

        return 200, {"ok": deleted}

    def _route_delete_blacklist(self, data):
        author = data.get(
            "author",
            "",
        ).strip()

        if not author:
            raise ValueError("Missing author")

        author = normalize_author(author)

        blacklist.delete_blacklist(author)

        return 200, {"ok": True}

    def _route_delete_filter(self, data):
        phrase = data.get(
            "phrase",
            "",
        ).strip()

        if not phrase:
            raise ValueError("Missing phrase")

        filters.delete_filter_phrase(phrase)

        return 200, {"ok": True}

    def _route_db_entry(self, data):
        row_id = int(data["id"])

        post = posts.get_post_by_id(row_id)

        if not post:
            post = review_building.get_building_review_post(row_id)

        if not post:
            raise ValueError(f"post {row_id} not found " "or already processed")

        result_json = post.get("extraction_result_json")

        if not result_json:
            raise ValueError(
                "no extraction result " "(extraction_result_json) " "for this post"
            )

        post_json = json.loads(result_json)

        if not post_json.get("relevant"):
            raise ValueError("extraction marked this " "post as not relevant")

        decision, candidate_property_id = asyncio.run(
            db_entry.enter_post(
                post_json,
                post["author"],
                post["post_url"],
                post["text"],
                post["scraped_at"],
            )
        )

        if decision == "discard":
            posts.mark_processed(
                row_id,
                1,
            )

            return 200, {
                "ok": True,
                "discarded": True,
            }

        if decision == "review":
            core.cur.execute(
                """
                INSERT INTO entry_review_queue (
                    post_id,
                    candidate_property_id,
                    reviewed,
                    created_at
                )
                VALUES (?, ?, 0, ?)
                """,
                (
                    row_id,
                    candidate_property_id,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )

            core.conn.commit()

            posts.mark_processed(
                row_id,
                1,
            )

            return 200, {
                "ok": True,
                "sent_to_review": True,
                "candidate_property_id": candidate_property_id,
            }

        posts.mark_processed(
            row_id,
            1,
        )

        posts.toggle_selected(
            row_id,
            1,
        )

        return 200, {
            "ok": True,
            "property_id": candidate_property_id,
        }

    def _route_db_entry_building(self, data):
        row_id = int(data["id"])

        post = review_building.get_building_review_post(row_id)

        if not post:
            raise ValueError(f"post {row_id} not in building review queue")

        result_json = post.get("extraction_result_json")

        if not result_json:
            raise ValueError(
                "no extraction result " "(extraction_result_json) " "for this post"
            )

        post_json = json.loads(result_json)

        if not post_json.get("relevant"):
            raise ValueError("extraction marked this " "post as not relevant")

        decision, candidate_property_id = asyncio.run(
            db_entry.enter_post(
                post_json,
                post["author"],
                post["post_url"],
                post["text"],
                post["scraped_at"],
            )
        )

        core.cur.execute(
            """
            UPDATE posts
            SET processed = 1, review_building = 0
            WHERE id = ?
            """,
            (row_id,),
        )
        core.conn.commit()

        if decision == "discard":
            return 200, {
                "ok": True,
                "discarded": True,
            }

        if decision == "review":
            core.cur.execute(
                """
                INSERT INTO entry_review_queue (
                    post_id,
                    candidate_property_id,
                    reviewed,
                    created_at
                )
                VALUES (?, ?, 0, ?)
                """,
                (
                    row_id,
                    candidate_property_id,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )

            core.conn.commit()

            return 200, {
                "ok": True,
                "sent_to_review": True,
                "candidate_property_id": candidate_property_id,
            }

        posts.toggle_selected(
            row_id,
            1,
        )

        return 200, {
            "ok": True,
            "property_id": candidate_property_id,
        }

    def _route_review_action(self, data):
        review_id = int(data["id"])
        action = data["action"]

        if action == "approve":
            decision, candidate_property_id = review.approve(review_id)

            return 200, {
                "ok": True,
                "decision": decision,
                "property_id": candidate_property_id,
            }

        if action == "reject":
            review.reject(review_id)

            return 200, {
                "ok": True,
                "rejected": True,
            }

        if action == "dismiss":
            review.dismiss(review_id)

            return 200, {
                "ok": True,
                "dismissed": True,
            }

        raise ValueError(f"unknown action: {action}")

    def _route_assign_building(self, data):
        post_id = int(data["post_id"])

        building_id = int(data["building_id"])

        post = review_building.get_building_review_post(post_id)

        if not post:
            raise ValueError(f"Post {post_id} not in " "building review queue")

        import json
        from db.db_entry import (
            resolve_or_create_owner,
            enter_post_with_known_building,
            get_session,
        )
        import asyncio

        post_json = json.loads(post["extraction_result_json"])

        async def _do():
            async with get_session() as db:
                owner_id = await resolve_or_create_owner(
                    db,
                    post_json,
                    post["author"],
                )

                decision, candidate_id = await enter_post_with_known_building(
                    db,
                    post_json,
                    owner_id,
                    building_id,
                    post["post_url"],
                    post["text"],
                    post["scraped_at"],
                )

                if decision == "insert":
                    await db.commit()
                    return candidate_id

                return None

        property_id = asyncio.run(_do())

        core.cur.execute(
            """
            UPDATE posts
            SET review_building = 0
            WHERE id = ?
            """,
            (post_id,),
        )

        core.conn.commit()

        return 200, {
            "ok": True,
            "property_id": property_id,
        }

    def _route_dismiss_building(self, data):
        post_id = int(data["post_id"])

        core.cur.execute(
            """
            UPDATE posts
            SET review_building = 0
            WHERE id = ?
            """,
            (post_id,),
        )

        core.conn.commit()

        return 200, {"ok": True}

    # ------------------------------------------------------------------
    # Shared HTTP helpers
    # ------------------------------------------------------------------

    # def _handle_post(
    #     self,
    #     route_fn,
    #     error_status_override=False,
    # ):
    #     try:
    #         length = int(
    #             self.headers.get(
    #                 "Content-Length",
    #                 0,
    #             )
    #         )

    #         body = self.rfile.read(length)
    #         data = json.loads(body)

    #         status, payload = route_fn(data)

    #         self._send_json(
    #             status,
    #             payload,
    #         )

    #     except (
    #         db_entry.OwnerConflictError,
    #         db_entry.NoIdentifiableOwnerError,
    #         db_entry.BuildingConflictError,
    #         db_entry.BuildingNotFoundError,
    #     ) as e:
    #         self._send_json(
    #             409,
    #             {"error": str(e)},
    #         )

    #     except Exception as e:
    #         print(
    #             "POST ERROR:",
    #             e,
    #         )

    #         self._send_json(
    #             400 if not error_status_override else 500,
    #             {"error": str(e)},
    #         )

    # def _send_html(self, html: str):
    #     self.send_response(200)

    #     self.send_header(
    #         "Content-type",
    #         "text/html",
    #     )

    #     self.end_headers()

    #     try:
    #         self.wfile.write(html.encode())
    #     except BrokenPipeError:
    #         pass

    # def _send_json(
    #     self,
    #     status: int,
    #     payload: dict,
    # ):
    #     self.send_response(status)

    #     self.send_header(
    #         "Content-type",
    #         "application/json",
    #     )

    #     self.end_headers()

    #     try:
    #         self.wfile.write(json.dumps(payload).encode())
    #     except BrokenPipeError:
    #         pass

    # def _send_redirect(
    #     self,
    #     location: str,
    # ):
    #     self.send_response(302)

    #     self.send_header(
    #         "Location",
    #         location,
    #     )

    #     self.end_headers()

    # def log_message(
    #     self,
    #     format,
    #     *args,
    # ):
    #     pass
