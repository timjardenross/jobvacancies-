import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scraper import ASXJobScraper


def test_score_job_high(mock_db, sample_jobs):
    scraper = ASXJobScraper(mock_db)
    score = scraper.score_job(sample_jobs[0])  # "Business Resilience Manager" — CBA (priority)
    assert score >= 30, f"Expected score >= 30 for resilience title, got {score}"


def test_score_job_medium(mock_db, sample_jobs):
    scraper = ASXJobScraper(mock_db)
    score = scraper.score_job(sample_jobs[1])  # "Customer Success Lead" — Telstra (priority)
    assert score >= 15


def test_score_job_excluded(mock_db, sample_jobs):
    scraper = ASXJobScraper(mock_db)
    score = scraper.score_job(sample_jobs[2])  # "Risk Specialist" — excluded keyword in title
    assert score < 0, f"Expected negative score for excluded title, got {score}"


def test_score_clamped(mock_db):
    scraper = ASXJobScraper(mock_db)
    job = {
        "company": "Commonwealth Bank",
        "title": "business resilience continuity recovery customer success cx",
        "description": "resilience continuity recovery crisis",
    }
    score = scraper.score_job(job)
    assert score <= 100


def test_filter_and_rank_removes_excluded(mock_db, sample_jobs):
    scraper = ASXJobScraper(mock_db)
    scored = scraper.filter_and_rank(sample_jobs)
    titles = [j["title"] for j in scored]
    assert "Risk Specialist" not in titles


def test_filter_and_rank_sorted(mock_db, sample_jobs):
    scraper = ASXJobScraper(mock_db)
    scored = scraper.filter_and_rank(sample_jobs)
    scores = [j["relevance_score"] for j in scored]
    assert scores == sorted(scores, reverse=True)
