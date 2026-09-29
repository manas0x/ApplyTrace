"""Job helpers: fetch a JD from a posting URL, and discover new jobs.

- POST /api/jobs/fetch-jd {url} -> {title, company, text}: downloads the
  posting page and extracts readable text, so nobody has to paste JDs.
- GET /api/jobs/discover?query=... -> live listings via the Adzuna API
  (needs ADZUNA_APP_ID / ADZUNA_APP_KEY env vars — free tier).
"""
import os
import re

import requests
from bs4 import BeautifulSoup
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    )
}


class FetchJdRequest(BaseModel):
    url: str


def _clean_text(soup: BeautifulSoup) -> str:
    for tag in soup(["script", "style", "nav", "header", "footer", "aside", "form"]):
        tag.decompose()
    # Prefer article/main content when present.
    root = soup.find("article") or soup.find("main") or soup.body or soup
    text = root.get_text(separator="\n")
    lines = [re.sub(r"\s+", " ", ln).strip() for ln in text.splitlines()]
    lines = [ln for ln in lines if len(ln) > 2]
    # Drop obvious nav/cookie boilerplate repeats.
    seen, out = set(), []
    for ln in lines:
        if ln not in seen:
            seen.add(ln)
            out.append(ln)
    return "\n".join(out)[:15000]


@router.post("/fetch-jd")
def fetch_jd(payload: FetchJdRequest):
    url = payload.url.strip()
    if not url.startswith(("http://", "https://")):
        raise HTTPException(400, "Please provide a full http(s) URL")
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
    except Exception as e:
        raise HTTPException(502, f"Could not download the posting: {e}")
    soup = BeautifulSoup(resp.text, "html.parser")
    title = (soup.title.string or "").strip() if soup.title else ""
    title = re.sub(r"\s+", " ", title)[:200]
    company = ""
    og_site = soup.find("meta", property="og:site_name")
    if og_site and og_site.get("content"):
        company = og_site["content"].strip()[:200]
    text = _clean_text(soup)
    if len(text) < 200:
        raise HTTPException(502, "The page blocked extraction (JS-heavy site?) — paste the JD manually.")
    return {"title": title, "company": company, "text": text}


@router.get("/discover")
def discover(query: str = "software developer intern", location: str = "India", pages: int = 1):
    """Live job listings via Adzuna. Requires ADZUNA_APP_ID / ADZUNA_APP_KEY."""
    app_id = os.getenv("ADZUNA_APP_ID", "")
    app_key = os.getenv("ADZUNA_APP_KEY", "")
    if not app_id or not app_key:
        raise HTTPException(
            501,
            "Job discovery isn't configured yet — add ADZUNA_APP_ID and ADZUNA_APP_KEY "
            "(free at developer.adzuna.com) to the backend env vars.",
        )
    try:
        resp = requests.get(
            "https://api.adzuna.com/v1/api/jobs/in/search/1",
            params={
                "app_id": app_id,
                "app_key": app_key,
                "results_per_page": min(max(pages, 1), 5) * 10,
                "what": query,
                "where": location,
                "sort_by": "date",
                "content-type": "application/json",
            },
            timeout=20,
        )
        resp.raise_for_status()
        data = resp.json()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(502, f"Adzuna request failed: {e}")
    jobs = []
    for j in data.get("results", []):
        jobs.append(
            {
                "title": j.get("title", ""),
                "company": (j.get("company") or {}).get("display_name", ""),
                "location": (j.get("location") or {}).get("display_name", ""),
                "url": j.get("redirect_url", ""),
                "snippet": BeautifulSoup(j.get("description", ""), "html.parser").get_text()[:600],
                "posted": (j.get("created") or "")[:10],
            }
        )
    return {"count": data.get("count", len(jobs)), "jobs": jobs}
