"""
MeetingMind AI - Main Analyzer
================================
Combines all three NLP modules into one clean API call:
    1. action_extractor  → extract action items
    2. scorer            → calculate effectiveness score
    3. pattern_detector  → detect recurring issues

Usage:
    from nlp.analyzer import analyze_meeting

    result = analyze_meeting(
        text="Your meeting notes here...",
        meeting_history=[...]   # optional past meetings
    )
"""

from .action_extractor import extract_action_items
from .scorer import score_meeting
from .pattern_detector import detect_recurring_issues, summarise_recurring
from datetime import datetime


def analyze_meeting(
    text: str,
    meeting_history: list[dict] | None = None,
    meeting_id: str | None = None,
) -> dict:
    """
    Full analysis pipeline for a meeting.

    Args:
        text:            Raw meeting notes or transcript.
        meeting_history: Optional list of past meetings for recurring detection.
        meeting_id:      Optional ID for this meeting (used in history tracking).

    Returns:
        Complete analysis result dict ready for the API response.
    """
    if not text or not text.strip():
        return {"error": "Meeting text is empty. Please provide meeting notes."}

    history = meeting_history or []

    # ── Step 1: Extract action items ────────────────────────────────────────
    action_items = extract_action_items(text)

    # ── Step 2: Detect recurring issues ─────────────────────────────────────
    recurring_issues = detect_recurring_issues(text, history)
    has_recurring = len(recurring_issues) > 0

    # ── Step 3: Score the meeting ────────────────────────────────────────────
    score_result = score_meeting(text, action_items, has_recurring)

    # ── Step 4: Generate summary ─────────────────────────────────────────────
    summary = _generate_summary(text, action_items, score_result, recurring_issues)

    return {
        "meeting_id":       meeting_id or _generate_id(),
        "analyzed_at":      datetime.now().isoformat(),
        "word_count":       len(text.split()),
        "action_items":     action_items,
        "action_item_count": len(action_items),
        "score":            score_result,
        "recurring_issues": recurring_issues,
        "recurring_summary": summarise_recurring(recurring_issues),
        "summary":          summary,
    }


def _generate_id() -> str:
    """Generate a simple meeting ID based on timestamp."""
    return f"mtg_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


def _generate_summary(
    text: str,
    action_items: list[dict],
    score_result: dict,
    recurring_issues: list[dict],
) -> str:
    """Generate a plain-English meeting summary for the dashboard."""
    score = score_result["score"]
    grade = score_result["grade"]["label"]
    action_count = len(action_items)
    owned = sum(1 for a in action_items if a.get("owner"))
    with_deadline = sum(1 for a in action_items if a.get("deadline"))
    recurring_count = len(recurring_issues)

    lines = []

    # Score summary
    lines.append(
        f"This meeting scored {score}/100 ({grade}). "
    )

    # Action items summary
    if action_count == 0:
        lines.append("No action items were detected.")
    elif action_count == 1:
        lines.append(
            f"1 action item was identified"
            + (f" assigned to {action_items[0]['owner']}." if action_items[0].get("owner") else ".")
        )
    else:
        lines.append(
            f"{action_count} action items were identified. "
            f"{owned} have named owners and {with_deadline} have deadlines."
        )

    # Recurring issues
    if recurring_count > 0:
        topics = ", ".join(f"'{r['topic']}'" for r in recurring_issues[:3])
        lines.append(
            f"⚠ {recurring_count} recurring topic(s) flagged: {topics}. "
            f"Consider addressing root causes in your next session."
        )

    # Improvement tip based on lowest scoring criterion
    lowest = min(score_result["breakdown"], key=lambda x: x["points"] / x["max"])
    if lowest["points"] < lowest["max"]:
        lines.append(f"Tip: Improve '{lowest['criterion']}' to boost your score.")

    return " ".join(lines)
