# scrape.config.py
import os

# ===================== FILES & PATHS =====================
DEBUG_DIR = "debug_output"
os.makedirs(DEBUG_DIR, exist_ok=True)

AUTH_FILE = "fb_auth.json"
DB_FILE = "posts.db"

# ===================== SCRAPING TIMING ====================
HEARTBEAT_INTERVAL = 30
STUCK_THRESHOLD = 45
SCROLL_PAUSE_MIN = 2
SCROLL_PAUSE_MAX = 4

# ===================== LOGGING =====================
# When True: logs full per-post debug detail (author/text/timestamp extraction)
# for EVERY post, success or fail.
# When False: only logs per-post debug detail for FAILED posts. Successes are
# not logged individually. Group summary is always logged regardless.
VERBOSE_POST_LOG = False

# ===================== PROCESS WATCHDOG =====================
# If a group's scrape subprocess reports no heartbeat for this many seconds,
# the parent process force-kills it and abandons that group.
WATCHDOG_TIMEOUT = 90


# ====================== TIME CONFIG =========================
# STOP_TIMESTAMPS = [
#     "6h",
#     "12h",
#     "1d",
#     "2d",
# ]
def build_stop_list(cutoff_hours):
    stop_list = []
    for h in range(1, 24):
        if h >= cutoff_hours:
            stop_list.append(f"{h}h")
    for d in range(1, 7):
        if d * 24 >= cutoff_hours:
            stop_list.append(f"{d}d")
    for w in range(1, 5):
        if w * 24 * 7 >= cutoff_hours:
            stop_list.append(f"{w}w")
    return stop_list


STOP_TIMESTAMPS = build_stop_list(6)


# ===================== GROUPS ============================
GROUPS = {
    "1": {
        "name": "Owner Only ปล่อยเช่าและขายคอนโดจากเจ้าของโดยตรง",
        "url": "https://www.facebook.com/groups/456957028207473/?sorting_setting=CHRONOLOGICAL",
        "members": "172.2K",
        "type": "Private",
    },
    "2": {
        "name": "Condo Owner ขาย-เช่า คอนโด สำหรับเจ้าของห้องโพสเท่านั้น ห้ามเอเจนท์โพส",
        "url": "https://www.facebook.com/groups/386316227145323/?sorting_setting=CHRONOLOGICAL",
        "members": "130.1K",
        "type": "Public",
    },
    "3": {
        "name": "Owner Post",
        "url": " https://www.facebook.com/groups/owneragentpost/?sorting_setting=CHRONOLOGICAL",
        "members": "112.1K",
        "type": "Public",
    },
    "4": {
        "name": "Owner Post เจ้าของปล่อยเช่าคอนโด 业主出租群",
        "url": "https://www.facebook.com/groups/374078016708868/?sorting_setting=CHRONOLOGICAL ",
        "members": "95.8K",
        "type": "Public",
    },
    ##
    "5": {
        "name": "CONDO & PROPERTY POST BY OWNER",
        "url": "https://www.facebook.com/groups/299716057099018/?sorting_setting=CHRONOLOGICAL_LISTINGS",
        "members": "39.2K",
        "type": "Public",
    },
    "6": {
        "name": "Owner Property Exchange Center เช่า ขายบ้านและคอนโดเฉพาะเจ้าของ",
        "url": "https://www.facebook.com/groups/1243400202881935/?sorting_setting=CHRONOLOGICAL",
        "members": "20.1K",
        "type": "Public",
    },
    "7": {
        "name": "กลุ่มคอนโดฝั่งธนบุรี ใกล้ BTS MRT ท่าพระ ตลาดพลู เพชรเกษม บางแค จรัญฯ",
        "url": "https://www.facebook.com/groups/3397058930622540/?sorting_setting=CHRONOLOGICAL",
        "members": "36.3K",
        "type": "Public",
    },
    "8": {
        "name": "ขาย/ ให้เช่า คอนโด หอพัก ย่าน จรัญฯ ปิ่นเกล้า บางพลัด อิสรภาพ",
        "url": "https://www.facebook.com/groups/176633257654992/?sorting_setting=CHRONOLOGICAL",
        "members": "75.9K",
        "type": "Public",
    },
    "9": {
        "name": "ปล่อยเช่าคอนโดทองหล่อ เอกมัย พัฒนาการ",
        "url": "https://www.facebook.com/groups/1093329418325871/?sorting_setting=CHRONOLOGICAL",
        "members": "6.3K",
        "type": "Public",
    },
    ##
    "10": {
        "name": "คอนโดให้เช่าฝั่งธน ใกล้ BTS MRT บางแค บางหว้า ตลาดพลู วุฒากาศ วงเวียนใหญ่",
        "url": "https://www.facebook.com/groups/388594476619201/?sorting_setting=CHRONOLOGICAL",
        "members": "91.8K",
        "type": "Public",
    },
    "11": {
        "name": "Owner Only ขาย/ให้เช่า คอนโด จรัญฯ ปิ่นเกล้า บางพลัด อิสรภาพ",
        "url": "https://www.facebook.com/groups/281453768148509/?sorting_setting=CHRONOLOGICAL",
        "members": "7.K",
        "type": "Public",
    },
    "12": {
        "name": "Owner Post ซื้อ ขาย เช่า คอนโด | สำหรับเจ้าของห้องโพสเท่านั้น | Condominium",
        "url": "https://www.facebook.com/groups/ownerpost/?sorting_setting=CHRONOLOGICAL",
        "members": "13.4K",
        "type": "Public",
    },
    "13": {
        "name": "แหล่งรวมคอนโด บ้าน หอพัก ย่านอารีย์ BTSอารีย์",
        "url": "https://www.facebook.com/groups/174635590974549/?sorting_setting=CHRONOLOGICAL",
        "members": "13.K",
        "type": "Public",
    },
    "14": {
        "name": "Owner Please ปล่อยเช่า และขายคอนโด จากเจ้าของโดยตรง",
        "url": "https://www.facebook.com/groups/510167383417215/?sorting_setting=CHRONOLOGICAL",
        "members": "34.4K",
        "type": "Private",
    },
    "15": {
        "name": "OWNER ปล่อยขายปล่อยเช่า ลูกค้าหาห้องพัก/AgentหาStock",
        "url": "https://www.facebook.com/groups/5237873106310208/?sorting_setting=CHRONOLOGICAL",
        "members": "23.2K",
        "type": "Private",
    },
}
# june 25
# "7": {
#     "name": "Bangkok Expats - Condos & Houses For Rent Group",
#     "url": "https://www.facebook.com/groups/1046291836187649/?sorting_setting=CHRONOLOGICAL_LISTINGS",
#     "members": "47.6K",
#     "type": "Public",
# },

# "5": {
#     "name": "Owner Only ปล่อยเช่า ขาย คอนโด จากเจ้าของห้องโดยตรง",
#     "url": "https://www.facebook.com/groups/owneronly/?sorting_setting=CHRONOLOGICAL",
#     "members": "76.4K",
#     "type": "Public",
# },
