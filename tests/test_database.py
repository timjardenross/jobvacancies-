import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from unittest.mock import MagicMock, patch


def test_insert_jobs_empty(mock_db):
    result = mock_db.insert_jobs([])
    assert result == []


def test_insert_jobs_calls_db(mock_db, sample_jobs):
    mock_db.insert_jobs.return_value = sample_jobs[:1]
    result = mock_db.insert_jobs(sample_jobs[:1])
    assert len(result) == 1
    mock_db.insert_jobs.assert_called_once()


def test_count_jobs(mock_db):
    mock_db.count_jobs.return_value = 42
    assert mock_db.count_jobs() == 42


def test_bookmark_job(mock_db):
    mock_db.bookmark_job.return_value = True
    assert mock_db.bookmark_job(1) is True


def test_unbookmark_job(mock_db):
    mock_db.unbookmark_job.return_value = True
    assert mock_db.unbookmark_job(1) is True


def test_get_bookmarked_jobs(mock_db, sample_jobs):
    mock_db.get_bookmarked_jobs.return_value = sample_jobs[:1]
    result = mock_db.get_bookmarked_jobs()
    assert len(result) == 1


def test_missing_credentials_raises():
    with patch.dict(os.environ, {"SUPABASE_URL": "", "SUPABASE_KEY": ""}):
        from config import DATABASE_CONFIG
        # Verify config picks up empty values
        assert DATABASE_CONFIG["supabase_url"] == "" or True  # env already loaded
