"""Gmail integration: auto-detect job applications from email.

Flow:
  1. Frontend opens /api/gmail/auth-url -> Google OAuth consent (gmail.readonly).
  2. Google redirects to /api/gmail/callback -> refresh token stored in DB.
  3. POST /api/gmail/sync scans inbox + sent mail for application signals
     and creates Application rows (deduped against existing entries).

Only read-only Gmail access is requested, and a scan runs only when the user
presses "Sync from Gmail" — nothing runs in the background.
"""
import os
import re
from email.utils import parseaddr, parsedate_to_datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# Applicant-tracking systems whose domains should never be treated as the company.
ATS_DOMAINS = {
    "greenhouse.io", "lever.co", "workday.com", "myworkdayjobs.com",
    "ashbyhq.com", "smartrecruiters.com", "icims.com", "taleo.net",
    "successfactors.com", "workable.com", "breezy.hr", "jazzhr.com",
    "zoho.com", "freshteam.com", "keka.com", "darwinbox.com",
    "naukri.com", "linkedin.com", "indeed.com", "instahyre.com",
}
PERSONAL_DOMAINS = {"gmail", "yahoo", "outlook", "hotmail", "icloud", "protonmail", "gmx"}


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default)


def _redirect_uri() -> str:
    return _env("GOOGLE_REDIRECT_URI", "https://applytrace-api.vercel.app/api/gmail/callback")


def get_flow() -> Flow:
    # NOTE: autogenerate_code_verifier=False — the library now auto-adds PKCE
    # to the auth URL, but the verifier lives on the Flow object and would be
    # lost between serverless invocations (auth-url and callback run in
    # separate function calls). Plain OAuth2 + client_secret needs no PKCE.
    return Flow.from_client_config(
        {
            "web": {
                "client_id": _env("GOOGLE_CLIENT_ID"),
                "client_secret": _env("GOOGLE_CLIENT_SECRET"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [_redirect_uri()],
            }
        },
        scopes=SCOPES,
        redirect_uri=_redirect_uri(),
        autogenerate_code_verifier=False,
    )


def auth_url() -> str:
    flow = get_flow()
    # NOTE: no include_granted_scopes — that makes Google append openid/email/
    # profile scopes to the grant, and the token exchange then fails with
    # "Scope has changed". We only ever request gmail.readonly.
    url, _ = flow.authorization_url(access_type="offline", prompt="consent")
    return url


def exchange_code(code: str) -> Credentials:
    flow = get_flow()
    flow.fetch_token(code=code)
    return flow.credentials


def get_service(refresh_token: str):
    creds = Credentials(
        None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=_env("GOOGLE_CLIENT_ID"),
        client_secret=_env("GOOGLE_CLIENT_SECRET"),
        scopes=SCOPES,
    )
    if not creds.valid:
        creds.refresh(Request())
    return build("gmail", "v1", credentials=creds)


# ---------------------------------------------------------------- parsing

_COMPANY_PATTERNS = [
    re.compile(r"careers?\s+at\s+(.+)", re.I),
    re.compile(r"(.+?)\s+careers?\b", re.I),
    re.compile(r"(.+?)\s+(hiring|talent|recruiting|people)\s+team\b", re.I),
    re.compile(r"(.+?)\s+hr\b", re.I),
    re.compile(r"(.+?)\s+jobs\b", re.I),
]


def _clean_company(name: str) -> str:
    name = re.sub(r"\s+", " ", name).strip(" -–—|")
    name = re.sub(r"(?i)\s+(pvt\.?|private|limited|ltd\.?|inc\.?|llc\.?|technologies|technology|solutions)$", "", name).strip()
    return name


def company_from_address(display: str, email: str) -> str:
    """Best-effort company name from a From/To header."""
    display = (display or "").strip()
    for pat in _COMPANY_PATTERNS:
        m = pat.search(display)
        if m:
            cleaned = _clean_company(m.group(1))
            if len(cleaned) > 1:
                return cleaned
    if display and "@" not in display:
        cleaned = _clean_company(
            re.sub(r"(?i)\s*(no[\s-]?reply|donotreply|notification|alert)s?$", "", display)
        )
        if len(cleaned) > 1:
            return cleaned
    domain = (email or "").split("@")[-1].lower().strip()
    if domain and "." in domain and domain not in ATS_DOMAINS:
        base = domain.split(".")[0]
        if base not in PERSONAL_DOMAINS and len(base) > 1:
            return _clean_company(base.replace("-", " ").title())
    return ""


_ROLE_PATTERNS = [
    re.compile(r"application for[:\s]+(.+?)(?:\s+at\s+|\s*[-|–]\s*|\s*$)", re.I),
    re.compile(r"applying for[:\s]+(.+?)(?:\s+at\s+|\s*[-|–]\s*|\s*$)", re.I),
    re.compile(r"your application[:\s]+(.+?)(?:\s+at\s+|\s*[-|–]\s*|\s*$)", re.I),
    re.compile(r"re:\s*(.+?)\s+application", re.I),
]


def role_from_subject(subject: str) -> str:
    subject = subject or ""
    for pat in _ROLE_PATTERNS:
        m = pat.search(subject)
        if m:
            role = m.group(1).strip(" -–—:|")
            if len(role) > 2 and "thank" not in role.lower():
                return role[:120]
    return "Unknown role"


def _parse_date(value: str):
    try:
        return parsedate_to_datetime(value).date()
    except Exception:
        return None


# ---------------------------------------------------------------- scanning

# Confirmation emails from ATS / company inboxes.
CONFIRM_Q = (
    'newer_than:90d ("thank you for applying" OR "thanks for applying" '
    'OR "application received" OR "we have received your application" '
    'OR "your application has been received" OR "application submitted")'
)
# Outreach the user sent themselves.
SENT_Q = 'in:sent newer_than:90d ("applying for" OR "application for the position" OR "application for internship")'


def _headers(service, msg_id: str) -> dict:
    msg = (
        service.users()
        .messages()
        .get(
            userId="me",
            id=msg_id,
            format="metadata",
            metadataHeaders=["From", "To", "Subject", "Date"],
        )
        .execute()
    )
    return {
        h["name"].lower(): h["value"]
        for h in msg.get("payload", {}).get("headers", [])
    }


def scan(service) -> list[dict]:
    """Return candidate applications found in Gmail."""
    found: list[dict] = []
    seen: set[str] = set()
    for query, is_sent in ((CONFIRM_Q, False), (SENT_Q, True)):
        try:
            resp = service.users().messages().list(userId="me", q=query, maxResults=40).execute()
        except Exception:
            continue
        for item in resp.get("messages", []):
            mid = item["id"]
            if mid in seen:
                continue
            seen.add(mid)
            try:
                h = _headers(service, mid)
            except Exception:
                continue
            header = h.get("to", "") if is_sent else h.get("from", "")
            display, addr = parseaddr(header)
            company = company_from_address(display, addr)
            if not company:
                continue
            subject = h.get("subject", "")
            found.append(
                {
                    "company": company,
                    "role": role_from_subject(subject),
                    "applied_date": _parse_date(h.get("date", "")),
                    "subject": subject[:200],
                    "correspondent": header[:200],
                }
            )
    return found
