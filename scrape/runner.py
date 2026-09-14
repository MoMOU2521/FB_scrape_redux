# scrape/runner.py

import time
import multiprocessing
import traceback
from wcwidth import wcswidth
from db.database import db

import scrape.config as config
from web.blacklist import get_blacklist_counts
from scrape.scraper import scrape_group


def _empty_result(group, error):
    return {
        "group_name": group["name"],
        "encountered": 0,
        "saved": 0,
        "skipped": 0,
        "skip_dedup": 0,
        "skip_filter": 0,
        "skip_blacklist": 0,
        "skip_no_text": 0,
        "stall_count": 0,
        "time_seconds": 0,
        "terminated": True,
        "error": error,
        "session_blacklist": {},
    }


def _scrape_group_worker(
    group,
    stop_mode,
    stop_timestamps,
    shared_heartbeat,
    result_queue,
):
    """
    Runs in a separate OS process. Opens its own DB connection, runs
    scrape_group, and puts the result on the queue for the parent to collect.
    """

    try:
        result = scrape_group(
            group,
            stop_mode=stop_mode,
            stop_timestamps=stop_timestamps,
            shared_heartbeat=shared_heartbeat,
        )
    except Exception as e:
        traceback.print_exc()
        result = _empty_result(group, str(e))
    finally:
        db.close()
    result_queue.put(result)


def run_group_with_watchdog(group, stop_mode, stop_timestamps, watchdog_timeout=None):
    """
    Runs scrape_group for one group in a subprocess. If the subprocess's
    heartbeat goes stale for longer than watchdog_timeout seconds, the
    subprocess is force-killed and the group is abandoned with an error
    result, instead of hanging forever.
    """
    if watchdog_timeout is None:
        watchdog_timeout = getattr(config, "WATCHDOG_TIMEOUT", 60)

    shared_heartbeat = multiprocessing.Value("d", time.time())
    result_queue = multiprocessing.Queue()
    lock = multiprocessing.Lock()

    process = multiprocessing.Process(
        target=_scrape_group_worker,
        args=(
            group,
            stop_mode,
            stop_timestamps,
            shared_heartbeat,
            result_queue,
        ),
    )
    process.start()

    while True:
        process.join(timeout=5)
        if not process.is_alive():
            break

        with lock:
            stuck_for = time.time() - shared_heartbeat.value
        if stuck_for > watchdog_timeout:
            print(
                f"⚠️ WATCHDOG: no heartbeat for {stuck_for:.0f}s on group "
                f"'{group['name']}' - killing process"
            )
            process.terminate()
            process.join(timeout=5)
            if process.is_alive():
                process.kill()
                process.join(timeout=5)
            return _empty_result(
                group,
                f"watchdog killed process after {stuck_for:.0f}s with no heartbeat",
            )

    try:
        result = result_queue.get(timeout=5)
        if result.get("error") is not None:
            print(f"⚠️ Group {group['name']} returned error: {result['error']}")
    except Exception:
        result = _empty_result(group, "process exited without returning a result")

    return result


def print_summary(all_results):
    total_encountered = sum(r["encountered"] for r in all_results)
    total_saved = sum(r["saved"] for r in all_results)
    total_skipped = sum(r["skipped"] for r in all_results)
    total_dedup = sum(r["skip_dedup"] for r in all_results)
    total_filter = sum(r["skip_filter"] for r in all_results)
    total_blacklist = sum(r["skip_blacklist"] for r in all_results)
    total_no_text = sum(r["skip_no_text"] for r in all_results)
    total_stalls = sum(r["stall_count"] for r in all_results)
    total_time = sum(r["time_seconds"] for r in all_results)
    total_terminated = sum(1 for r in all_results if r.get("terminated", False))
    errors = [r for r in all_results if r["error"]]

    print("\n" + "=" * 100)
    print("                  TOTAL SCRAPE SUMMARY")
    print("=" * 100)
    print(
        f"  {'Status':<4} {'Group':<30} {'Saved':>5} {'Posts':>5} {'Dedup':>6} "
        f"{'Filter':>6} {'Black':>6} {'NoTxt':>6} {'Stalls':>6} {'Term':>4} {'Time':>7}"
    )
    print("  " + "-" * 95)

    for r in all_results:
        status = "❌" if r["error"] else "✅"
        term_flag = "Y" if r.get("terminated", False) else "N"

        # FIX: Use wcwidth to properly pad Thai text
        raw_name = r["group_name"][:30]
        try:
            display_width = wcswidth(raw_name)
            if display_width < 0:
                display_width = len(raw_name)
        except:
            display_width = len(raw_name)
        padding = max(0, 30 - display_width)

        print(
            f"  {status} {raw_name}{' ' * padding} "
            f"{r['saved']:>5} {r['encountered']:>5} "
            f"{r['skip_dedup']:>6} {r['skip_filter']:>6} "
            f"{r['skip_blacklist']:>6} {r['skip_no_text']:>6} "
            f"{r['stall_count']:>6} {term_flag:>4} {r['time_seconds']:>7.0f}"
        )

    print("-" * 95)
    print(f"  Total groups processed : {len(all_results)}")
    print(f"  Total posts encountered: {total_encountered}")
    print(f"  Total saved            : {total_saved}")
    print(f"  Total skipped          : {total_skipped}")
    print(f"    ↳ Deduplicated : {total_dedup}")
    print(f"    ↳ Filter phrase: {total_filter}")
    print(f"    ↳ Blacklisted  : {total_blacklist}")
    print(f"    ↳ No text      : {total_no_text}")
    print(f"  Total stalls           : {total_stalls}")
    print(f"  Total terminated       : {total_terminated}")
    print(f"  Total time             : {total_time:.0f}s")

    all_session_blacklists = {}
    for r in all_results:
        tracker = r.get("session_blacklist", {})
        for author, session_count in tracker.items():
            all_session_blacklists[author] = (
                all_session_blacklists.get(author, 0) + session_count
            )

    if all_session_blacklists:
        try:
            lifetime_counts = get_blacklist_counts(all_session_blacklists.keys())
            print("\n" + "-" * 95)
            print("  🚫 BLACKLISTED AUTHORS (this session across all groups):")
            sorted_offenders = sorted(
                all_session_blacklists.items(), key=lambda x: x[1], reverse=True
            )
            for author, session_count in sorted_offenders:
                lifetime = lifetime_counts.get(author, 0)
                # FIX: Also pad author names with wcwidth
                author_display = author[:40]
                try:
                    author_width = wcswidth(author_display)
                    if author_width < 0:
                        author_width = len(author_display)
                except:
                    author_width = len(author_display)
                author_padding = max(0, 40 - author_width)
                print(
                    f"    {author_display}{' ' * author_padding} : {session_count:>3} this session, {lifetime:>3} total"
                )
            print("")
        except Exception as e:
            print(f"  ⚠️ Could not retrieve lifetime blacklist counts: {e}")

    if errors:
        print("-" * 60)
        print("  ERRORS:")
        for r in errors:
            print(f"    - {r['group_name']}: {r['error']}")
    print("=" * 100)
