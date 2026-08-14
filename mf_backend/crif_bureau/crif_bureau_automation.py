"""
consent_automate.py
--------------------
Page 1: Check all checkboxes → Click "Check my CRIF Score"
Page 2: Click "Share crif Report" → Wait for processing → Confirm success

Handles:
  - URL fails to load / timeout
  - URL unauthorised (403 / login redirect)
  - Consent URL expired

Usage:
    python consent_automate.py https://snz.bz/SIGNZY/UmzrwL
    python consent_automate.py https://snz.bz/SIGNZY/UmzrwL --headless

Install:
    pip install playwright
    playwright install chromium
"""

import sys

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
except ImportError:
    print("Run: pip install playwright && playwright install chromium")
    sys.exit(1)

SUCCESS_URL = "https://underwriting-preproduction.signzy.app/bureau-portal/success"

# Keywords that indicate an expired or unauthorised page
EXPIRED_KEYWORDS  = ["expired", "link has expired", "no longer valid", "invalid link", "session expired"]
UNAUTH_KEYWORDS   = ["unauthorised", "unauthorized", "access denied", "forbidden", "not allowed", "login"]


def bail(reason: str):
    """Print a clear error and exit with code 1."""
    print(f"\n✗ Error: {reason}")
    print("  Automation stopped.")
    sys.exit(1)


def wait_ready(page):
    try:
        page.wait_for_load_state("networkidle", timeout=15_000)
    except PWTimeout:
        page.wait_for_timeout(3000)


def check_page_validity(page, label: str):
    """
    After loading a page, inspect its HTTP status, URL, and content
    to detect expired / unauthorised / error states.
    """
    url   = page.url
    title = page.title().lower()
    body  = page.locator("body").inner_text().lower()

    # HTTP error codes caught via URL patterns or title
    if "404" in title or "page not found" in title:
        bail(f"{label} — Page not found (404): {url}")

    if "500" in title or "server error" in title:
        bail(f"{label} — Server error (500): {url}")

    # Expired link detection
    for kw in EXPIRED_KEYWORDS:
        if kw in body or kw in title:
            bail(f"{label} — Consent URL has expired: {url}")

    # Unauthorised / login wall detection
    for kw in UNAUTH_KEYWORDS:
        if kw in body or kw in title:
            bail(f"{label} — Unauthorised access: {url}")


def automate(start_url: str, headless: bool = True):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page    = context.new_page()

        # ── PAGE 1: Consent ────────────────────────────────────────────────
        print(f"\nStep 1 — Opening: {start_url}")
        try:
            page.goto(start_url, wait_until="domcontentloaded", timeout=30_000)
            wait_ready(page)
        except PWTimeout:
            bail(f"Page failed to load (timeout): {start_url}")
        except Exception as e:
            bail(f"Failed to open URL: {e}")

        print(f"         Loaded:  {page.url}")
        check_page_validity(page, "Page 1 (Consent)")

        # Check all checkboxes
        try:
            page.wait_for_selector("input[type='checkbox']", timeout=10_000)
        except PWTimeout:
            bail("Consent page loaded but no checkboxes found — page may have changed.")

        checkboxes = page.locator("input[type='checkbox']")
        print(f"         Checkboxes found: {checkboxes.count()}")
        for i in range(checkboxes.count()):
            cb = checkboxes.nth(i)
            if not cb.is_checked():
                cb.check()
                print(f"           ✓ Checked checkbox {i + 1}")

        # Click "Check my CRIF Score"
        try:
            btn1 = page.get_by_role("button", name="Check my CRIF Score")
            btn1.wait_for(timeout=10_000)
            btn1.click()
            print("         Clicked: 'Check my CRIF Score'")
        except PWTimeout:
            bail("'Check my CRIF Score' button not found on consent page.")

        # ── PAGE 2: Score ──────────────────────────────────────────────────
        print(f"\nStep 2 — Waiting for score page...")
        try:
            page.wait_for_timeout(2000)
            page2 = context.pages[-1]
            wait_ready(page2)
        except Exception as e:
            bail(f"Score page failed to load: {e}")

        print(f"         Loaded:  {page2.url}")
        check_page_validity(page2, "Page 2 (Score)")

        # Click "Share crif Report"
        try:
            btn2 = page2.get_by_role("button", name="Share crif Report")
            btn2.wait_for(timeout=10_000)
            btn2.click()
            print("         Clicked: 'Share crif Report'")
        except PWTimeout:
            bail("'Share crif Report' button not found on score page.")

        # ── Wait for processing (Sharing...) ──────────────────────────────
        print(f"\nStep 3 — Processing...")
        try:
            page2.wait_for_selector("button:has-text('Sharing...')", timeout=5_000)
            print("         Status: Sharing...")
            page2.wait_for_selector(
                "button:has-text('Sharing...')",
                state="hidden",
                timeout=30_000
            )
        except PWTimeout:
            try:
                page2.wait_for_load_state("networkidle", timeout=30_000)
            except PWTimeout:
                bail("Sharing timed out — server may be unavailable or report generation failed.")

        # ── Wait for success page ──────────────────────────────────────────
        print(f"\nStep 4 — Waiting for success redirect...")
        try:
            page2.wait_for_url(SUCCESS_URL, timeout=15_000)
        except PWTimeout:
            final_url = page2.url
            if final_url != SUCCESS_URL:
                bail(
                    f"Did not reach success page.\n"
                    f"  Expected : {SUCCESS_URL}\n"
                    f"  Got      : {final_url}"
                )

        print(f"         ✓ Success! {page2.url}")
        browser.close()


if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description="Automate checkbox + submit on any URL.")
    # parser.add_argument("url", help="Target URL to automate")
    # parser.add_argument("--headless", action="store_true", help="Run without browser window")
    # args = parser.parse_args()

    #automate("https://snz.bz/SIGNZY/UmzrwL", headless=True)
    automate("https://snz.bz/SIGNZY/wJdKi_", headless=False)