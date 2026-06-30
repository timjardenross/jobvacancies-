"""
ASX Job Scraper Configuration
All 50 companies, keywords, scoring logic
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# SUPABASE & EMAIL CONFIG (from .env)
# ============================================================================

SUPABASE_URL = os.getenv('SUPABASE_URL', '')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')
GMAIL_ADDRESS = os.getenv('GMAIL_ADDRESS', '')
GMAIL_PASSWORD = os.getenv('GMAIL_PASSWORD', '')

# ============================================================================
# ASX TOP 50 COMPANY FEEDS
# ============================================================================

ASX_FEEDS = {
    # RANK 1-10
    "Commonwealth Bank": {
        "feed": "https://cba.wd3.myworkdayjobs.com/CommBank_Careers/feed",
        "alternative": "https://www.commbank.com.au/about-us/careers.html",
        "sector": "Financial Services"
    },
    "National Australia Bank": {
        "feed": "https://nab.wd3.myworkdayjobs.com/NAB_Careers/feed",
        "alternative": "https://careers.nab.com.au",
        "sector": "Financial Services"
    },
    "Westpac": {
        "feed": "https://westpac.wd3.myworkdayjobs.com/Westpac_Careers/feed",
        "alternative": "https://www.westpac.com.au/careers/",
        "sector": "Financial Services"
    },
    "ANZ": {
        "feed": "https://anz.wd3.myworkdayjobs.com/ANZ_Careers/feed",
        "alternative": "https://careers.anz.com/au/en/",
        "sector": "Financial Services"
    },
    "QBE Insurance": {
        "feed": "https://qbe.wd3.myworkdayjobs.com/QBE-Careers/feed",
        "alternative": "https://careers.qbe.com",
        "sector": "Financial Services"
    },
    "BHP Group": {
        "feed": "https://bhp.wd3.myworkdayjobs.com/BHP_Careers/feed",
        "alternative": "https://careers.bhp.com",
        "sector": "Materials"
    },
    "Rio Tinto": {
        "feed": "https://riotinto.wd3.myworkdayjobs.com/RioTinto_Careers/feed",
        "alternative": "https://careers.riotinto.com",
        "sector": "Materials"
    },
    "Telstra": {
        "feed": "https://telstra.wd3.myworkdayjobs.com/Telstra_Careers/feed",
        "alternative": "https://www.telstra.com.au/careers/",
        "sector": "Telecommunications"
    },
    "Woolworths": {
        "feed": "https://woolworths.wd3.myworkdayjobs.com/Woolworths_Careers/feed",
        "alternative": "https://careers.woolworthsgroup.com.au",
        "sector": "Retail"
    },
    "Macquarie": {
        "feed": "https://macquarie.wd3.myworkdayjobs.com/Macquarie_Careers/feed",
        "alternative": "https://www.macquarie.com/au/en/about/careers.html",
        "sector": "Financial Services"
    },
    
    # RANK 11-20
    "AMP": {
        "feed": "https://amp.wd3.myworkdayjobs.com/AMP_Careers/feed",
        "alternative": "https://careers.amp.com.au",
        "sector": "Financial Services"
    },
    "Lendlease": {
        "feed": "https://lendlease.wd3.myworkdayjobs.com/lendleasecareers/feed",
        "alternative": "https://careers.lendlease.com",
        "sector": "Real Estate"
    },
    "CSL": {
        "feed": "https://csl.wd1.myworkdayjobs.com/CSL_External/feed",
        "alternative": "https://careers.csl.com.au",
        "sector": "Healthcare"
    },
    "Fortescue": {
        "feed": "https://fmg.wd3.myworkdayjobs.com/FMG_Careers/feed",
        "alternative": "https://careers.fortescuemetalsgroup.com",
        "sector": "Materials"
    },
    "Brambles": {
        "feed": "https://brambles.wd3.myworkdayjobs.com/Brambles_Careers/feed",
        "alternative": "https://www.brambles.com/careers",
        "sector": "Industrials"
    },
    "nbn": {
        "feed": "https://nbn.wd3.myworkdayjobs.com/nbncareers/feed",
        "alternative": "https://careers.nbnco.com.au",
        "sector": "Telecommunications"
    },
    "Woodside Energy": {
        "feed": "https://woodsideenergy.wd3.myworkdayjobs.com/Woodside_Careers/feed",
        "alternative": "https://careers.woodside.com.au",
        "sector": "Energy"
    },
    "Santos": {
        "feed": "https://santos.wd3.myworkdayjobs.com/Santos_Careers/feed",
        "alternative": "https://careers.santos.com",
        "sector": "Energy"
    },
    "Suncorp": {
        "feed": "https://suncorp.wd3.myworkdayjobs.com/Suncorp_Careers/feed",
        "alternative": "https://careers.suncorp.com.au",
        "sector": "Financial Services"
    },
    
    # RANK 21-30
    "Transurban": {
        "feed": "https://transurban.wd3.myworkdayjobs.com/Transurban_Careers/feed",
        "alternative": "https://careers.transurban.com/",
        "sector": "Industrials"
    },
    "Aristocrat Leisure": {
        "feed": "https://aristocrat.wd3.myworkdayjobs.com/AristocratExternalCareersSite/feed",
        "alternative": "https://careers.aristocrat.com",
        "sector": "Consumer Discretionary"
    },
    "WiseTech Global": {
        "feed": "https://www.wisetechglobal.com/careers/current-openings",  # Custom portal
        "alternative": "https://www.wisetechglobal.com/careers",
        "sector": "Information Technology"
    },
    "REA Group": {
        "feed": "https://rea.wd3.myworkdayjobs.com/REA_Careers/feed",
        "alternative": "https://www.realestate.com.au/careers",
        "sector": "Information Technology"
    },
    "Coles Group": {
        "feed": "https://coles.wd3.myworkdayjobs.com/Coles_Careers/feed",
        "alternative": "https://colescareers.com.au/",
        "sector": "Retail"
    },
    "NEXTDC": {
        "feed": "https://nextdc.wd3.myworkdayjobs.com/NEXTDC_Careers/feed",
        "alternative": "https://www.nextdc.com/careers",
        "sector": "Information Technology"
    },
    "APA Group": {
        "feed": "https://apa.wd3.myworkdayjobs.com/APA_Careers/feed",
        "alternative": "https://careers.apa.com.au",
        "sector": "Utilities"
    },
    "SEEK Limited": {
        "feed": "https://seek.wd3.myworkdayjobs.com/SEEK_Careers/feed",
        "alternative": "https://careers.seek.com.au",
        "sector": "Consumer Discretionary"
    },
    "Afterpay": {
        "feed": "https://afterpay.wd3.myworkdayjobs.com/Afterpay_Careers/feed",
        "alternative": "https://careers.afterpay.com",
        "sector": "Financial Services"
    },
    "Nine Entertainment": {
        "feed": "https://ninemedia.wd3.myworkdayjobs.com/Nine_Careers/feed",
        "alternative": "https://careers.nineentertainment.com.au",
        "sector": "Communication Services"
    },
    
    # RANK 31-40
    "Evolution Mining": {
        "feed": "https://evolutionmining.wd3.myworkdayjobs.com/Evolution_Careers/feed",
        "alternative": "https://careers.evolutionmining.com.au",
        "sector": "Materials"
    },
    "Wesfarmers": {
        "feed": "https://wesfarmers.wd3.myworkdayjobs.com/Wesfarmers_Careers/feed",
        "alternative": "https://careers.wesfarmers.com.au",
        "sector": "Retail"
    },
    "Sonic Healthcare": {
        "feed": "https://sonichealthcare.wd3.myworkdayjobs.com/Sonic_Careers/feed",
        "alternative": "https://careers.sonichealthcare.com.au",
        "sector": "Healthcare"
    },
    "Medibank": {
        "feed": "https://medibank.wd3.myworkdayjobs.com/Medibank_Careers/feed",
        "alternative": "https://careers.medibank.com.au",
        "sector": "Healthcare"
    },
    "Pro Medicus": {
        "feed": "https://promedicus.wd3.myworkdayjobs.com/ProMedicus_Careers/feed",
        "alternative": "https://careers.promedicus.com.au",
        "sector": "Healthcare"
    },
    "Computershare": {
        "feed": "https://computershare.wd3.myworkdayjobs.com/Computershare_Careers/feed",
        "alternative": "https://careers.computershare.com",
        "sector": "Financial Services"
    },
    "Insurance Australia Group": {
        "feed": "https://iag.wd3.myworkdayjobs.com/IAG_Careers/feed",
        "alternative": "https://careers.iag.com.au",
        "sector": "Financial Services"
    },
    "Amcor": {
        "feed": "https://amcor.wd3.myworkdayjobs.com/Amcor_Careers/feed",
        "alternative": "https://careers.amcor.com",
        "sector": "Materials"
    },
    "Technology One": {
        "feed": "https://technologyone.wd3.myworkdayjobs.com/TechOne_Careers/feed",
        "alternative": "https://careers.technologyone.com",
        "sector": "Information Technology"
    },
    
    # RANK 41-50
    "Xero": {
        "feed": "https://xero.wd3.myworkdayjobs.com/Xero_Careers/feed",
        "alternative": "https://careers.xero.com",
        "sector": "Information Technology"
    },
    "Qantas Airways": {
        "feed": "https://qantas.wd3.myworkdayjobs.com/Qantas_Careers/feed",
        "alternative": "https://careers.qantas.com.au",
        "sector": "Industrials"
    },
    "South32": {
        "feed": "https://south32.wd3.myworkdayjobs.com/South32_Careers/feed",
        "alternative": "https://careers.south32.net",
        "sector": "Materials"
    },
    "Cochlear": {
        "feed": "https://cochlear.wd3.myworkdayjobs.com/Cochlear_Careers/feed",
        "alternative": "https://careers.cochlear.com",
        "sector": "Healthcare"
    },
    "Origin Energy": {
        "feed": "https://originenergy.wd3.myworkdayjobs.com/Origin_Careers/feed",
        "alternative": "https://careers.originenergy.com.au",
        "sector": "Utilities"
    },
    "Vicinity Centres": {
        "feed": "https://vicinity.wd3.myworkdayjobs.com/Vicinity_Careers/feed",
        "alternative": "https://careers.vicinity.com.au",
        "sector": "Real Estate"
    },
    "BlueScope Steel": {
        "feed": "https://bluescope.wd3.myworkdayjobs.com/BlueScope_Careers/feed",
        "alternative": "https://careers.bluescope.com",
        "sector": "Materials"
    },
    "Worley": {
        "feed": "https://worley.wd3.myworkdayjobs.com/Worley_Careers/feed",
        "alternative": "https://careers.worley.com",
        "sector": "Industrials"
    },
    "Aurizon Holdings": {
        "feed": "https://aurizon.wd3.myworkdayjobs.com/Aurizon_Careers/feed",
        "alternative": "https://careers.aurizon.com.au",
        "sector": "Industrials"
    },
    "Ramsay Health Care": {
        "feed": "https://ramsayhealth.wd3.myworkdayjobs.com/Ramsay_Careers/feed",
        "alternative": "https://careers.ramsayhealth.com.au",
        "sector": "Healthcare"
    },
}

# ============================================================================
# KEYWORD SCORING
# ============================================================================

KEYWORDS_INCLUDE = [
    "resilience",
    "continuity",
    "recovery",
    "customer success",
    "service delivery",
    "customer experience",
    "cx",
    "operational excellence",
    "service management",
    "business continuity",
    "disaster recovery",
    "crisis management",
]

KEYWORDS_EXCLUDE = [
    "risk specialist",
    "compliance officer",
    "pure risk",
    "security clearance",
    "underwriting",
    "actuarial",
    "audit",
]

# ============================================================================
# SCORING WEIGHTS
# ============================================================================

RELEVANCE_SCORING = {
    "keyword_in_title": 30,           # +30 if keyword appears in title
    "keyword_in_description": 15,     # +15 if keyword in description
    "exclusion_in_title": -50,        # -50 if exclusion keyword in title
    "priority_company_bonus": 10,     # +10 for Top 20 companies
    "minimum_score": 0,               # Min score before inclusion
    "maximum_score": 100,             # Max score (clamped)
}

# Companies weighted higher (all in Top 20)
PRIORITY_COMPANIES = [
    "Commonwealth Bank",
    "National Australia Bank",
    "Westpac",
    "ANZ",
    "QBE Insurance",
    "BHP Group",
    "Rio Tinto",
    "Telstra",
    "Woolworths",
    "Macquarie",
    "AMP",
    "Lendlease",
    "CSL",
    "Fortescue",
    "Brambles",
    "nbn",
    "Woodside Energy",
    "Santos",
    "Suncorp",
]

# ============================================================================
# EMAIL SETTINGS
# ============================================================================

EMAIL_CONFIG = {
    "send_digest": True,
    "digest_recipient": os.getenv('GMAIL_ADDRESS', ''),
    "daily_schedule": "06:00",  # 6 AM AEST
    "top_jobs_in_email": 15,    # Show top 15 jobs
    "minimum_relevance_score": 0,  # Include jobs with score > 0
}

# ============================================================================
# SCRAPER SETTINGS
# ============================================================================

SCRAPER_CONFIG = {
    "rss_timeout": 10,              # Seconds to wait for RSS feed
    "playwright_timeout": 15,       # Seconds to wait for page load
    "max_retries": 2,               # Retry failed feeds N times
    "parallel_playwright": 3,       # Number of concurrent Playwright instances
    "max_jobs_per_company": 20,     # Don't include more than 20 per company
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}

# ============================================================================
# DATABASE SETTINGS
# ============================================================================

DATABASE_CONFIG = {
    "supabase_url": SUPABASE_URL,
    "supabase_key": SUPABASE_KEY,
    "jobs_table": "jobs",
    "feed_logs_table": "feed_logs",
    "bookmarks_table": "bookmarks",
    "bulk_insert_size": 100,  # Insert N jobs at a time
}

# ============================================================================
# LOGGING
# ============================================================================

LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "log_file": "scraper.log",
}
