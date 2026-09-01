# scrape/browser.py
import time
import random
import threading

from playwright.sync_api import sync_playwright

import scrape.config as config


# ===================== FREEZE MONITOR =====================
class FreezeMonitor:
    def __init__(
        self,
        heartbeat_interval=config.HEARTBEAT_INTERVAL,
        stuck_threshold=config.STUCK_THRESHOLD,
        shared_heartbeat=None,
        lock=None,  # FIXED: add lock parameter
    ):
        self._last_activity = time.time()
        self._stop_event = threading.Event()
        self._frozen = threading.Event()
        self._thread = None
        self.heartbeat_interval = heartbeat_interval
        self.stuck_threshold = stuck_threshold
        self.shared_heartbeat = shared_heartbeat
        self.lock = lock

    def touch(self):
        self._last_activity = time.time()
        if self.shared_heartbeat is not None and self.lock is not None:
            try:
                with self.lock:
                    self.shared_heartbeat.value = self._last_activity
            except Exception:
                pass
        elif self.shared_heartbeat is not None:
            # Fallback without lock (less safe)
            try:
                self.shared_heartbeat.value = self._last_activity
            except Exception:
                pass

    @property
    def is_frozen(self):
        return self._frozen.is_set()

    def _monitor_loop(self):
        while not self._stop_event.is_set():
            time.sleep(self.heartbeat_interval)
            if self._stop_event.is_set():
                break
            stuck_for = time.time() - self._last_activity
            if stuck_for > self.stuck_threshold:
                self._frozen.set()
                print(
                    f"[FREEZE DETECTED] No activity for {stuck_for:.0f}s. "
                    "Abandoning current group."
                )
                self._stop_event.set()
                break

    def start(self):
        self._stop_event.clear()
        self._frozen.clear()
        self._last_activity = time.time()
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2)


# ===================== HUMAN BEHAVIOUR ====================
def human_mouse_move(page, start_x, start_y, target_x, target_y):
    distance = ((target_x - start_x) ** 2 + (target_y - start_y) ** 2) ** 0.5
    steps = max(5, min(25, int(distance / 30) + random.randint(-3, 5)))
    steps = max(5, steps)
    page.mouse.move(target_x, target_y, steps=steps)
    time.sleep(random.uniform(0.02, 0.08))
    if random.random() < 0.2:
        overshoot_x = target_x + random.randint(-15, 15)
        overshoot_y = target_y + random.randint(-15, 15)
        page.mouse.move(overshoot_x, overshoot_y, steps=random.randint(3, 7))
        time.sleep(random.uniform(0.01, 0.04))
        page.mouse.move(target_x, target_y, steps=random.randint(3, 7))
    return target_x, target_y


def jiggle(page, cursor_x, cursor_y):
    t0 = time.time()
    viewport = page.viewport_size
    if not viewport:
        return cursor_x, cursor_y
    target_x = random.randint(100, viewport["width"] - 100)
    target_y = random.randint(100, viewport["height"] - 100)
    cursor_x, cursor_y = human_mouse_move(page, cursor_x, cursor_y, target_x, target_y)
    delta = random.choice([-1, 1]) * random.randint(50, 80)
    page.evaluate(f"window.scrollBy(0, {delta})")
    time.sleep(random.uniform(0.1, 0.3))
    elapsed = time.time() - t0
    if elapsed > 5:
        print(f"  ⚠️ jiggle() took {elapsed:.1f}s (slower than expected)")
    return cursor_x, cursor_y


def recover_stall(page, cursor_x, cursor_y):
    t0 = time.time()
    viewport = page.viewport_size
    if not viewport:
        return cursor_x, cursor_y
    height = viewport["height"]
    cursor_x, cursor_y = human_mouse_move(
        page, cursor_x, cursor_y, random.randint(100, 300), random.randint(100, 300)
    )
    up = random.randint(int(height * 0.3), int(height * 0.5))
    page.evaluate(f"window.scrollBy(0, -{up})")
    time.sleep(random.uniform(1.0, 2.5))
    cursor_x, cursor_y = human_mouse_move(
        page, cursor_x, cursor_y, random.randint(800, 1100), random.randint(400, 700)
    )
    down = random.randint(int(height * 0.4), int(height * 0.6))
    page.evaluate(f"window.scrollBy(0, {down})")
    time.sleep(random.uniform(0.8, 1.8))
    cursor_x, cursor_y = human_mouse_move(
        page, cursor_x, cursor_y, random.randint(200, 900), random.randint(100, 700)
    )
    elapsed = time.time() - t0
    if elapsed > 10:
        print(f"  ⚠️ recover_stall() took {elapsed:.1f}s (slower than expected)")
    return cursor_x, cursor_y


def launch_browser():
    """Returns (playwright_instance, browser, page). Caller must clean up."""
    p = sync_playwright().start()
    browser = p.chromium.launch(
        headless=False,
        args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
    )
    context = browser.new_context(
        storage_state=config.AUTH_FILE, viewport={"width": 1280, "height": 900}
    )
    context.add_init_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined}); window.chrome = { runtime: {} };"
    )
    page = context.new_page()
    return p, browser, page
