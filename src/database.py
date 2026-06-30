"""
Supabase Database Client
Handle all database operations (insert, query, bookmark)
"""
import logging
from datetime import datetime
from typing import List, Dict, Optional

try:
    from supabase import create_client, Client
except ImportError:
    raise ImportError("supabase not installed. Run: pip install supabase")

from config import DATABASE_CONFIG

logger = logging.getLogger(__name__)


class SupabaseClient:
    """Supabase PostgreSQL client"""
    
    def __init__(self):
        """Initialize Supabase client"""
        if not DATABASE_CONFIG['supabase_url'] or not DATABASE_CONFIG['supabase_key']:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY required. Check .env file.")
        
        try:
            self.client: Client = create_client(
                DATABASE_CONFIG['supabase_url'],
                DATABASE_CONFIG['supabase_key']
            )
            logger.info("✓ Connected to Supabase")
        except Exception as e:
            logger.error(f"✗ Supabase connection failed: {e}")
            raise
    
    def insert_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """
        Insert jobs into database (upsert by URL to avoid duplicates)
        Returns list of newly inserted jobs
        """
        if not jobs:
            logger.warning("No jobs to insert")
            return []
        
        new_jobs = []
        table = DATABASE_CONFIG['jobs_table']
        
        for job in jobs:
            try:
                # Check if URL already exists
                existing = self.client.table(table).select('id').eq('url', job['url']).execute()
                
                if not existing.data:
                    # Insert new job
                    result = self.client.table(table).insert({
                        'company': job.get('company', ''),
                        'title': job.get('title', ''),
                        'url': job.get('url', ''),
                        'description': job.get('description', '')[:1000],  # Truncate
                        'posted_date': job.get('posted_date', datetime.now().isoformat()),
                        'scraped_date': datetime.now().isoformat(),
                        'source': job.get('source', 'Unknown'),
                        'relevance_score': job.get('relevance_score', 0),
                        'sector': job.get('sector', ''),
                        'is_bookmarked': False,
                    }).execute()
                    
                    if result.data:
                        new_jobs.append(result.data[0])
                        logger.debug(f"✓ Inserted: {job.get('title')}")
                else:
                    logger.debug(f"~ Skipped (exists): {job.get('title')}")
            
            except Exception as e:
                logger.error(f"✗ Insert error for {job.get('title')}: {e}")
        
        logger.info(f"Inserted {len(new_jobs)} new jobs out of {len(jobs)} total")
        return new_jobs
    
    def get_recent_jobs(self, days: int = 1, limit: int = 50) -> List[Dict]:
        """Get jobs from the last N days"""
        try:
            table = DATABASE_CONFIG['jobs_table']
            result = self.client.table(table).select('*')\
                .gte('scraped_date', self._get_date_iso(days))\
                .order('scraped_date', desc=True)\
                .limit(limit)\
                .execute()
            
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"✗ Query error: {e}")
            return []
    
    def get_top_jobs(self, limit: int = 15, min_score: int = 0) -> List[Dict]:
        """Get top-scoring jobs"""
        try:
            table = DATABASE_CONFIG['jobs_table']
            result = self.client.table(table).select('*')\
                .gte('relevance_score', min_score)\
                .order('relevance_score', desc=True)\
                .limit(limit)\
                .execute()
            
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"✗ Query error: {e}")
            return []
    
    def get_jobs_by_company(self, company: str, limit: int = 20) -> List[Dict]:
        """Get jobs for a specific company"""
        try:
            table = DATABASE_CONFIG['jobs_table']
            result = self.client.table(table).select('*')\
                .eq('company', company)\
                .order('scraped_date', desc=True)\
                .limit(limit)\
                .execute()
            
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"✗ Query error for {company}: {e}")
            return []
    
    def bookmark_job(self, job_id: int) -> bool:
        """Mark a job as bookmarked"""
        try:
            table = DATABASE_CONFIG['jobs_table']
            result = self.client.table(table).update(
                {'is_bookmarked': True}
            ).eq('id', job_id).execute()
            
            logger.debug(f"✓ Bookmarked job {job_id}")
            return bool(result.data)
        except Exception as e:
            logger.error(f"✗ Bookmark error: {e}")
            return False
    
    def unbookmark_job(self, job_id: int) -> bool:
        """Remove bookmark from a job"""
        try:
            table = DATABASE_CONFIG['jobs_table']
            result = self.client.table(table).update(
                {'is_bookmarked': False}
            ).eq('id', job_id).execute()
            
            logger.debug(f"✓ Unbookmarked job {job_id}")
            return bool(result.data)
        except Exception as e:
            logger.error(f"✗ Unbookmark error: {e}")
            return False
    
    def get_bookmarked_jobs(self, limit: int = 50) -> List[Dict]:
        """Get all bookmarked jobs"""
        try:
            table = DATABASE_CONFIG['jobs_table']
            result = self.client.table(table).select('*')\
                .eq('is_bookmarked', True)\
                .order('scraped_date', desc=True)\
                .limit(limit)\
                .execute()
            
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"✗ Query error: {e}")
            return []
    
    def count_jobs(self, days: Optional[int] = None) -> int:
        """Count total jobs (or jobs from last N days)"""
        try:
            table = DATABASE_CONFIG['jobs_table']
            query = self.client.table(table).select('id', count='exact')
            
            if days:
                query = query.gte('scraped_date', self._get_date_iso(days))
            
            result = query.execute()
            return result.count if result.count is not None else 0
        except Exception as e:
            logger.error(f"✗ Count error: {e}")
            return 0
    
    def log_feed_status(self, company: str, feed_url: str, status: str, entries: int = 0) -> bool:
        """Log feed validation status"""
        try:
            table = DATABASE_CONFIG['feed_logs_table']
            result = self.client.table(table).insert({
                'company': company,
                'feed_url': feed_url,
                'status': status,
                'last_checked': datetime.now().isoformat(),
                'entries_found': entries,
            }).execute()
            
            return bool(result.data)
        except Exception as e:
            logger.error(f"✗ Feed log error: {e}")
            return False
    
    def delete_old_jobs(self, days: int = 90) -> int:
        """Delete jobs older than N days (for cleanup)"""
        try:
            table = DATABASE_CONFIG['jobs_table']
            result = self.client.table(table).delete()\
                .lt('scraped_date', self._get_date_iso(days))\
                .execute()
            
            logger.info(f"Deleted old jobs from {days}+ days ago")
            return len(result.data) if result.data else 0
        except Exception as e:
            logger.error(f"✗ Delete error: {e}")
            return 0
    
    @staticmethod
    def _get_date_iso(days_ago: int) -> str:
        """Get ISO format date from N days ago"""
        from datetime import timedelta
        date = datetime.now() - timedelta(days=days_ago)
        return date.isoformat()


if __name__ == '__main__':
    # Test connection: python -m src.database
    try:
        db = SupabaseClient()
        count = db.count_jobs()
        print(f"✓ Connected. Total jobs in DB: {count}")
    except Exception as e:
        print(f"✗ Connection failed: {e}")
