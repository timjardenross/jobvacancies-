"""
Main ASX Job Scraper
Fetches RSS feeds, scores by relevance, stores in Supabase
"""
import feedparser
import logging
from datetime import datetime
from typing import List, Dict
import asyncio
from playwright.async_api import async_playwright
import requests

from config import (
    ASX_FEEDS, KEYWORDS_INCLUDE, KEYWORDS_EXCLUDE,
    RELEVANCE_SCORING, PRIORITY_COMPANIES, SCRAPER_CONFIG,
    LOGGING_CONFIG
)

# Setup logging
logging.basicConfig(
    level=LOGGING_CONFIG['level'],
    format=LOGGING_CONFIG['format'],
    handlers=[
        logging.FileHandler(LOGGING_CONFIG['log_file']),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ASXJobScraper:
    """Main scraper orchestration"""
    
    def __init__(self, db_client):
        self.db = db_client
        self.jobs = []
        self.stats = {
            'rss_fetched': 0,
            'rss_jobs': 0,
            'rss_errors': 0,
            'playwright_jobs': 0,
            'playwright_errors': 0,
            'total_scored': 0,
            'jobs_included': 0,
        }
    
    def score_job(self, job: Dict) -> int:
        """
        Calculate relevance score for a job
        Range: 0-100
        """
        title = (job.get('title', '') or '').lower()
        description = (job.get('description', '') or '').lower()
        company = job.get('company', '')
        
        score = 0
        
        # Check exclusions first (hard stop)
        for keyword in KEYWORDS_EXCLUDE:
            if keyword.lower() in title:
                logger.debug(f"Excluding {job.get('title')}: contains '{keyword}'")
                return -50  # Negative score = exclude
        
        # Check inclusions
        for keyword in KEYWORDS_INCLUDE:
            if keyword.lower() in title:
                score += RELEVANCE_SCORING['keyword_in_title']
            elif keyword.lower() in description:
                score += RELEVANCE_SCORING['keyword_in_description']
        
        # Priority company bonus
        if company in PRIORITY_COMPANIES:
            score += RELEVANCE_SCORING['priority_company_bonus']
        
        # Clamp score
        score = max(RELEVANCE_SCORING['minimum_score'], 
                   min(score, RELEVANCE_SCORING['maximum_score']))
        
        return score
    
    async def fetch_rss_feeds(self) -> List[Dict]:
        """Fetch all RSS feeds asynchronously"""
        logger.info(f"Starting RSS feed fetch for {len(ASX_FEEDS)} companies...")
        jobs = []
        
        for company, config in ASX_FEEDS.items():
            try:
                feed_url = config.get('feed', '')
                if not feed_url or 'wisetechglobal' in feed_url:
                    # Skip non-RSS feeds
                    logger.debug(f"Skipping non-RSS feed for {company}")
                    continue
                
                logger.debug(f"Fetching RSS: {company}")
                feed = feedparser.parse(feed_url)
                
                if feed.bozo and isinstance(feed.bozo_exception, Exception):
                    logger.warning(f"RSS parse error for {company}: {feed.bozo_exception}")
                    self.stats['rss_errors'] += 1
                    continue
                
                entries_count = len(feed.entries[:SCRAPER_CONFIG['max_jobs_per_company']])
                
                for entry in feed.entries[:SCRAPER_CONFIG['max_jobs_per_company']]:
                    job = {
                        'company': company,
                        'title': entry.get('title', 'No title'),
                        'url': entry.get('link', ''),
                        'description': entry.get('summary', ''),
                        'posted_date': entry.get('published', datetime.now().isoformat()),
                        'source': 'RSS',
                        'sector': config.get('sector', ''),
                    }
                    
                    if job['url']:  # Only include if URL exists
                        jobs.append(job)
                
                self.stats['rss_fetched'] += 1
                self.stats['rss_jobs'] += entries_count
                logger.info(f"✓ {company}: {entries_count} jobs")
                
            except Exception as e:
                logger.error(f"✗ RSS error for {company}: {str(e)}")
                self.stats['rss_errors'] += 1
        
        return jobs
    
    async def scrape_fallback_pages(self) -> List[Dict]:
        """
        Fallback: Scrape career pages for companies without RSS feeds
        Used for WiseTech and others
        """
        logger.info("Starting fallback page scraping...")
        jobs = []
        
        # WiseTech Global (known custom portal)
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page()
                
                # Scrape WiseTech
                logger.debug("Scraping WiseTech Global...")
                await page.goto('https://www.wisetechglobal.com/careers/current-openings/', 
                               timeout=SCRAPER_CONFIG['playwright_timeout'] * 1000)
                
                # Wait for job cards to load
                try:
                    await page.wait_for_selector('[data-test="job-card"]', timeout=5000)
                    job_cards = await page.query_selector_all('[data-test="job-card"]')
                    
                    for card in job_cards:
                        try:
                            title_elem = await card.query_selector('h3, [data-test="job-title"]')
                            link_elem = await card.query_selector('a')
                            
                            if title_elem and link_elem:
                                title = await title_elem.text_content()
                                url = await link_elem.get_attribute('href')
                                
                                if url and not url.startswith('http'):
                                    url = 'https://www.wisetechglobal.com' + url
                                
                                job = {
                                    'company': 'WiseTech Global',
                                    'title': title.strip(),
                                    'url': url,
                                    'description': '',
                                    'posted_date': datetime.now().isoformat(),
                                    'source': 'Playwright',
                                    'sector': 'Information Technology',
                                }
                                jobs.append(job)
                        except Exception as e:
                            logger.debug(f"Error parsing WiseTech job card: {e}")
                    
                    self.stats['playwright_jobs'] += len(job_cards)
                    logger.info(f"✓ WiseTech Global: {len(job_cards)} jobs")
                    
                except Exception as e:
                    logger.warning(f"WiseTech page timeout: {e}")
                    self.stats['playwright_errors'] += 1
                
                await browser.close()
        
        except Exception as e:
            logger.error(f"✗ Playwright error: {str(e)}")
            self.stats['playwright_errors'] += 1
        
        return jobs
    
    def filter_and_rank(self, jobs: List[Dict]) -> List[Dict]:
        """Score, filter, and sort jobs by relevance"""
        logger.info(f"Scoring {len(jobs)} jobs...")
        
        scored_jobs = []
        for job in jobs:
            score = self.score_job(job)
            
            # Include jobs with score > 0 (and not excluded)
            if score > RELEVANCE_SCORING['minimum_score']:
                job['relevance_score'] = score
                scored_jobs.append(job)
            
            self.stats['total_scored'] += 1
        
        # Sort by score descending
        scored_jobs.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        self.stats['jobs_included'] = len(scored_jobs)
        logger.info(f"Included {len(scored_jobs)} jobs after scoring")
        
        return scored_jobs
    
    async def run(self) -> List[Dict]:
        """Main orchestration"""
        logger.info("=" * 60)
        logger.info("ASX JOB SCRAPER STARTED")
        logger.info("=" * 60)
        
        # Fetch RSS feeds
        rss_jobs = await self.fetch_rss_feeds()
        
        # Fallback scraping
        fallback_jobs = await self.scrape_fallback_pages()
        
        # Combine and deduplicate by URL
        all_jobs = rss_jobs + fallback_jobs
        seen_urls = set()
        deduped_jobs = []
        
        for job in all_jobs:
            if job['url'] not in seen_urls:
                deduped_jobs.append(job)
                seen_urls.add(job['url'])
        
        logger.info(f"Total jobs after dedup: {len(deduped_jobs)}")
        
        # Score and filter
        scored_jobs = self.filter_and_rank(deduped_jobs)
        
        # Store in database
        if scored_jobs:
            logger.info(f"Inserting {len(scored_jobs)} jobs into database...")
            new_jobs = self.db.insert_jobs(scored_jobs)
            logger.info(f"✓ Inserted {len(new_jobs)} new jobs")
        else:
            logger.warning("No jobs to insert")
            new_jobs = []
        
        # Log stats
        logger.info("=" * 60)
        logger.info("SCRAPER STATS")
        logger.info("=" * 60)
        for key, value in self.stats.items():
            logger.info(f"{key}: {value}")
        logger.info("=" * 60)
        
        return new_jobs


async def run_scraper(db_client):
    """Async entry point"""
    scraper = ASXJobScraper(db_client)
    return await scraper.run()


if __name__ == '__main__':
    # For testing: python -m src.scraper
    from database import SupabaseClient
    
    db = SupabaseClient()
    new_jobs = asyncio.run(run_scraper(db))
    
    print(f"\n✓ Scrape complete. Found {len(new_jobs)} new jobs.")
