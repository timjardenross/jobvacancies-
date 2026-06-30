import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.email_digest import EmailDigest


def test_html_generation(sample_jobs):
    digest = EmailDigest()
    scored = [{**j, "relevance_score": 50} for j in sample_jobs[:2]]
    html = digest.generate_html(scored, total_count=2)

    assert "ASX Jobs Digest" in html
    assert "Business Resilience Manager" in html
    assert "Commonwealth Bank" in html
    assert "2 matching jobs" in html
    assert "#4D5A94" in html  # brand colour


def test_html_empty_jobs():
    digest = EmailDigest()
    html = digest.generate_html([], total_count=0)
    assert "0 matching jobs" in html


def test_html_score_colours(sample_jobs):
    digest = EmailDigest()
    high = [{**sample_jobs[0], "relevance_score": 40}]
    mid  = [{**sample_jobs[0], "relevance_score": 20}]
    low  = [{**sample_jobs[0], "relevance_score": 5}]

    assert "#27ae60" in digest.generate_html(high, 1)
    assert "#e67e22" in digest.generate_html(mid, 1)
    assert "#7f8c8d" in digest.generate_html(low, 1)
