# main.py
import re

from db.database import db
import scrape.config as config
from web.queries.blacklist import get_blacklist_counts
from scrape.runner import run_group_with_watchdog, print_summary

from db.services.posts.processing import cleanup_old_posts


def _parse_cutoff_to_hours(user_input):
    m = re.search(r"(\d+)\s*(h|d|w)", user_input.strip().lower())
    if not m:
        return None
    value, unit = int(m.group(1)), m.group(2)
    if unit == "h":
        return value
    if unit == "d":
        return value * 24
    if unit == "w":
        return value * 24 * 7
    return None


def get_stop_timestamps():
    default_input = "1d"
    print("\nStop scraping once a post is at least this old.")
    print("Examples: 6h, 12h, 1d, 2d")
    print(f"Press Enter for default [{default_input}]")
    user_input = input("> ").strip().lower() or default_input

    cutoff_hours = _parse_cutoff_to_hours(user_input)
    while cutoff_hours is None:
        print(f"Couldn't parse '{user_input}', try again (e.g. 6h, 1d, 2w):")
        user_input = input("> ").strip().lower()
        cutoff_hours = _parse_cutoff_to_hours(user_input)

    return config.build_stop_list(cutoff_hours)


def get_stop_mode():
    """
    Prompts for one of the two stopping methods and returns
    (stop_mode, stop_timestamps).

    stop_mode is "time_marker" or "last_post".
    stop_timestamps is only populated for "time_marker"; it's None
    for "last_post" since that boundary comes from the DB instead.
    """
    print("\nStop scraping method:")
    print("  1. Time marker")
    print("  2. Last scraped post")
    choice = input("Enter mode (1 or 2): ").strip()

    if choice == "1":
        stop_timestamps = get_stop_timestamps()
        print(
            f"Time marker mode: will stop at first post with timestamp in {stop_timestamps}"
        )
        return "time_marker", stop_timestamps
    elif choice == "2":
        print(
            "Last scraped post mode: will stop at the last post saved for this group."
        )
        return "last_post", None
    else:
        return None, None


def main():
    print("\nWhich group?")
    for k, g in config.GROUPS.items():
        print(f"  {k}. {g['name']}")
    print("  T. ALL groups")
    choice = input("Enter number or 'T': ").strip()
    # db = LocalDatabase(DB_FILE)

    # Cleanup old posts at session start using shared core connection.
    cleanup_old_posts()

    if choice.upper() == "T":
        stop_mode, stop_timestamps = get_stop_mode()
        while stop_mode is None:
            print("Invalid mode")
            stop_mode, stop_timestamps = get_stop_mode()

        print(f"\nTOTAL MODE: Processing all groups (stop mode: {stop_mode})")
        all_results = []
        for key, group in config.GROUPS.items():
            result = run_group_with_watchdog(group, stop_mode, stop_timestamps)
            all_results.append(result)
            if result["error"]:
                print(f"⚠️ Group {key} failed, continuing to next...")
        print_summary(all_results)
        return

    if choice not in config.GROUPS:
        print("Invalid")
        return

    group = config.GROUPS[choice]

    stop_mode, stop_timestamps = get_stop_mode()
    while stop_mode is None:
        print("Invalid mode")
        stop_mode, stop_timestamps = get_stop_mode()

    result = run_group_with_watchdog(group, stop_mode, stop_timestamps)

    stop_on_display = (
        ", ".join(stop_timestamps)
        if stop_mode == "time_marker"
        else "last scraped post"
    )

    print(f"""
╔══════════════════════════════════════════
║              SCRAPE SUMMARY              
╠══════════════════════════════════════════
║  Group   : {result['group_name'][:40]:<40} ║
╠══════════════════════════════════════════
║  Stop on : {stop_on_display:<24} ║
╠══════════════════════════════════════════
║  Scrolled past : {result['encountered']:<24} 
║  ✅ Saved      : {result['saved']:<24} 
║  ⏭️ Skipped    : {result['skipped']:<24} 
║    ↳ Deduplicated  : {result['skip_dedup']:<21} 
║    ↳ Filter phrase : {result['skip_filter']:<21} 
║    ↳ Blacklisted   : {result['skip_blacklist']:<21} 
║    ↳ No text       : {result['skip_no_text']:<21} 
║  Stalls          : {result['stall_count']:<24} 
║  Terminated      : {'Y' if result.get('terminated', False) else 'N':<24} 
║  Time            : {result['time_seconds']:.1f}s
╚══════════════════════════════════════════
""")

    tracker = result.get("session_blacklist", {})
    if tracker:
        print("\n🚫 BLACKLISTED AUTHORS (this session):")
        lifetime_counts = get_blacklist_counts(tracker.keys())
        sorted_offenders = sorted(tracker.items(), key=lambda x: x[1], reverse=True)
        for author, session_count in sorted_offenders:
            lifetime = lifetime_counts.get(author, 0)
            print(f"   {author}: {session_count} this session, {lifetime} total")


if __name__ == "__main__":
    main()
