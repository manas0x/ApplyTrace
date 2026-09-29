"""TF-based keyword matcher. No external APIs — pure stdlib.

Pipeline:
  1. Tokenize + lowercase, strip punctuation.
  2. Drop English stopwords and short tokens.
  3. Score JD terms by term frequency (+ bonus for ALL-CAPS tech acronyms
     like SQL, AWS, REST — common in job descriptions).
  4. Compare top JD keywords against resume keywords.
  5. Score = 100 * (sum of weights of matched keywords) / (sum of weights of all JD keywords).
  6. Missing keywords -> concrete tweak suggestions.
"""
import re
from collections import Counter

STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "then", "else", "when", "while",
    "of", "at", "by", "for", "with", "about", "into", "through", "during",
    "before", "after", "above", "below", "to", "from", "up", "down", "in",
    "out", "on", "off", "over", "under", "again", "further", "once", "here",
    "there", "all", "any", "both", "each", "few", "more", "most", "other",
    "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than",
    "too", "very", "can", "will", "just", "don", "should", "now", "we", "you",
    "your", "our", "us", "they", "their", "them", "he", "she", "it", "its",
    "this", "that", "these", "those", "is", "are", "was", "were", "be", "been",
    "being", "have", "has", "had", "having", "do", "does", "did", "doing",
    "would", "could", "ought", "i", "me", "my", "myself", "we", "who", "whom",
    "what", "which", "where", "how", "why", "as", "between", "per", "within",
    "including", "include", "includes", "including", "looking", "seeking",
    "join", "team", "work", "working", "experience", "year", "years", "strong",
    "good", "great", "excellent", "ability", "skills", "skill", "knowledge",
    "understanding", "familiarity", "plus", "etc", "eg", "ie", "via",
}

# Canonical aliases: resume-side synonyms that count as the same skill.
ALIASES = {
    "react": {"reactjs", "react.js"},
    "javascript": {"js"},
    "typescript": {"ts"},
    "nodejs": {"node", "node.js"},
    "postgresql": {"postgres"},
    "mysql": {"sql"},  # MySQL experience implies SQL, but not vice versa
    "tailwindcss": {"tailwind"},
    "rest": {"restful", "rest-api", "restapi"},
}

# Common tech tokens we keep even though they're short.
KEPT_SHORT = {"c", "c++", "c#", "go", "r", "ai", "ml", "sql", "js", "ts", "ui", "ux", "qa", "aws", "gcp"}


def _normalize(token: str) -> str:
    return token.lower()


def tokenize(text: str) -> list[str]:
    # Keep things like c++, node.js, react.js intact.
    raw = re.findall(r"[a-zA-Z][a-zA-Z0-9.+#]*", text)
    out = []
    for tok in raw:
        t = tok.strip(".").lower()
        if t in KEPT_SHORT or (len(t) > 2 and t not in STOPWORDS):
            out.append(t)
    return out


def _expand(term: str) -> set[str]:
    """All surface forms that count as `term` (aliases included)."""
    forms = {term}
    for canon, alts in ALIASES.items():
        if term == canon or term in alts:
            forms |= {canon} | alts
    return forms


def extract_jd_keywords(jd_text: str, top_n: int = 25) -> list[tuple[str, float]]:
    """Return top JD keywords with TF weights (acronyms get a bonus)."""
    tokens = tokenize(jd_text)
    if not tokens:
        return []
    counts = Counter(tokens)
    total = len(tokens)
    weighted: dict[str, float] = {}
    for term, count in counts.items():
        w = count / total
        if term.isupper() or term in KEPT_SHORT:  # SQL, AWS, REST, CI/CD style tokens
            w *= 1.5
        weighted[term] = w
    # Dedupe alias-collisions: keep the canonical, higher-weighted form.
    merged: dict[str, float] = {}
    for term, w in sorted(weighted.items(), key=lambda kv: -kv[1]):
        canon = term
        for c, alts in ALIASES.items():
            if term == c or term in alts:
                canon = c
                break
        merged[canon] = max(merged.get(canon, 0.0), w)
    return sorted(merged.items(), key=lambda kv: -kv[1])[:top_n]


def analyze(jd_text: str, resume_text: str) -> dict:
    jd_keywords = extract_jd_keywords(jd_text)
    resume_terms = set(tokenize(resume_text))

    matched, missing = [], []
    matched_w = 0.0
    total_w = sum(w for _, w in jd_keywords) or 1.0

    for term, w in jd_keywords:
        if _expand(term) & resume_terms:
            matched.append(term)
            matched_w += w
        else:
            missing.append(term)

    score = round(100 * matched_w / total_w, 1)

    tweaks = []
    for term in missing[:8]:
        if term in KEPT_SHORT or len(term) <= 4:
            tweaks.append(f"Add '{term}' to your skills/projects section if you genuinely have it.")
        else:
            tweaks.append(f"Weave '{term}' into a project bullet or your experience section.")
    if score >= 70:
        tweaks.append("Strong match — apply soon and mention these keywords in your cover note.")
    elif score < 40:
        tweaks.append("Low overlap — consider whether this role fits before spending an application.")

    return {
        "score": score,
        "matched_keywords": matched,
        "missing_keywords": missing,
        "suggested_tweaks": tweaks,
    }
