"""
consent_automate.py
--------------------
Page 1: Check all checkboxes → Click "Check my CRIF Score"
Page 2: Extract CRIF score → Click "Share crif Report" → Wait for success

Returns:
    dict  { "success": True, "crif_score": 742, "final_url": "..." }
    dict  { "success": False, "error": "reason..." }

Usage as script:
    python consent_automate.py https://snz.bz/SIGNZY/UmzrwL
    python consent_automate.py https://snz.bz/SIGNZY/UmzrwL --headless

Usage from Django view:
    from consent_automate import automate
    result = automate("https://snz.bz/SIGNZY/UmzrwL", headless=True)
    # result["crif_score"] → 742

Install:
    pip install playwright
    playwright install chromium
"""

import sys
import argparse
from typing import Optional

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
except ImportError:
    print("Run: pip install playwright && playwright install chromium")
    sys.exit(1)

SUCCESS_URL      = "https://underwriting-preproduction.signzy.app/bureau-portal/success"
EXPIRED_KEYWORDS = ["expired", "link has expired", "no longer valid", "invalid link", "session expired"]
UNAUTH_KEYWORDS  = ["unauthorised", "unauthorized", "access denied", "forbidden", "not allowed", "login"]


# ── Helpers ────────────────────────────────────────────────────────────────

def error(reason: str) -> dict:
    """Return a failure dict (used when called from Django)."""
    return {"success": False, "crif_score": None, "error": reason}


def wait_ready(page):
    try:
        page.wait_for_load_state("networkidle", timeout=15_000)
    except PWTimeout:
        page.wait_for_timeout(3000)


def check_page_validity(page, label: str):
    """Raise ValueError if page looks expired / unauthorised / broken."""
    title = page.title().lower()
    body  = page.locator("body").inner_text().lower()

    if "404" in title or "page not found" in title:
        raise ValueError(f"{label} — Page not found (404): {page.url}")
    if "500" in title or "server error" in title:
        raise ValueError(f"{label} — Server error (500): {page.url}")
    for kw in EXPIRED_KEYWORDS:
        if kw in body or kw in title:
            raise ValueError(f"{label} — Consent URL has expired: {page.url}")
    for kw in UNAUTH_KEYWORDS:
        if kw in body or kw in title:
            raise ValueError(f"{label} — Unauthorised access: {page.url}")


def extract_crif_score(page) -> Optional[int]:
    """
    Extract score from <span class="text-4xl font-bold">742</span>
    Returns int score or None if not found.
    """
    try:
        # Wait for score element to appear
        page.wait_for_selector("span.text-4xl.font-bold", timeout=10_000)
        score_text = page.locator("span.text-4xl.font-bold").first.inner_text().strip()
        return int(score_text)
    except (PWTimeout, ValueError):
        return None


# ── Main automation ────────────────────────────────────────────────────────

def automate(start_url: str, headless: bool = True, expected_redirect_url: str = None) -> dict:
    """
    Run the full consent → score → share flow.
    Always returns a dict — never raises.
    """
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless)
            context = browser.new_context(viewport={"width": 1280, "height": 900})
            page    = context.new_page()

            # ── PAGE 1: Consent ────────────────────────────────────────────
            print(f"\nStep 1 — Opening: {start_url}")
            try:
                page.goto(start_url, wait_until="domcontentloaded", timeout=30_000)
                wait_ready(page)
            except PWTimeout:
                return error(f"Page failed to load (timeout): {start_url}")
            except Exception as e:
                return error(f"Failed to open URL: {e}")

            print(f"         Loaded : {page.url}")
            check_page_validity(page, "Page 1 (Consent)")

            # Check all checkboxes
            try:
                page.wait_for_selector("input[type='checkbox']", timeout=10_000)
            except PWTimeout:
                return error("Consent page loaded but no checkboxes found.")

            checkboxes = page.locator("input[type='checkbox']")
            print(f"         Checkboxes: {checkboxes.count()} found")
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
                return error("'Check my CRIF Score' button not found.")

            # ── PAGE 2: Score ──────────────────────────────────────────────
            print(f"\nStep 2 — Waiting for score page...")
            try:
                page.wait_for_timeout(2000)
                page2 = context.pages[-1]
                wait_ready(page2)
            except Exception as e:
                return error(f"Score page failed to load: {e}")

            print(f"         Loaded : {page2.url}")
            check_page_validity(page2, "Page 2 (Score)")

            # ── Extract CRIF score ─────────────────────────────────────────
            print(f"\nStep 3 — Extracting CRIF score...")
            crif_score = extract_crif_score(page2)
            if crif_score is None:
                return error("CRIF score element not found on score page.")
            print(f"         Score  : {crif_score}")

            # ── Click "Share crif Report" ──────────────────────────────────
            print(f"\nStep 4 — Sharing report...")
            try:
                btn2 = page2.get_by_role("button", name="Share crif Report")
                btn2.wait_for(timeout=10_000)
                btn2.click()
                print("         Clicked: 'Share crif Report'")
            except PWTimeout:
                return error("'Share crif Report' button not found.")

            # Wait for "Sharing..." processing to finish
            try:
                page2.wait_for_selector("button:has-text('Sharing...')", timeout=5_000)
                print("         Status : Sharing...")
                page2.wait_for_selector(
                    "button:has-text('Sharing...')",
                    state="hidden",
                    timeout=30_000,
                )
            except PWTimeout:
                try:
                    page2.wait_for_load_state("networkidle", timeout=30_000)
                except PWTimeout:
                    return error("Sharing timed out — server may be unavailable.")

            # ── Wait for success redirect ──────────────────────────────────
            print(f"\nStep 5 — Waiting for success redirect...")
            expected_urls = [SUCCESS_URL]
            if expected_redirect_url:
                expected_urls.append(expected_redirect_url.rstrip("/"))

            try:
                page2.wait_for_url(SUCCESS_URL, timeout=15_000)
            except PWTimeout:
                final_url_base = page2.url.rstrip("/")
                reached_expected_url = any(final_url_base.startswith(url) for url in expected_urls)
                if not reached_expected_url:
                    return error(
                        f"Did not reach success page.\n"
                        f"  Expected : {', '.join(expected_urls)}\n"
                        f"  Got      : {page2.url}"
                    )

            final_url = page2.url
            print(f"         ✓ Success! {final_url}")
            browser.close()

            return {
                "success":    True,
                "crif_score": crif_score,
                "final_url":  final_url,
                "error":      None,
            }

    except ValueError as e:
        return error(str(e))
    except Exception as e:
        return error(f"Unexpected error: {e}")


# ── Django view example ────────────────────────────────────────────────────
#
# from django.http import JsonResponse
# from django.views import View
# from .consent_automate import automate
#
# class CrifScoreView(View):
#     def post(self, request):
#         url    = request.POST.get("url") or "https://snz.bz/SIGNZY/UmzrwL"
#         result = automate(url, headless=True)
#         status = 200 if result["success"] else 500
#         return JsonResponse(result, status=status)


# ── CLI entry point ────────────────────────────────────────────────────────

if __name__ == "__main__":
    # parser = argparse.ArgumentParser()
    # parser.add_argument("url", help="Consent URL to automate")
    # parser.add_argument("--headless", action="store_true")
    # args = parser.parse_args()
    result = automate("https://snz.bz/SIGNZY/V1Qxjb", headless=False)
    #result = automate(args.url, headless=args.headless)

    print("\n── Result ──────────────────────────────")
    if result["success"]:
        print(f"  ✓ CRIF Score : {result['crif_score']}")
        print(f"  ✓ Final URL  : {result['final_url']}")
    else:
        print(f"  ✗ Error      : {result['error']}")
    print("────────────────────────────────────────\n")
