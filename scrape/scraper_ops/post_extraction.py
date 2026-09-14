import re
import time
from scrape.scraper_ops.DebugLogger import debug

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
