"""
CLI interface — scrape, validate, test email, stats
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import asyncio
import logging
import click

from config import EMAIL_CONFIG, LOGGING_CONFIG

logging.basicConfig(
    level=LOGGING_CONFIG["level"],
    format=LOGGING_CONFIG["format"],
    handlers=[logging.FileHandler(LOGGING_CONFIG["log_file"]), logging.StreamHandler()],
)


@click.group()
def cli():
    """ASX Job Scraper — automated job discovery across ASX 50 companies."""
    pass


@cli.command()
def validate():
    """Test all 50 RSS feeds and show health report."""
    from src.validator import FeedValidator
    FeedValidator().run()


@cli.command()
@click.option("--email/--no-email", default=False, help="Send email digest after scraping")
@click.option("--recipient", default=None, help="Override email recipient")
def scrape(email, recipient):
    """Run full scraper across all ASX companies."""
    from src.database import SupabaseClient
    from src.scraper import run_scraper

    db = SupabaseClient()
    new_jobs = asyncio.run(run_scraper(db))
    click.echo(f"\n✓ Scrape complete. {len(new_jobs)} new jobs found.")

    if email and new_jobs:
        from src.email_digest import EmailDigest
        to = recipient or EMAIL_CONFIG["digest_recipient"]
        top_jobs = sorted(new_jobs, key=lambda j: j.get("relevance_score", 0), reverse=True)
        top_jobs = top_jobs[: EMAIL_CONFIG["top_jobs_in_email"]]
        sent = EmailDigest().send(to, top_jobs, len(new_jobs))
        click.echo(f"{'✓ Email sent to ' + to if sent else '✗ Email failed'}")


@cli.command()
@click.option("--recipient", default=None, help="Send test email to this address")
def test_email(recipient):
    """Send a test email digest with sample data."""
    from src.email_digest import EmailDigest
    from config import GMAIL_ADDRESS, EMAIL_CONFIG

    sample_jobs = [
        {"title": "Business Resilience Manager", "company": "Commonwealth Bank", "sector": "Financial Services", "url": "https://example.com/job/1", "relevance_score": 75},
        {"title": "Customer Success Lead", "company": "Telstra", "sector": "Telecommunications", "url": "https://example.com/job/2", "relevance_score": 60},
        {"title": "Service Delivery Manager", "company": "ANZ", "sector": "Financial Services", "url": "https://example.com/job/3", "relevance_score": 45},
    ]
    to = recipient or EMAIL_CONFIG["digest_recipient"] or GMAIL_ADDRESS
    sent = EmailDigest().send(to, sample_jobs, 3)
    click.echo(f"{'✓ Test email sent to ' + to if sent else '✗ Email failed — check GMAIL_ADDRESS and GMAIL_PASSWORD in .env'}")


@cli.command()
def stats():
    """Show database stats (total jobs, today's jobs, top companies)."""
    from src.database import SupabaseClient
    db = SupabaseClient()
    total = db.count_jobs()
    today = db.count_jobs(days=1)
    week = db.count_jobs(days=7)
    bookmarked = len(db.get_bookmarked_jobs())

    click.echo(f"\n📊 ASX Job Scraper Stats")
    click.echo(f"  Total jobs:       {total}")
    click.echo(f"  Jobs today:       {today}")
    click.echo(f"  Jobs this week:   {week}")
    click.echo(f"  Bookmarked:       {bookmarked}\n")


@cli.command()
@click.option("--days", default=90, help="Delete jobs older than N days (default: 90)")
def cleanup(days):
    """Delete old jobs from the database."""
    from src.database import SupabaseClient
    db = SupabaseClient()
    deleted = db.delete_old_jobs(days=days)
    click.echo(f"✓ Deleted {deleted} jobs older than {days} days")


if __name__ == "__main__":
    cli()
