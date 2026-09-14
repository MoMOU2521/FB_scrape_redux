# scrape/scraper_ops.DebugLogger.py
import os
from datetime import datetime

import scrape.config as config


class DebugLogger:
    def __init__(self, debug_dir):
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
