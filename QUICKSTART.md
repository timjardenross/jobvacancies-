# Quickstart — 5 Minutes to First Scrape

## Prerequisites
- Python 3.11+
- Supabase project (free at supabase.com)
- Gmail account with app password

## Setup

```bash
# 1. Clone your repo
git clone https://github.com/YOUR_USERNAME/asx-jobs-scraper.git
cd asx-jobs-scraper

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
playwright install chromium

# 4. Configure credentials
cp .env.example .env
# Edit .env with your Supabase URL, key, Gmail address + app password

# 5. Create database tables
# Go to Supabase → SQL Editor → paste contents of SUPABASE_INIT.sql → Run

# 6. Test email
python -m src.cli test-email

# 7. Run scraper
python -m src.cli scrape --email

# 8. Start dashboard
python web/app.py
# Open: http://localhost:5000
```

## After First Run
- Check your inbox — digest email should arrive
- Open http://localhost:5000 — jobs are listed
- Push to GitHub — Actions will run daily at 6 AM AEST automatically

## Common Commands

| Command | What it does |
|---------|-------------|
| `python -m src.cli scrape --email` | Scrape + send digest |
| `python -m src.cli validate` | Check all 50 feeds |
| `python -m src.cli test-email` | Send test email |
| `python -m src.cli stats` | Show job counts |
| `python web/app.py` | Start dashboard |
| `pytest tests/` | Run tests |
