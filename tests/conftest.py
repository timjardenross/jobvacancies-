import pytest
from unittest.mock import MagicMock


@pytest.fixture
def mock_db():
    db = MagicMock()
    db.insert_jobs.return_value = []
    db.get_top_jobs.return_value = []
    db.get_recent_jobs.return_value = []
    db.count_jobs.return_value = 0
    db.get_bookmarked_jobs.return_value = []
    return db


@pytest.fixture
def sample_jobs():
    return [
        {
            "company": "Commonwealth Bank",
            "title": "Business Resilience Manager",
            "url": "https://example.com/job/1",
            "description": "Leading business continuity and resilience programs.",
            "posted_date": "2026-06-30T00:00:00",
            "source": "RSS",
            "sector": "Financial Services",
        },
        {
            "company": "Telstra",
            "title": "Customer Success Lead",
            "url": "https://example.com/job/2",
            "description": "Drive customer success outcomes across enterprise accounts.",
            "posted_date": "2026-06-30T00:00:00",
            "source": "RSS",
            "sector": "Telecommunications",
        },
        {
            "company": "ANZ",
            "title": "Risk Specialist",
            "url": "https://example.com/job/3",
            "description": "Compliance and audit role.",
            "posted_date": "2026-06-30T00:00:00",
            "source": "RSS",
            "sector": "Financial Services",
        },
    ]
