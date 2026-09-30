"""Keep Streamlit Community Cloud apps awake.

Opens each app in headless Chromium, clicks the wake button if the app is
asleep, and waits until the real app (inside the /~/+/ iframe) has rendered.
"""
import sys
import time

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

APPS = [
    "https://fabric-aoi-digital-twin-roupnarjtrzs52gtycm6c5.streamlit.app/",
    "https://human-airways-digital-twin-wvmgvehsbnkkpfe3dndrnr.streamlit.app/",
    "https://lcoh-hrs-dashboard-5bfusfd7iwbyzh65nvpt3t.streamlit.app/",
    "https://manufacturing-dt-yqhzjcqffrjz3whfd5jbne.streamlit.app/",
    "https://mit-projects-yuh96eyqnu3gjc5j4xabyq.streamlit.app/",
]

BOOT_TIMEOUT_S = 300  # cold starts can take several minutes
WAKE_SELECTORS = [
    '[data-testid="wakeup-button-viewer"]',
    '[data-testid="wakeup-button-owner"]',
    'button:has-text("get this app back up")',
]


def app_rendered(page) -> bool:
    """True once the Streamlit app itself has rendered inside its iframe."""
    for frame in page.frames:
        if "/~/+/" in frame.url:
            try:
                if frame.locator('[data-testid="stApp"]').count() > 0:
                    return True
            except Exception:
                pass
    return False


def click_wake_button(page) -> bool:
    for sel in WAKE_SELECTORS:
        btn = page.locator(sel)
        if btn.count() > 0 and btn.first.is_visible():
            btn.first.click()
            return True
    return False


def check(browser, url: str) -> str:
    page = browser.new_page()
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=60_000)
        woke = False
        deadline = time.time() + BOOT_TIMEOUT_S
        while time.time() < deadline:
            if app_rendered(page):
                page.wait_for_timeout(5_000)  # dwell so the session registers
                return "WOKEN" if woke else "AWAKE"
            if not woke and click_wake_button(page):
                woke = True
                print(f"  sleep screen found, clicked wake button: {url}")
            page.wait_for_timeout(3_000)
        return "TIMEOUT"
    except PWTimeout:
        return "TIMEOUT"
    except Exception as e:
        return f"ERROR ({type(e).__name__}: {e})"
    finally:
        page.close()


def main() -> int:
    failures = 0
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for url in APPS:
            start = time.time()
            status = check(browser, url)
            print(f"[{time.time() - start:5.1f}s] {status:8} {url}")
            if status not in ("AWAKE", "WOKEN"):
                failures += 1
        browser.close()
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
