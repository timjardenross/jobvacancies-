"""
Flask web dashboard — browse jobs, bookmark, view stats
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from flask import Flask, render_template, jsonify, request
from config import ASX_FEEDS

app = Flask(__name__)

# Use real DB if credentials present, otherwise demo mode
def _make_db():
    try:
        from src.database import SupabaseClient
        return SupabaseClient()
    except Exception:
        return None

db = _make_db()

_DEMO_JOBS = [
    {"id": 1, "company": "Commonwealth Bank", "title": "Business Resilience Manager", "url": "#", "description": "Lead business continuity programs across the enterprise.", "sector": "Financial Services", "relevance_score": 75, "is_bookmarked": False},
    {"id": 2, "company": "Telstra", "title": "Customer Success Lead", "url": "#", "description": "Drive customer success outcomes for enterprise accounts.", "sector": "Telecommunications", "relevance_score": 60, "is_bookmarked": True},
    {"id": 3, "company": "ANZ", "title": "Service Delivery Manager", "url": "#", "description": "Manage service delivery across banking operations.", "sector": "Financial Services", "relevance_score": 45, "is_bookmarked": False},
    {"id": 4, "company": "Macquarie", "title": "Operational Resilience Analyst", "url": "#", "description": "Support operational resilience frameworks and recovery planning.", "sector": "Financial Services", "relevance_score": 40, "is_bookmarked": False},
    {"id": 5, "company": "Westpac", "title": "Business Continuity Coordinator", "url": "#", "description": "Coordinate continuity planning and disaster recovery.", "sector": "Financial Services", "relevance_score": 35, "is_bookmarked": False},
    {"id": 6, "company": "Woolworths", "title": "Customer Experience Manager", "url": "#", "description": "Improve CX across retail and digital touchpoints.", "sector": "Retail", "relevance_score": 30, "is_bookmarked": False},
    {"id": 7, "company": "BHP Group", "title": "Crisis Management Specialist", "url": "#", "description": "Lead crisis management and emergency response plans.", "sector": "Materials", "relevance_score": 25, "is_bookmarked": False},
]


def _get(method, *args, **kwargs):
    if db:
        return getattr(db, method)(*args, **kwargs)
    return None


@app.route("/")
def index():
    company = request.args.get("company", "")
    sector = request.args.get("sector", "")
    bookmarked_only = request.args.get("bookmarked") == "1"
    min_score = int(request.args.get("min_score", 0))

    if db:
        if bookmarked_only:
            jobs = db.get_bookmarked_jobs(limit=100)
        elif company:
            jobs = db.get_jobs_by_company(company, limit=100)
        else:
            jobs = db.get_top_jobs(limit=100, min_score=min_score)
        if sector:
            jobs = [j for j in jobs if j.get("sector") == sector]
        sectors = sorted({j.get("sector", "") for j in db.get_top_jobs(limit=500) if j.get("sector")})
    else:
        jobs = [j for j in _DEMO_JOBS if j["relevance_score"] >= min_score]
        if company:
            jobs = [j for j in jobs if j["company"] == company]
        if sector:
            jobs = [j for j in jobs if j["sector"] == sector]
        if bookmarked_only:
            jobs = [j for j in jobs if j["is_bookmarked"]]
        sectors = sorted({j["sector"] for j in _DEMO_JOBS})

    companies = sorted(ASX_FEEDS.keys())
    demo_mode = db is None

    return render_template(
        "index.html",
        jobs=jobs,
        sectors=sectors,
        companies=companies,
        filters={"company": company, "sector": sector, "bookmarked_only": bookmarked_only, "min_score": min_score},
        demo_mode=demo_mode,
    )


@app.route("/stats")
def stats():
    if db:
        total = db.count_jobs()
        today = db.count_jobs(days=1)
        week = db.count_jobs(days=7)
        bookmarked = len(db.get_bookmarked_jobs())
        top_jobs = db.get_top_jobs(limit=5)
        recent_jobs = db.get_recent_jobs(days=1, limit=10)
    else:
        total = len(_DEMO_JOBS)
        today = 3
        week = 7
        bookmarked = sum(1 for j in _DEMO_JOBS if j["is_bookmarked"])
        top_jobs = sorted(_DEMO_JOBS, key=lambda j: j["relevance_score"], reverse=True)[:5]
        recent_jobs = _DEMO_JOBS[:5]

    return render_template(
        "stats.html",
        total=total, today=today, week=week, bookmarked=bookmarked,
        top_jobs=top_jobs, recent_jobs=recent_jobs,
        demo_mode=db is None,
    )


@app.route("/api/bookmark/<int:job_id>", methods=["POST"])
def bookmark(job_id):
    action = request.json.get("action", "bookmark") if request.is_json else "bookmark"
    if db:
        ok = db.unbookmark_job(job_id) if action == "unbookmark" else db.bookmark_job(job_id)
    else:
        ok = True  # demo mode: always succeed
    return jsonify({"success": ok, "action": action})


@app.route("/api/jobs")
def api_jobs():
    limit = min(int(request.args.get("limit", 50)), 200)
    min_score = int(request.args.get("min_score", 0))
    jobs = db.get_top_jobs(limit=limit, min_score=min_score) if db else _DEMO_JOBS
    return jsonify(jobs)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, port=port)
