"""
Feed validator — test all ASX RSS feeds and report health
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import requests
import feedparser
import logging
from typing import Dict, List

from config import ASX_FEEDS, SCRAPER_CONFIG

logger = logging.getLogger(__name__)


class FeedValidator:

    def test_feed(self, company: str, url: str) -> Dict:
        result = {"company": company, "url": url, "status": "unknown", "entries": 0, "error": None}

        if not url or "wisetechglobal" in url:
            result["status"] = "skip"
            result["error"] = "Non-RSS feed (Playwright fallback)"
            return result

        try:
            head = requests.head(url, timeout=SCRAPER_CONFIG["rss_timeout"], allow_redirects=True)
            if head.status_code >= 400:
                result["status"] = "http_error"
                result["error"] = f"HTTP {head.status_code}"
                return result
        except requests.exceptions.RequestException as e:
            result["status"] = "unreachable"
            result["error"] = str(e)
            return result

        feed = feedparser.parse(url)
        if feed.bozo and not feed.entries:
            result["status"] = "parse_error"
            result["error"] = str(feed.bozo_exception)
            return result

        result["entries"] = len(feed.entries)
        result["status"] = "ok" if feed.entries else "empty"
        return result

    def run(self) -> List[Dict]:
        results = []
        ok = skip = error = empty = 0

        print(f"\nValidating {len(ASX_FEEDS)} ASX feeds...\n")
        print(f"{'Company':<30} {'Status':<12} {'Entries':>8}  Notes")
        print("-" * 70)

        for company, cfg in ASX_FEEDS.items():
            r = self.test_feed(company, cfg.get("feed", ""))
            results.append(r)

            status = r["status"]
            icon = {"ok": "✓", "empty": "○", "skip": "→", "http_error": "✗", "unreachable": "✗", "parse_error": "✗"}.get(status, "?")
            note = r["error"] or ""
            print(f"{icon} {company:<28} {status:<12} {r['entries']:>8}  {note}")

            if status == "ok":
                ok += 1
            elif status == "skip":
                skip += 1
            elif status == "empty":
                empty += 1
            else:
                error += 1

        print("-" * 70)
        print(f"\nSummary: {ok} ok · {empty} empty · {skip} skipped · {error} errors\n")
        return results
