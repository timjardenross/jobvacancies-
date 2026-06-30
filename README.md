# ASX Job Scraper — Production-Ready Package

Automated daily job scraper for ASX Top 50 companies. Scrapes job feeds, scores by relevance, stores in cloud database, sends email digest.

**Status:** Ready for Claude Code → Deploy

---

## What It Does

- ✓ Scrapes 50 ASX company career feeds (RSS + Playwright fallback)
- ✓ Filters by Business Resilience / Customer Success / CX keywords
- ✓ Runs daily at 6 AM AEST (GitHub Actions)
- ✓ Sends email digest with top jobs
- ✓ Cloud database (Supabase PostgreSQL)
- ✓ Web dashboard to browse + bookmark jobs
- ✓ All code versioned in GitHub

---

## Tech Stack

```
GitHub Repo (Code + Actions)
    ↓
Supabase (PostgreSQL Database)
    ↓
Gmail (Email Digest)
    ↓
Web Dashboard (Optional: Vercel)
```

**Cost:** $0/month (everything free tier)

---

## Quick Start

### 1️⃣ Prerequisites (5 mins)

You need:
- GitHub account (free): https://github.com/signup
- Supabase account (free): https://supabase.com
- Gmail account (existing)

### 2️⃣ Build with Claude Code (30 mins)

In Claude Code, I'll generate all files. You'll get:
- `src/` — Main scraper logic
- `web/` — Flask dashboard
- `.github/workflows/` — Automated scheduling
- `config/` — ASX 50 feeds
- `requirements.txt` — Dependencies
- `.env.example` — Secrets template

### 3️⃣ Push to GitHub (5 mins)

```bash
git clone https://github.com/YOUR-USERNAME/asx-jobs-scraper.git
cd asx-jobs-scraper
# (Copy all files from Claude Code here)
git add .
git commit -m "Initial commit"
git push origin main
```

### 4️⃣ Connect External Services (10 mins)

- **Supabase:** Create project, get credentials
- **Gmail:** Generate app password
- **GitHub Secrets:** Add SUPABASE_URL, SUPABASE_KEY, GMAIL_ADDRESS, GMAIL_PASSWORD

### 5️⃣ Test & Launch (5 mins)

- Run GitHub Actions workflow manually
- Verify email arrives
- Check Supabase has data
- Done! Runs automatically every day.

---

## Architecture

```
┌─────────────────────────────────────┐
│ GitHub Actions (6 AM daily)         │
│ python -m src.cli scrape --email    │
└────────────────┬────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────┐
│ ASX Job Scraper                     │
│ • RSS feeds (50 companies)          │
│ • Playwright fallback               │
│ • Keyword scoring                   │
│ • Relevance ranking                 │
└────────────────┬────────────────────┘
                 │
          ┌──────┴──────┐
          ↓             ↓
    ┌──────────┐  ┌──────────┐
    │ Supabase │  │   Email  │
    │   (DB)   │  │  (SMTP)  │
    └──────────┘  └──────────┘
          ↑
          │
    ┌──────────┐
    │ Dashboard│ (Optional: Vercel)
    └──────────┘
```

---

## Files Included

| File | Purpose |
|------|---------|
| `src/config.py` | ASX 50 feeds + keywords |
| `src/scraper.py` | Main scraper orchestration |
| `src/database.py` | Supabase client |
| `src/email.py` | Email digest HTML + SMTP |
| `src/cli.py` | CLI commands (validate, scrape, test-email) |
| `src/validator.py` | Feed testing + reporting |
| `web/app.py` | Flask dashboard |
| `web/templates/*` | HTML pages (branded) |
| `web/static/style.css` | TJR brand styling |
| `.github/workflows/daily-scrape.yml` | GitHub Actions scheduler |
| `requirements.txt` | Python dependencies |
| `docker-compose.yml` | Local dev environment |
| `.env.example` | Secrets template |

---

## Setup Steps (In Order)

### Step 1: Create GitHub Repo

```bash
# On GitHub.com
1. Click "New Repository"
2. Name: asx-jobs-scraper
3. Description: "Automated ASX Top 50 job scraper"
4. Click "Create repository"

# On your laptop
git clone https://github.com/YOUR-USERNAME/asx-jobs-scraper.git
cd asx-jobs-scraper
```

### Step 2: Copy Files from Claude Code

Claude Code will generate all files. Copy them into this directory.

### Step 3: Create Supabase Project

```
1. Go to https://supabase.com
2. Click "New Project"
3. Name: asx-jobs-db
4. Region: Australia (ap-southeast-2)
5. Save database password
6. Wait for deployment (~2 mins)
7. Go to Settings → API
8. Copy: Project URL, anon/public key
```

### Step 4: Initialize Supabase Tables

```
In Supabase, go to SQL Editor → New Query → paste:
(See SUPABASE_INIT.sql in this package)
Click Run
```

### Step 5: Get Gmail App Password

```
1. Go to https://myaccount.google.com/security
2. Enable 2-Factor Auth (if needed)
3. Search "App passwords"
4. Select Mail + Linux
5. Copy 16-character password
```

### Step 6: Add GitHub Secrets

```
GitHub repo → Settings → Secrets and variables → Actions

Add these:
- SUPABASE_URL = (from Supabase settings)
- SUPABASE_KEY = (from Supabase settings)
- GMAIL_ADDRESS = your-email@gmail.com
- GMAIL_PASSWORD = (16-char from Gmail)
```

### Step 7: Push to GitHub

```bash
git add .
git commit -m "Initial commit"
git push origin main
```

### Step 8: Test

```bash
# In GitHub repo, go to Actions tab
# Click "Daily ASX Job Scrape"
# Click "Run workflow"
# Wait ~2 mins for ✅

# Check your inbox for email digest
# Check Supabase: SQL Editor → SELECT COUNT(*) FROM jobs;
```

---

## Usage

### Command Line

```bash
# Validate all feeds
python -m src.cli validate

# Run scraper once
python -m src.cli scrape --email your-email@gmail.com

# Send test email
python -m src.cli test_email

# Start web dashboard
python web/app.py
# Visit http://localhost:5000
```

### GitHub Actions

Runs automatically every day at 6 AM AEST.

To manually trigger:
```
GitHub → Actions → Daily ASX Job Scrape → Run workflow
```

### Web Dashboard

View/bookmark jobs at `http://localhost:5000` (or Vercel URL if deployed)

---

## Customization

### Change Schedule

Edit `.github/workflows/daily-scrape.yml`:
```yaml
on:
  schedule:
    - cron: '0 6 * * *'  # Change time here (6 AM AEST)
```

### Add/Remove Companies

Edit `src/config.py`:
```python
ASX_FEEDS = {
    "Commonwealth Bank": {...},
    # Add or remove companies
}
```

### Change Email Recipient

In GitHub Secrets, update `GMAIL_ADDRESS` or:
```bash
python -m src.cli scrape --email different@email.com
```

### Change Keyword Scoring

Edit `src/config.py`:
```python
KEYWORDS_INCLUDE = ["resilience", "continuity", ...]
KEYWORDS_EXCLUDE = ["risk specialist", ...]
```

---

## Troubleshooting

### GitHub Actions Fails

1. Go to Actions → Job → Run details
2. Check error message
3. Common issues:
   - Secret not set → Add to GitHub Secrets
   - Auth error → Verify secret values (copy-paste exactly)
   - Import error → Check file names match

### No Email Received

1. Check spam folder
2. Verify `GMAIL_PASSWORD` is app password (16 chars)
3. Test locally: `python -m src.cli test_email`

### Dashboard Connection Error

1. Check `SUPABASE_URL` and `SUPABASE_KEY` are correct
2. Verify tables exist: Supabase → SQL Editor
3. Test Supabase connection locally first

---

## Deployment Options

| Option | Cost | Setup | Best For |
|--------|------|-------|----------|
| **GitHub Actions** | $0 | 15 min | Fully automated (recommended) |
| **Your VM** | $0 | 20 min | Keep on existing VM |
| **Vercel** (dashboard) | $0 | 10 min | Web UI accessible anywhere |
| **Google Cloud Run** | $5/mo | 30 min | Serverless (skip for now) |

**Recommended:** GitHub Actions + optional Vercel for dashboard

---

## Monitoring

**Daily:** Check email at 6 AM AEST

**Weekly:** 
```bash
# Review jobs
python -m src.cli scrape  # Local test

# Check Supabase
SELECT COUNT(*) FROM jobs WHERE scraped_date > NOW() - INTERVAL '7 days';
```

**Monthly:**
```bash
# Validate feeds
python -m src.cli validate > report.txt
cat report.txt
```

---

## Support

If something breaks:

1. Check `.github/workflows/daily-scrape.yml` matches your setup
2. Verify GitHub Secrets are exact copies (no extra spaces)
3. Test locally: `python -m src.cli validate`
4. Check Supabase tables exist
5. Review Supabase logs for SQL errors

---

## Next Steps

1. **Now:** Read this README
2. **Next:** Follow the Setup Steps above
3. **Then:** Use COMPLETE_CHECKLIST.md to track progress
4. **Finally:** Monitor for 1-2 weeks, optimize keywords if needed

---

**Ready to build?** Start with Step 1 above, then use Claude Code to generate all files.

**Total setup time:** ~1 hour  
**Monthly cost:** $0  
**Maintenance:** ~5 mins/week

