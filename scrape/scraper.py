# scrape/scraper.py
import time
import random
from datetime import datetime, timezone

import scrape.config as config
from scrape.browser import (
    FreezeMonitor,
    launch_browser,
    jiggle,
    recover_stall,
)
from scrape.scraper_ops.DebugLogger import debug
from scrape.scraper_ops.post_extraction import extract_post_id, extract_post_data
from db.services.scraper.post_validation import (
    is_author_blacklisted,
    increment_blacklist_count,
    matches_filter_phrase,
)
from db.services.scraper.get_last_scraped_post import get_last_scraped_post
from db.services.scraper.save_post import save_post


# ===================== FILTER HELPERS =====================
def should_stop(timestamp_str, stop_list=None):
    if not timestamp_str or not stop_list:
        return False
    ts = timestamp_str.strip().lower()
    return ts in stop_list


# ===================== MAIN SCRAPER ========================
def scrape_group(
    group: dict,
    stop_mode,
    stop_timestamps=None,
    shared_heartbeat=None,
):
    monitor = FreezeMonitor(shared_heartbeat=shared_heartbeat)
    saved_count = 0
    encountered = 0
    seen_ids = set()
    skip_dedup = 0
    skip_blacklist = 0
    skip_filter = 0
    skip_no_text = 0
    stall_count = 0
    start_time = time.time()
    terminated = False
    error_msg = None
    session_blacklist_tracker = {}

    # last-post boundary is only relevant in that mode, but resolving it
    # unconditionally keeps the branch below simple and cheap either way
    last_scraped = (
        get_last_scraped_post(group["name"]) if stop_mode == "last_post" else None
    )

    debug.log(f"\n{'='*60}")
    debug.log(f"STARTING GROUP: {group['name']}")
    debug.log(f"STOP MODE: {stop_mode}")
    if stop_mode == "last_post":
        if last_scraped:
            debug.log(
                f"LAST SCRAPED POST: "
                f"{last_scraped['group_name']} / {last_scraped['post_id']}"
            )
        else:
            debug.log("LAST SCRAPED POST: NONE (first scrape of this group)")
    debug.log(f"{'='*60}")

    p = None
    browser = None
    page = None

    try:
        p, browser, page = launch_browser()

        page.goto(group["url"])
        time.sleep(3)
        monitor.touch()

        monitor.start()

        cursor_x = random.randint(100, 500)
        cursor_y = random.randint(100, 500)
        cursor_x, cursor_y = jiggle(page, cursor_x, cursor_y)
        monitor.touch()

        if monitor.is_frozen:
            debug.log(
                "  ⚠️ Freeze detected after initial jiggle, abandoning group",
                "WARN",
            )
            terminated = True
            error_msg = "Freeze detected during initialization"
            return _build_result(
                group,
                encountered,
                saved_count,
                skip_dedup,
                skip_filter,
                skip_blacklist,
                skip_no_text,
                stall_count,
                start_time,
                terminated,
                session_blacklist_tracker,
                error_msg,
            )

        stop_scraping = False
        stall_counter = 0
        last_article_count = 0

        while True:
            if monitor.is_frozen:
                debug.log("  ⚠️ Freeze detected at loop top, abandoning group", "WARN")
                terminated = True
                error_msg = "Freeze detected during scraping"
                break

            articles = page.query_selector_all('[role="article"]')
            monitor.touch()
            if monitor.is_frozen:
                debug.log(
                    "  ⚠️ Freeze detected after query_selector_all, abandoning group",
                    "WARN",
                )
                terminated = True
                error_msg = "Freeze detected after querying articles"
                break

            current_count = len(articles)
            if current_count == last_article_count and current_count > 0:
                stall_counter += 1
            else:
                stall_counter = 0
                last_article_count = current_count

            if stall_counter in (1, 2):
                debug.log(
                    f"  ⚠️ Stall #{stall_counter} detected ({current_count} articles) - attempting recovery",
                    "WARN",
                )
                stall_count += 1
                cursor_x, cursor_y = recover_stall(page, cursor_x, cursor_y)
                monitor.touch()
                if monitor.is_frozen:
                    debug.log(
                        "  ⚠️ Freeze detected after recover_stall, abandoning group",
                        "WARN",
                    )
                    terminated = True
                    error_msg = "Freeze detected after stall recovery"
                    break

            if stall_counter >= 3:
                debug.log("  ⚠️ STALLED 3 TIMES - terminating group", "WARN")
                stall_count += 1
                terminated = True
                error_msg = "Stalled 3 times, abandoning group"
                break

            for article in articles:
                if monitor.is_frozen:
                    debug.log(
                        "  ⚠️ Freeze detected inside article loop, abandoning group",
                        "WARN",
                    )
                    terminated = True
                    error_msg = "Freeze detected during article processing"
                    break

                post_id = extract_post_id(article)
                monitor.touch()
                if monitor.is_frozen:
                    debug.log(
                        "  ⚠️ Freeze detected after extract_post_id, abandoning group",
                        "WARN",
                    )
                    terminated = True
                    error_msg = "Freeze detected after post ID extraction"
                    break

                if not post_id or post_id in seen_ids:
                    continue

                # last-post boundary check happens BEFORE seen_ids/encountered
                # so the old boundary post is never counted, extracted, or saved
                if (
                    stop_mode == "last_post"
                    and last_scraped is not None
                    and group["name"] == last_scraped["group_name"]
                    and post_id == last_scraped["post_id"]
                ):
                    print(f"   🛑 STOP: reached last scraped post ({post_id})")
                    stop_scraping = True
                    break

                seen_ids.add(post_id)
                encountered += 1

                print(f"📄 [{encountered}] {post_id}")

                _extract_t0 = time.time()
                post = extract_post_data(article)
                monitor.touch()
                if monitor.is_frozen:
                    debug.log(
                        "  ⚠️ Freeze detected after extract_post_data, abandoning group",
                        "WARN",
                    )
                    terminated = True
                    error_msg = "Freeze detected after data extraction"
                    break

                _extract_elapsed = time.time() - _extract_t0
                if _extract_elapsed > 8:
                    debug.log(
                        f"  ⚠️ extract_post_data took {_extract_elapsed:.1f}s on post {post_id}",
                        "WARN",
                    )

                if config.VERBOSE_POST_LOG or not post["success"]:
                    debug.log_post_debug(
                        post_id,
                        post["author_debug"],
                        post["text_debug"],
                        post["timestamp_debug"],
                        post["success"],
                        post.get("failure_reason", ""),
                    )

                # time-marker boundary check — only in that mode
                if stop_mode == "time_marker" and post["timestamp"]:
                    if stop_timestamps is None:
                        stop_list = config.STOP_TIMESTAMPS
                        debug.log(
                            "  ⚠️ Using default STOP_TIMESTAMPS from config", "WARN"
                        )
                    else:
                        stop_list = stop_timestamps

                    if should_stop(post["timestamp"], stop_list):
                        print(
                            f"   🛑 STOP: found first stop timestamp ({post['timestamp']})"
                        )
                        stop_scraping = True
                        break

                # DB OPERATIONS
                if post["success"] and is_author_blacklisted(post["author"]):
                    increment_blacklist_count(post["author"])
                    session_blacklist_tracker[post["author"]] = (
                        session_blacklist_tracker.get(post["author"], 0) + 1
                    )
                    debug.log(
                        f" ⏭️ SKIPPED: author blacklisted ({post['author']}) "
                        f"- session count: {session_blacklist_tracker[post['author']]}",
                        "WARN",
                    )
                    skip_blacklist += 1
                    continue

                if not post["success"]:
                    skip_no_text += 1
                else:
                    matched = matches_filter_phrase(post["text"])
                    if matched:
                        matched_phrase = matched["phrase"]
                        debug.log(
                            f" ⏭️ SKIPPED: filtered by phrase '{matched_phrase}'",
                            "WARN",
                        )
                        skip_filter += 1
                    else:
                        scraped_at = datetime.now(timezone.utc).isoformat()
                        if save_post(
                            post["post_id"],
                            post["author"],
                            post["timestamp"],
                            post["text"],
                            f"https://www.facebook.com/{post['post_id']}",
                            group["name"],
                            scraped_at,
                        ):
                            saved_count += 1
                            print(f"   ✅ SAVED (total: {saved_count})")
                        else:
                            debug.log("  SKIPPED: duplicate author+text in DB", "WARN")
                            skip_dedup += 1

            if stop_scraping or terminated:
                break

            _scroll_t0 = time.time()
            page.evaluate("window.scrollBy(0, window.innerHeight)")
            monitor.touch()
            if monitor.is_frozen:
                debug.log("  ⚠️ Freeze detected after scroll, abandoning group", "WARN")
                terminated = True
                error_msg = "Freeze detected after scroll"
                break

            _scroll_elapsed = time.time() - _scroll_t0
            if _scroll_elapsed > 8:
                debug.log(
                    f"  ⚠️ main scroll evaluate() took {_scroll_elapsed:.1f}s",
                    "WARN",
                )

            time.sleep(random.uniform(config.SCROLL_PAUSE_MIN, config.SCROLL_PAUSE_MAX))
            monitor.touch()
            if monitor.is_frozen:
                debug.log("  ⚠️ Freeze detected after sleep, abandoning group", "WARN")
                terminated = True
                error_msg = "Freeze detected after sleep"
                break

            cursor_x, cursor_y = jiggle(page, cursor_x, cursor_y)
            monitor.touch()
            if monitor.is_frozen:
                debug.log("  ⚠️ Freeze detected after jiggle, abandoning group", "WARN")
                terminated = True
                error_msg = "Freeze detected after jiggle"
                break

    except Exception as e:
        error_msg = str(e)
        debug.log(f"ERROR in group {group['name']}: {error_msg}", "ERROR")
    finally:
        if browser:
            try:
                browser.close()
            except:
                pass
        if p:
            try:
                p.stop()
            except:
                pass
        monitor.stop()

    result = _build_result(
        group,
        encountered,
        saved_count,
        skip_dedup,
        skip_filter,
        skip_blacklist,
        skip_no_text,
        stall_count,
        start_time,
        terminated,
        session_blacklist_tracker,
        error_msg,
    )
    debug.log_summary(result)
    return result


def _build_result(
    group,
    encountered,
    saved,
    skip_dedup,
    skip_filter,
    skip_blacklist,
    skip_no_text,
    stall_count,
    start_time,
    terminated,
    session_blacklist_tracker,
    error_msg=None,
):
    elapsed = time.time() - start_time
    return {
        "group_name": group["name"],
        "encountered": encountered,
        "saved": saved,
        "skipped": skip_dedup + skip_blacklist + skip_filter + skip_no_text,
        "skip_dedup": skip_dedup,
        "skip_filter": skip_filter,
        "skip_blacklist": skip_blacklist,
        "skip_no_text": skip_no_text,
        "stall_count": stall_count,
        "time_seconds": elapsed,
        "terminated": terminated,
        "error": error_msg,
        "session_blacklist": session_blacklist_tracker,
    }
