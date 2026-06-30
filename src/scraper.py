"""
ASX Job Scraper — uses Adzuna Australia API (reliable, no bot protection)
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import requests
import logging
import asyncio
from datetime import datetime
from typing import List, Dict

from config import (
    KEYWORDS_INCLUDE, KEYWORDS_EXCLUDE,
    RELEVANCE_SCORING, PRIORITY_COMPANIES, SCRAPER_CONFIG,
    LOGGING_CONFIG
)

logging.basicConfig(
    level=LOGGING_CONFIG['level'],
    format=LOGGING_CONFIG['format'],
    handlers=[
        logging.FileHandler(LOGGING_CONFIG['log_file']),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

ADZUNA_APP_ID  = os.getenv('ADZUNA_APP_ID', '')
ADZUNA_APP_KEY = os.getenv('ADZUNA_APP_KEY', '')
ADZUNA_BASE    = 'https://api.adzuna.com/v1/api/jobs/au/search/1'

# One search per keyword — Adzuna returns up to 50 results per call
SEARCH_QUERIES = [
    'business resilience',
    'customer success',
    'service delivery manager',
    'business continuity',
    'operational resilience',
    'customer experience manager',
    'crisis management',
]


class ASXJobScraper:

    def __init__(self, db_client):
        self.db = db_client
        self.stats = {
            'queries_run': 0,
            'queries_error': 0,
            'total_jobs_raw': 0,
            'jobs_included': 0,
        }

    def score_job(self, job: Dict) -> int:
        title       = (job.get('title', '') or '').lower()
        description = (job.get('description', '') or '').lower()
        company     = job.get('company', '')

        for kw in KEYWORDS_EXCLUDE:
            if kw.lower() in title:
                return -50

        score = 0
        for kw in KEYWORDS_INCLUDE:
            if kw.lower() in title:
                score += RELEVANCE_SCORING['keyword_in_title']
            elif kw.lower() in description:
                score += RELEVANCE_SCORING['keyword_in_description']

        company_lower = company.lower()
        for asx_name in PRIORITY_COMPANIES:
            if asx_name.lower() in company_lower or company_lower in asx_name.lower():
                score += RELEVANCE_SCORING['priority_company_bonus']
                break

        return max(0, min(score, RELEVANCE_SCORING['maximum_score']))

    def fetch_adzuna(self) -> List[Dict]:
        if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
            logger.error('ADZUNA_APP_ID and ADZUNA_APP_KEY not set — check .env or GitHub secrets')
            return []

        jobs = []
        for query in SEARCH_QUERIES:
            try:
                params = {
                    'app_id':          ADZUNA_APP_ID,
                    'app_key':         ADZUNA_APP_KEY,
                    'results_per_page': 50,
                    'what':            query,
                    'where':           'australia',
                    'max_days_old':    1,
                    'sort_by':         'date',
                    'content-type':    'application/json',
                }
                r = requests.get(ADZUNA_BASE, params=params, timeout=SCRAPER_CONFIG['rss_timeout'])
                r.raise_for_status()
                data = r.json()
                results = data.get('results', [])
                logger.info(f"✓ Adzuna '{query}': {len(results)} results")
                self.stats['queries_run'] += 1

                for item in results:
                    job = {
                        'company':     item.get('company', {}).get('display_name', 'Unknown'),
                        'title':       item.get('title', 'No title'),
                        'url':         item.get('redirect_url', ''),
                        'description': item.get('description', ''),
                        'posted_date': item.get('created', datetime.now().isoformat()),
                        'source':      f'Adzuna:{query}',
                        'sector':      item.get('category', {}).get('label', ''),
                    }
                    if job['url']:
                        jobs.append(job)

                self.stats['total_jobs_raw'] += len(results)

            except Exception as e:
                logger.error(f"✗ Adzuna error for '{query}': {e}")
                self.stats['queries_error'] += 1

        return jobs

    def filter_and_rank(self, jobs: List[Dict]) -> List[Dict]:
        logger.info(f"Scoring {len(jobs)} jobs...")
        scored = []
        for job in jobs:
            score = self.score_job(job)
            if score > 0:
                job['relevance_score'] = score
                scored.append(job)

        scored.sort(key=lambda j: j.get('relevance_score', 0), reverse=True)
        self.stats['jobs_included'] = len(scored)
        logger.info(f"Included {len(scored)} jobs after scoring")
        return scored

    async def run(self) -> List[Dict]:
        logger.info("=" * 60)
        logger.info("ASX JOB SCRAPER STARTED (Adzuna API)")
        logger.info("=" * 60)

        raw_jobs = self.fetch_adzuna()

        # Deduplicate by URL
        seen, deduped = set(), []
        for job in raw_jobs:
            if job['url'] not in seen:
                deduped.append(job)
                seen.add(job['url'])
        logger.info(f"Unique jobs after dedup: {len(deduped)}")

        scored_jobs = self.filter_and_rank(deduped)

        if scored_jobs:
            logger.info(f"Inserting {len(scored_jobs)} jobs...")
            new_jobs = self.db.insert_jobs(scored_jobs)
            logger.info(f"✓ Inserted {len(new_jobs)} new jobs")
        else:
            logger.warning("No jobs matched scoring criteria")
            new_jobs = []

        logger.info("=" * 60)
        for k, v in self.stats.items():
            logger.info(f"  {k}: {v}")
        logger.info("=" * 60)

        return new_jobs


async def run_scraper(db_client):
    scraper = ASXJobScraper(db_client)
    return await scraper.run()


if __name__ == '__main__':
    from database import SupabaseClient
    db = SupabaseClient()
    import asyncio
    new_jobs = asyncio.run(run_scraper(db))
    print(f"\n✓ Scrape complete. Found {len(new_jobs)} new jobs.")
