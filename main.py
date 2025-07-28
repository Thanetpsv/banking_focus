# to run the app locally, run the following on terminal: 
# 1) Activate venv: source venv/bin/activate 
# 2) run: uvicorn main:app --reload

# Grow Wealth Focus Backend (Audit & News)
from fastapi import FastAPI, Query
from pydantic import BaseModel
from audit_definitions import audit_definitions
from dotenv import load_dotenv
import os
import random
import feedparser



app = FastAPI()

# Static UK audit terms (can be expanded)
UK_AUDIT_TERMS = [
    "Materiality", "Substantive Testing", "ISA 315", "ISA 240", "ISA 330", "ISA 700", "ISA 520", "ISA 540", "ISA 570", "ISA 580", "ISA 600", "ISA 610", "ISA 620",
    "Going Concern", "Audit Risk", "Control Environment", "Sampling", "Engagement Letter", "Audit Opinion", "Assertions", "ICAEW Code of Ethics", "External Confirmation", "Analytical Procedures", "Audit Evidence",
    "Audit Planning", "Risk Assessment", "Test of Controls", "Substantive Procedures", "Audit Documentation", "Audit Trail", "Professional Skepticism", "Independence", "Ethical Standards", "Audit Committee", "Internal Audit", "External Audit",
    "Audit File", "Audit Partner", "Audit Manager", "Audit Senior", "Audit Junior", "Audit Findings", "Audit Recommendations", "Audit Follow-up", "Audit Scope", "Audit Methodology", "Audit Standards", "Audit Quality", "Audit Review",
    "Audit Engagement", "Audit Client", "Audit Fees", "Audit Timetable", "Audit Risks", "Audit Controls", "Audit Testing", "Audit Completion", "Audit Communication", "Audit Working Papers", "Audit Population", "Audit Selection", "Audit Results", "Audit Issues", "Audit Adjustments", "Audit Observation", "Audit Inquiry", "Audit Confirmation", "Audit Inspection", "Audit Analysis", "Audit Techniques", "Audit Tools", "Audit Software", "Audit Automation", "Audit Analytics", "Audit Data", "Audit Reasoning", "Audit Judgment", "Audit Professionalism", "Audit Ethics", "Audit Integrity", "Audit Objectivity"
]

class AuditTermRequest(BaseModel):
    term: str

@app.get("/audit/terms")
async def get_audit_terms(refresh: bool = Query(False)):
    """Return 3 random UK audit terms. Use refresh to get a new set."""
    terms = random.sample(UK_AUDIT_TERMS, k=3)
    return {"terms": terms}

@app.post("/audit/define")
async def define_audit_term(req: AuditTermRequest):
    """Return a memorable, light-hearted, and accurate definition for a UK audit term from local data, plus FRC link."""
    definition = audit_definitions.get(req.term)
    base_url = "https://www.frc.org.uk/library/?query="
    term_query = req.term.replace(" ", "+")
    frc_url = f"{base_url}{term_query}&topics=auditing"
    if definition:
        return {"definition": definition, "frc_link": frc_url}
    else:
        return {"definition": "No definition found for this term.", "frc_link": frc_url}

@app.get("/audit/news")
async def get_audit_news():
    """Return 2 latest news headlines: UK audit and global banking/capital markets."""
    feeds = [
        # UK audit news (e.g. Accountancy Daily)
        "https://www.accountancydaily.co/rss/audit",
        # Global banking/capital markets (Reuters)
        "https://www.reuters.com/rssFeed/bankingNews"
    ]
    headlines = []
    for url in feeds:
        try:
            d = feedparser.parse(url)
            if d.entries:
                headlines.append({
                    "title": d.entries[0].title,
                    "link": d.entries[0].link
                })
        except Exception:
            headlines.append({"title": "Error fetching news", "link": url})
    return {"headlines": headlines}
