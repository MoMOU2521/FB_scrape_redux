# scrape/scraper.py
import os
import re
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
from scrape.db_ops import (
    is_author_blacklisted,
    increment_blacklist_count,
    matches_filter_phrase,
    save_post,
    get_last_scraped_post,
)


# ===================== DEBUG LOGGER ======================
class DebugLogger:
    def __init__(self, debug_dir):
        # FIXED: ensure debug directory exists
        os.makedirs(debug_dir, exist_ok=True)
        self.log_file = os.path.join(
            debug_dir, f"scrape_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )

    def log(self, msg, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] [{level}] {msg}\n")
        except Exception:
            pass  # Fallback if file write fails
        print(f"[{level}] {msg}")

    def log_post_debug(
        self,
        post_id,
        author_debug,
        text_debug,
        timestamp_debug,
        success,
        failure_reason="",
    ):
        self.log("")
        self.log("=" * 80)
        self.log(f"POST ID : {post_id}")
        self.log("=" * 80)
        self.log("AUTHOR")
        self.log(f"  Selector : {author_debug.get('selector')}")
        self.log(f"  Extracted: {author_debug.get('extracted', '')[:100]}")
        self.log(f"  HTML     : {author_debug.get('html', '')[:200]}")
        self.log("-" * 80)
        self.log("TIMESTAMP")
        self.log(f"  Selector : {timestamp_debug.get('selector')}")
        self.log(f"  Extracted: {timestamp_debug.get('extracted', '')}")
        self.log(f"  HTML     : {timestamp_debug.get('html', '')[:200]}")
        self.log("-" * 80)
        self.log("TEXT")
        self.log(f"  Selector : {text_debug.get('selector')}")
        self.log(f"  Length   : {text_debug.get('length', 0)}")
        self.log(f"  Extracted: {text_debug.get('extracted', '')[:200]}")
        self.log(f"  HTML     : {text_debug.get('html', '')[:200]}")
        if success:
            self.log("-" * 80)
            self.log("STATUS : SUCCESS")
        else:
            self.log("-" * 80)
            self.log(f"STATUS : FAILED ({failure_reason})", "WARN")
        self.log("=" * 80)

    def log_summary(self, result):
        self.log("")
        self.log("#" * 80)
        self.log(f"GROUP SUMMARY : {result['group_name']}")
        self.log("#" * 80)
        self.log(f"  Encountered      : {result['encountered']}")
        self.log(f"  Saved            : {result['saved']}")
        self.log(f"  Skipped (total)  : {result['skipped']}")
        self.log(f"    - dedup        : {result['skip_dedup']}")
        self.log(f"    - filter       : {result['skip_filter']}")
        self.log(f"    - blacklist    : {result['skip_blacklist']}")
        self.log(f"    - no_text      : {result['skip_no_text']}")
        self.log(f"  Stall count      : {result['stall_count']}")
        self.log(f"  Time (s)         : {result['time_seconds']:.1f}")
        self.log(f"  Terminated early : {result['terminated']}")
        if result.get("error"):
            self.log(f"  ERROR            : {result['error']}")
        if result["session_blacklist"]:
            self.log("  Blacklist hits this session:")
            for author, count in result["session_blacklist"].items():
                self.log(f"    - {author}: {count}")
        self.log("#" * 80)


debug = DebugLogger(config.DEBUG_DIR)


# ===================== POST EXTRACTION =====================
UNSCRAMBLE_JS = """
function getAuthor(article) {
    const selectors = [
        'h2 b span', 'h2 span', 'strong span', 'a[role="link"] span',
        'h3 span', 'span[dir="auto"]:first-child', 'div[role="article"] strong'
    ];
    let container = null;
    for (let sel of selectors) {
        container = article.querySelector(sel);
        if (container && container.textContent.trim().length > 1) break;
    }
    if (!container) return "UNKNOWN";
    const children = container.children;
    if (children.length >= 4 && 
        Array.from(children).every(c => (c.textContent || '').length <= 2) && 
        Array.from(children).some(c => parseInt(getComputedStyle(c).order || '0') !== 0)) {
        return Array.from(children)
            .sort((a, b) => (parseInt(getComputedStyle(a).order || '0') - parseInt(getComputedStyle(b).order || '0')))
            .map(c => c.textContent)
            .join('');
    }
    return container.textContent.trim();
}
"""


def extract_post_id(article):
    try:
        link = article.query_selector('a[href*="/posts/"]')
        if link:
            href = link.get_attribute("href")
            m = re.search(r"/posts/([^/?]+)", href)
            if m:
                return m.group(1)
    except:
        pass
    return None


def _expand_see_more(container):
    if not container:
        return
    for btn in container.query_selector_all(
        'div[role="button"]:has-text("See more"), '
        'div[role="button"]:has-text("ดูเพิ่ม"), '
        'div[role="button"]:has-text("More"), '
        'div[role="button"]:has-text("Continue reading")'
    ):
        try:
            btn.click()
            time.sleep(0.5)
        except:
            pass


def extract_post_data(article):
    post_data = {
        "post_id": None,
        "author": "UNKNOWN",
        "text": "",
        "timestamp": None,
        "success": False,
        "author_debug": {"selector": "", "html": "", "extracted": ""},
        "text_debug": {"selector": "", "html": "", "extracted": "", "length": 0},
        "timestamp_debug": {"selector": "", "html": "", "extracted": ""},
        "failure_reason": "",
    }

    try:
        link = article.query_selector('a[href*="/posts/"]')
        if link:
            href = link.get_attribute("href")
            m = re.search(r"/posts/([^/?]+)", href)
            if m:
                post_data["post_id"] = m.group(1)
    except:
        pass

    try:
        author_name = article.evaluate(f"""
            (element) => {{
                {UNSCRAMBLE_JS}
                return getAuthor(element);
            }}
        """)
        if author_name and author_name != "UNKNOWN":
            post_data["author"] = author_name
            container_html = article.evaluate(f"""
                (element) => {{
                    {UNSCRAMBLE_JS}
                    const selectors = ['h2 b span', 'h2 span', 'strong span', 'a[role="link"] span', 'h3 span', 'span[dir="auto"]:first-child', 'div[role="article"] strong'];
                    for (let sel of selectors) {{
                        let c = element.querySelector(sel);
                        if (c && c.textContent.trim().length > 1) return c.outerHTML;
                    }}
                    return '';
                }}
            """)
            post_data["author_debug"] = {
                "selector": "unscramble_js",
                "html": (container_html or "")[:300],
                "extracted": author_name[:200],
            }
    except Exception as e:
        debug.log(f"  Author extraction failed: {e}", "WARN")

    timestamp_raw = None
    timestamp_selector = ""
    try:
        time_links = article.query_selector_all(
            'a[href*="/posts/"], a[href*="?story_fbid"]'
        )
        for link in time_links:
            aria = link.get_attribute("aria-label")
            if aria:
                timestamp_raw = aria.strip()
                timestamp_selector = "a[href*='/posts/'] aria-label"
                break
            link_text = link.inner_text().strip()
            if link_text:
                if any(
                    t in link_text.lower()
                    for t in ["h", "d", "w", "min", "yesterday", "just now"]
                ):
                    timestamp_raw = link_text
                    timestamp_selector = "a[href*='/posts/'] inner_text"
                    break

        if timestamp_raw:
            post_data["timestamp"] = timestamp_raw
            post_data["timestamp_debug"] = {
                "selector": timestamp_selector,
                "html": "",
                "extracted": timestamp_raw[:200],
            }
        else:
            post_data["timestamp_debug"] = {
                "selector": timestamp_selector or "a[href*='/posts/']",
                "html": "",
                "extracted": "NO_TIMESTAMP",
            }
    except Exception as e:
        post_data["timestamp_debug"] = {
            "selector": "ERROR",
            "html": "",
            "extracted": f"EXCEPTION: {str(e)[:100]}",
        }

    full_text = ""
    used_selector = ""
    html_snippet = ""

    for attr in [
        'data-ad-comet-preview="message"',
        'data-ad-preview="message"',
        'data-ad-rendering-role="story_message"',
    ]:
        container = article.query_selector(f"div[{attr}]")
        if container:
            _expand_see_more(container)
            full_text = container.inner_text().strip()
            if full_text:
                used_selector = f"div[{attr}]"
                html_snippet = container.evaluate("el => el.outerHTML")[:1000]
                break

    if not full_text:
        candidates = article.query_selector_all('div[dir="auto"]')
        for container in candidates:
            _expand_see_more(container)
            text = container.inner_text().strip()
            if len(text) > 50:
                full_text = text
                used_selector = 'div[dir="auto"]'
                html_snippet = container.evaluate("el => el.outerHTML")[:1000]
                break

    if not full_text:
        for selector in [
            "div.x1e56ztr",
            'div[class*="story_body_container"]',
            'div[class*="user_content"]',
        ]:
            container = article.query_selector(selector)
            if container:
                _expand_see_more(container)
                text = container.inner_text().strip()
                if len(text) > 50:
                    full_text = text
                    used_selector = selector
                    html_snippet = container.evaluate("el => el.outerHTML")[:1000]
                    break

    if not full_text:
        raw = article.inner_text().strip()
        lines = raw.split("\n")
        if len(lines) > 30:
            raw = "\n".join(lines[:30])
        if raw:
            full_text = raw
            used_selector = "article.inner_text() fallback"
            html_snippet = raw[:1000]

    if full_text:
        post_data["text"] = full_text
        post_data["text_debug"] = {
            "selector": used_selector,
            "html": html_snippet,
            "extracted": full_text[:200],
            "length": len(full_text),
        }
    else:
        post_data["failure_reason"] = "no_text"

    if post_data["text"] and post_data["author"] != "UNKNOWN":
        post_data["success"] = True
    elif post_data["text"]:
        post_data["success"] = True
    else:
        post_data["success"] = False

    return post_data


# ===================== FILTER HELPERS =====================
# def build_stop_list(cutoff_hours):
#     """
#     Facebook only ever renders a fixed, small vocabulary of relative
#     timestamps: 1h-23h, then 1d-6d, then it switches to weeks (1w-4w+).
#     Generate every value from cutoff_hours up through that whole range,
#     once, at setup time. Closed set -> no gap can ever slip through,
#     no matter how sparse the actual posting frequency is.
#     """
#     stop_list = []
#     for h in range(1, 24):
#         if h >= cutoff_hours:
#             stop_list.append(f"{h}h")
#     for d in range(1, 7):
#         if d * 24 >= cutoff_hours:
#             stop_list.append(f"{d}d")
#     for w in range(1, 5):
#         if w * 24 * 7 >= cutoff_hours:
#             stop_list.append(f"{w}w")
#     return stop_list


def should_stop(timestamp_str, stop_list=None):
    if not timestamp_str or not stop_list:
        return False
    ts = timestamp_str.strip().lower()
    return ts in stop_list


# ===================== FILTER HELPERS =====================
def should_stop(timestamp_str, stop_list=None):
    if not timestamp_str or not stop_list:
        return False
    ts = timestamp_str.strip().lower()
    return ts in stop_list


# ===================== MAIN SCRAPER ========================
# def scrape_group(
#     group: dict,
#     auto_mode=True,
#     target=None,
#     stop_timestamps=None,
#     shared_heartbeat=None,
# ):
#     monitor = FreezeMonitor(shared_heartbeat=shared_heartbeat)
#     saved_count = 0
#     encountered = 0
#     seen_ids = set()
#     skip_dedup = 0
#     skip_blacklist = 0
#     skip_filter = 0
#     skip_no_text = 0
#     stall_count = 0
#     start_time = time.time()
#     terminated = False
#     error_msg = None
#     session_blacklist_tracker = {}

#     debug.log(f"\n{'='*60}")
#     debug.log(f"STARTING GROUP: {group['name']}")
#     debug.log(f"{'='*60}")

#     p = None
#     browser = None
#     page = None

#     try:
#         p, browser, page = launch_browser()

#         page.goto(group["url"])
#         time.sleep(3)
#         monitor.touch()

#         monitor.start()

#         cursor_x = random.randint(100, 500)
#         cursor_y = random.randint(100, 500)
#         cursor_x, cursor_y = jiggle(page, cursor_x, cursor_y)
#         monitor.touch()

#         if monitor.is_frozen:
#             debug.log(
#                 "  ⚠️ Freeze detected after initial jiggle, abandoning group",
#                 "WARN",
#             )
#             terminated = True
#             error_msg = "Freeze detected during initialization"
#             return _build_result(
#                 group,
#                 encountered,
#                 saved_count,
#                 skip_dedup,
#                 skip_filter,
#                 skip_blacklist,
#                 skip_no_text,
#                 stall_count,
#                 start_time,
#                 terminated,
#                 session_blacklist_tracker,
#                 error_msg,
#             )

#         stop_scraping = False
#         stall_counter = 0
#         last_article_count = 0

#         while True:
#             if monitor.is_frozen:
#                 debug.log("  ⚠️ Freeze detected at loop top, abandoning group", "WARN")
#                 terminated = True
#                 error_msg = "Freeze detected during scraping"
#                 break

#             articles = page.query_selector_all('[role="article"]')
#             monitor.touch()
#             if monitor.is_frozen:
#                 debug.log(
#                     "  ⚠️ Freeze detected after query_selector_all, abandoning group",
#                     "WARN",
#                 )
#                 terminated = True
#                 error_msg = "Freeze detected after querying articles"
#                 break

#             current_count = len(articles)
#             if current_count == last_article_count and current_count > 0:
#                 stall_counter += 1
#             else:
#                 stall_counter = 0
#                 last_article_count = current_count

#             if stall_counter in (1, 2):
#                 debug.log(
#                     f"  ⚠️ Stall #{stall_counter} detected ({current_count} articles) - attempting recovery",
#                     "WARN",
#                 )
#                 stall_count += 1
#                 cursor_x, cursor_y = recover_stall(page, cursor_x, cursor_y)
#                 monitor.touch()
#                 if monitor.is_frozen:
#                     debug.log(
#                         "  ⚠️ Freeze detected after recover_stall, abandoning group",
#                         "WARN",
#                     )
#                     terminated = True
#                     error_msg = "Freeze detected after stall recovery"
#                     break

#             if stall_counter >= 3:
#                 debug.log("  ⚠️ STALLED 3 TIMES - terminating group", "WARN")
#                 stall_count += 1
#                 terminated = True
#                 error_msg = "Stalled 3 times, abandoning group"
#                 break

#             for article in articles:
#                 if monitor.is_frozen:
#                     debug.log(
#                         "  ⚠️ Freeze detected inside article loop, abandoning group",
#                         "WARN",
#                     )
#                     terminated = True
#                     error_msg = "Freeze detected during article processing"
#                     break

#                 post_id = extract_post_id(article)
#                 monitor.touch()
#                 if monitor.is_frozen:
#                     debug.log(
#                         "  ⚠️ Freeze detected after extract_post_id, abandoning group",
#                         "WARN",
#                     )
#                     terminated = True
#                     error_msg = "Freeze detected after post ID extraction"
#                     break

#                 if not post_id or post_id in seen_ids:
#                     continue

#                 seen_ids.add(post_id)
#                 encountered += 1

#                 if not auto_mode and target and encountered > target:
#                     stop_scraping = True
#                     break

#                 print(f"📄 [{encountered}] {post_id}")

#                 _extract_t0 = time.time()
#                 post = extract_post_data(article)
#                 monitor.touch()
#                 if monitor.is_frozen:
#                     debug.log(
#                         "  ⚠️ Freeze detected after extract_post_data, abandoning group",
#                         "WARN",
#                     )
#                     terminated = True
#                     error_msg = "Freeze detected after data extraction"
#                     break

#                 _extract_elapsed = time.time() - _extract_t0
#                 if _extract_elapsed > 8:
#                     debug.log(
#                         f"  ⚠️ extract_post_data took {_extract_elapsed:.1f}s on post {post_id}",
#                         "WARN",
#                     )

#                 if config.VERBOSE_POST_LOG or not post["success"]:
#                     debug.log_post_debug(
#                         post_id,
#                         post["author_debug"],
#                         post["text_debug"],
#                         post["timestamp_debug"],
#                         post["success"],
#                         post.get("failure_reason", ""),
#                     )

#                 if auto_mode and post["timestamp"]:
#                     # FIXED: explicit handling for None
#                     if stop_timestamps is None:
#                         stop_list = config.STOP_TIMESTAMPS
#                         debug.log(
#                             "  ⚠️ Using default STOP_TIMESTAMPS from config", "WARN"
#                         )
#                     else:
#                         stop_list = stop_timestamps

#                     if should_stop(post["timestamp"], stop_list):
#                         print(
#                             f"   🛑 STOP: found first stop timestamp ({post['timestamp']})"
#                         )
#                         stop_scraping = True
#                         break

#                 # DB OPERATIONS - extracted to db_ops.py
#                 if post["success"] and is_author_blacklisted(post["author"]):
#                     increment_blacklist_count(post["author"])
#                     session_blacklist_tracker[post["author"]] = (
#                         session_blacklist_tracker.get(post["author"], 0) + 1
#                     )
#                     debug.log(
#                         f" ⏭️ SKIPPED: author blacklisted ({post['author']}) "
#                         f"- session count: {session_blacklist_tracker[post['author']]}",
#                         "WARN",
#                     )
#                     skip_blacklist += 1
#                     continue

#                 if not post["success"]:
#                     skip_no_text += 1
#                 else:
#                     matched = matches_filter_phrase(post["text"])
#                     if matched:
#                         matched_phrase = matched["phrase"]
#                         debug.log(
#                             f" ⏭️ SKIPPED: filtered by phrase '{matched_phrase}'",
#                             "WARN",
#                         )
#                         skip_filter += 1
#                     else:
#                         scraped_at = datetime.now(timezone.utc).isoformat()
#                         if save_post(
#                             post["post_id"],
#                             post["author"],
#                             post["timestamp"],
#                             post["text"],
#                             f"https://www.facebook.com/{post['post_id']}",
#                             group["name"],
#                             scraped_at,
#                         ):
#                             saved_count += 1
#                             print(f"   ✅ SAVED (total: {saved_count})")
#                         else:
#                             debug.log("  SKIPPED: duplicate author+text in DB", "WARN")
#                             skip_dedup += 1

#             if stop_scraping or terminated:
#                 break

#             if not auto_mode and target and encountered >= target:
#                 break

#             _scroll_t0 = time.time()
#             page.evaluate("window.scrollBy(0, window.innerHeight)")
#             monitor.touch()
#             if monitor.is_frozen:
#                 debug.log("  ⚠️ Freeze detected after scroll, abandoning group", "WARN")
#                 terminated = True
#                 error_msg = "Freeze detected after scroll"
#                 break

#             _scroll_elapsed = time.time() - _scroll_t0
#             if _scroll_elapsed > 8:
#                 debug.log(
#                     f"  ⚠️ main scroll evaluate() took {_scroll_elapsed:.1f}s",
#                     "WARN",
#                 )

#             time.sleep(random.uniform(config.SCROLL_PAUSE_MIN, config.SCROLL_PAUSE_MAX))
#             monitor.touch()
#             if monitor.is_frozen:
#                 debug.log("  ⚠️ Freeze detected after sleep, abandoning group", "WARN")
#                 terminated = True
#                 error_msg = "Freeze detected after sleep"
#                 break

#             cursor_x, cursor_y = jiggle(page, cursor_x, cursor_y)
#             monitor.touch()
#             if monitor.is_frozen:
#                 debug.log("  ⚠️ Freeze detected after jiggle, abandoning group", "WARN")
#                 terminated = True
#                 error_msg = "Freeze detected after jiggle"
#                 break

#     except Exception as e:
#         error_msg = str(e)
#         debug.log(f"ERROR in group {group['name']}: {error_msg}", "ERROR")
#     finally:
#         # FIXED: always clean up resources
#         if browser:
#             try:
#                 browser.close()
#             except:
#                 pass
#         if p:
#             try:
#                 p.stop()
#             except:
#                 pass
#         monitor.stop()


#     result = _build_result(
#         group,
#         encountered,
#         saved_count,
#         skip_dedup,
#         skip_filter,
#         skip_blacklist,
#         skip_no_text,
#         stall_count,
#         start_time,
#         terminated,
#         session_blacklist_tracker,
#         error_msg,
#     )
#     debug.log_summary(result)
#     return result
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
        "error": error_msg,  # FIXED: propagate errors
        "session_blacklist": session_blacklist_tracker,
    }
