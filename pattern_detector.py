"""
MeetingMind AI - Recurring Issue Detector
==========================================
Detects topics that appear repeatedly across multiple meeting records.
A topic is flagged as "recurring" if it appears in 3+ meetings
within a 30-day window — as defined in the BA document (FR-04).
"""

import re
import json
from collections import Counter
from datetime import datetime, timedelta
from nltk.corpus import stopwords
import nltk

nltk.download("stopwords", quiet=True)
nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)

STOP_WORDS = set(stopwords.words("english"))

# Add domain-specific stopwords that don't signal a real issue
EXTRA_STOP = {
    "meeting", "team", "discussed", "update", "updates", "review",
    "follow", "action", "item", "items", "noted", "agreed", "confirmed",
    "please", "also", "make", "sure", "need", "needs", "want", "like",
    "would", "could", "going", "will", "shall", "today", "tomorrow",
    "week", "month", "sprint", "quarter", "point", "points", "agenda",
    "everyone", "anyone", "someone", "people", "person", "time", "next",
}
STOP_WORDS = STOP_WORDS | EXTRA_STOP

# Minimum length for a keyword to be meaningful
MIN_KEYWORD_LEN = 4

# Recurring threshold: topic must appear in this many meetings to be flagged
RECURRING_THRESHOLD = 3

# Window: only consider meetings within the last N days
WINDOW_DAYS = 30


def _extract_keywords(text: str) -> set[str]:
    """
    Extract meaningful keywords from meeting text.
    Removes stop words and short/numeric tokens.
    """
    # Tokenize — simple word split for portability
    tokens = re.findall(r"\b[a-zA-Z]{4,}\b", text.lower())
    keywords = {
        t for t in tokens
        if t not in STOP_WORDS and len(t) >= MIN_KEYWORD_LEN
    }
    return keywords


def _extract_bigrams(text: str) -> set[str]:
    """
    Extract two-word phrases (bigrams) that often represent real issues.
    Example: 'performance issue', 'api timeout', 'login bug'
    """
    words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
    filtered = [w for w in words if w not in STOP_WORDS]
    bigrams = set()
    for i in range(len(filtered) - 1):
        bigram = f"{filtered[i]} {filtered[i+1]}"
        bigrams.add(bigram)
    return bigrams


def detect_recurring_issues(
    current_text: str,
    meeting_history: list[dict],
) -> list[dict]:
    """
    Compare the current meeting's keywords against historical meeting records
    and flag topics that have appeared repeatedly.

    Args:
        current_text:    Raw text of the current meeting being analyzed.
        meeting_history: List of past meeting dicts:
                         [{"date": "YYYY-MM-DD", "text": "...", "id": "..."}, ...]

    Returns:
        List of flagged recurring issues:
        [
            {
                "topic":        str   — the recurring keyword or phrase,
                "appearances":  int   — number of meetings it appeared in,
                "last_seen":    str   — date of most recent appearance,
                "meeting_ids":  list  — IDs of meetings where it appeared,
                "severity":     str   — "High" | "Medium"
            }
        ]
    """
    # Filter history to the last WINDOW_DAYS days
    cutoff = datetime.now() - timedelta(days=WINDOW_DAYS)
    recent_history = []
    for m in meeting_history:
        try:
            d = datetime.strptime(m["date"], "%Y-%m-%d")
            if d >= cutoff:
                recent_history.append(m)
        except (ValueError, KeyError):
            recent_history.append(m)  # include if date is missing

    if not recent_history:
        return []

    # Extract keywords from current meeting
    current_keywords = _extract_keywords(current_text)
    current_bigrams = _extract_bigrams(current_text)
    current_terms = current_keywords | current_bigrams

    # Build a frequency map: term → list of (date, meeting_id) appearances
    term_appearances: dict[str, list[dict]] = {}

    for meeting in recent_history:
        past_keywords = _extract_keywords(meeting.get("text", ""))
        past_bigrams = _extract_bigrams(meeting.get("text", ""))
        past_terms = past_keywords | past_bigrams

        # Only track terms that also appear in the CURRENT meeting
        overlap = current_terms & past_terms

        for term in overlap:
            if term not in term_appearances:
                term_appearances[term] = []
            term_appearances[term].append({
                "date": meeting.get("date", "unknown"),
                "id": meeting.get("id", "unknown"),
            })

    # Flag terms that appear in RECURRING_THRESHOLD+ past meetings
    flagged = []
    seen_topics = set()

    for term, appearances in term_appearances.items():
        if len(appearances) >= RECURRING_THRESHOLD - 1:
            # -1 because we also count the current meeting
            total = len(appearances) + 1
            severity = "High" if total >= 5 else "Medium"

            # Avoid near-duplicate terms (e.g. "bug" and "bugs" as separate issues)
            skip = False
            for seen in seen_topics:
                if term in seen or seen in term:
                    skip = True
                    break
            if skip:
                continue

            seen_topics.add(term)

            # Sort appearances by date to get the most recent
            sorted_app = sorted(appearances, key=lambda x: x["date"], reverse=True)
            last_seen = sorted_app[0]["date"]

            flagged.append({
                "topic":       term,
                "appearances": total,
                "last_seen":   last_seen,
                "meeting_ids": [a["id"] for a in appearances],
                "severity":    severity,
            })

    # Sort by most appearances first
    flagged.sort(key=lambda x: x["appearances"], reverse=True)

    # Return top 10 most recurring issues
    return flagged[:10]


def summarise_recurring(flagged: list[dict]) -> str:
    """
    Generate a plain-English summary of recurring issues.
    Useful for the dashboard and API response.
    """
    if not flagged:
        return "No recurring issues detected in the last 30 days."

    lines = [f"⚠ {len(flagged)} recurring issue(s) detected in the last 30 days:"]
    for issue in flagged:
        lines.append(
            f"  • '{issue['topic']}' appeared in {issue['appearances']} meetings "
            f"(last seen: {issue['last_seen']}) — {issue['severity']} severity"
        )
    return "\n".join(lines)
