"""
MeetingMind AI - Meeting Effectiveness Scorer
===============================================
Calculates a 0-100 effectiveness score for a meeting based on
weighted criteria aligned with the BA document (Phase 1, Section 5.2).

Scoring weights:
    Action items with owners   → 30 pts
    Decisions documented       → 25 pts
    Deadlines assigned         → 20 pts
    Clear agenda present       → 15 pts
    No recurring issues        → 10 pts  (passed in from pattern detector)
"""

import re


# ── Decision Keywords ────────────────────────────────────────────────────────
DECISION_PATTERNS = re.compile(
    r"\b(decided|agreed|confirmed|approved|resolved|conclusion|we will|team will|"
    r"going with|chosen|selected|finalised|finalized|consensus|accepted|rejected)\b",
    re.IGNORECASE,
)

# ── Agenda Keywords ──────────────────────────────────────────────────────────
AGENDA_PATTERNS = re.compile(
    r"\b(agenda|meeting agenda|today['']?s? (agenda|topics?|goals?|objectives?)|"
    r"topics? (to (cover|discuss|address))|purpose of (this|today['']?s?) meeting|"
    r"items? (for discussion|to discuss)|discussion points?)\b",
    re.IGNORECASE,
)

# ── Deadline Keywords (for scoring) ─────────────────────────────────────────
DEADLINE_SCORE_PATTERN = re.compile(
    r"\b(by|before|due|until|deadline|no later than|eod|eow|end of (week|day|month|sprint))\b",
    re.IGNORECASE,
)

# ── Owner Assignment Keywords ────────────────────────────────────────────────
OWNER_SCORE_PATTERN = re.compile(
    r"\b(assigned to|action for|will|shall|responsible|owner|@[A-Za-z])\b",
    re.IGNORECASE,
)


def _score_action_items(action_items: list[dict]) -> tuple[int, str]:
    """
    Score: 30 pts if ≥1 action item has a named owner.
    Partial credit: 15 pts if action items exist but no owners named.
    """
    if not action_items:
        return 0, "No action items detected"

    with_owners = [a for a in action_items if a.get("owner")]
    ratio = len(with_owners) / len(action_items)

    if ratio >= 0.7:
        return 30, f"{len(with_owners)}/{len(action_items)} action items have named owners"
    elif ratio >= 0.3:
        return 20, f"{len(with_owners)}/{len(action_items)} action items have named owners (partial)"
    elif action_items:
        return 10, "Action items found but no owners assigned"
    return 0, "No action items detected"


def _score_decisions(text: str) -> tuple[int, str]:
    """Score: 25 pts based on number of decision keywords found."""
    matches = DECISION_PATTERNS.findall(text)
    unique = set(m.lower() for m in matches)
    count = len(unique)

    if count >= 3:
        return 25, f"{count} distinct decision keywords found"
    elif count == 2:
        return 18, f"{count} decision keywords found"
    elif count == 1:
        return 10, f"{count} decision keyword found"
    return 0, "No decisions documented"


def _score_deadlines(action_items: list[dict], text: str) -> tuple[int, str]:
    """Score: 20 pts if deadlines appear in action items or text."""
    items_with_deadlines = [a for a in action_items if a.get("deadline")]

    if items_with_deadlines:
        ratio = len(items_with_deadlines) / max(len(action_items), 1)
        if ratio >= 0.5:
            return 20, f"{len(items_with_deadlines)} action items have deadlines"
        return 12, f"{len(items_with_deadlines)} action items have deadlines (partial)"

    # Fall back to raw text scan
    if DEADLINE_SCORE_PATTERN.search(text):
        return 8, "Deadline language present but not linked to specific tasks"
    return 0, "No deadlines assigned"


def _score_agenda(text: str) -> tuple[int, str]:
    """Score: 15 pts if agenda/purpose language is present."""
    if AGENDA_PATTERNS.search(text):
        return 15, "Meeting agenda or purpose is documented"
    return 0, "No agenda or meeting purpose detected"


def _score_recurring(has_recurring_issues: bool) -> tuple[int, str]:
    """Score: 10 pts if no recurring issues flagged."""
    if not has_recurring_issues:
        return 10, "No recurring unresolved issues detected"
    return 0, "Recurring issues detected from past meetings"


def _grade(score: int) -> dict:
    """Convert numeric score to a grade label and colour."""
    if score >= 80:
        return {"label": "Excellent", "color": "green"}
    elif score >= 60:
        return {"label": "Good", "color": "teal"}
    elif score >= 40:
        return {"label": "Fair", "color": "amber"}
    else:
        return {"label": "Poor", "color": "red"}


def score_meeting(
    text: str,
    action_items: list[dict],
    has_recurring_issues: bool = False,
) -> dict:
    """
    Calculate the overall Meeting Effectiveness Score.

    Args:
        text:                 Raw meeting notes text.
        action_items:         List of action items from action_extractor.
        has_recurring_issues: True if pattern detector flagged recurring topics.

    Returns:
        {
            "score":      int (0–100),
            "grade":      dict {label, color},
            "breakdown":  list of {criterion, points, max, note}
        }
    """
    s1, n1 = _score_action_items(action_items)
    s2, n2 = _score_decisions(text)
    s3, n3 = _score_deadlines(action_items, text)
    s4, n4 = _score_agenda(text)
    s5, n5 = _score_recurring(has_recurring_issues)

    total = s1 + s2 + s3 + s4 + s5

    breakdown = [
        {"criterion": "Action items with named owners", "points": s1, "max": 30, "note": n1},
        {"criterion": "Decisions documented",           "points": s2, "max": 25, "note": n2},
        {"criterion": "Deadlines assigned to tasks",    "points": s3, "max": 20, "note": n3},
        {"criterion": "Clear agenda present",           "points": s4, "max": 15, "note": n4},
        {"criterion": "No recurring issues",            "points": s5, "max": 10, "note": n5},
    ]

    return {
        "score":     total,
        "grade":     _grade(total),
        "breakdown": breakdown,
    }
