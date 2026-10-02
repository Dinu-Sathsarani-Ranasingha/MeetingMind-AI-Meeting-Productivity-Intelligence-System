"""
MeetingMind AI - Test Suite
============================
Tests all three NLP modules using realistic meeting note samples.
Run: python tests/test_nlp.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nlp.analyzer import analyze_meeting
from nlp.action_extractor import extract_action_items
from nlp.scorer import score_meeting
from nlp.pattern_detector import detect_recurring_issues

# ── Sample Meeting Notes ─────────────────────────────────────────────────────

GOOD_MEETING = """
Agenda: Sprint 23 Planning — Engineering Team
Date: 2026-05-25

Topics discussed:
1. API performance issues in the payment module
2. New feature rollout plan for Q3
3. Team capacity for the upcoming sprint

Decisions made:
The team agreed to prioritize the payment API fix before any new feature work.
It was confirmed that the Q3 roadmap will be finalized by end of this week.
Leadership approved the budget for the new testing infrastructure.

Action Items:
- John will investigate the payment API timeout issue by Friday.
- Sarah needs to update the Q3 roadmap document and share it with the team by Thursday.
- Michael should schedule a 1:1 with each team member this week to discuss capacity.
- The backend team must deploy the hotfix to staging by end of day today.
- Lisa agreed to prepare the testing infrastructure proposal by next Monday.

Next meeting: Monday 9am — Sprint 23 kickoff
"""

POOR_MEETING = """
We talked about the project stuff. 
Things seem to be going okay but there are some concerns.
Maybe someone should look at the issues.
We will think about the next steps.
"""

MEDIUM_MEETING = """
Meeting notes — Product team

We discussed the login bug that has been affecting mobile users.
The team reviewed the latest analytics dashboard numbers.
It was decided that we need to fix the login issue as soon as possible.
Ravi will look into the authentication service and report back.
We also talked about the upcoming product demo next week.
The demo should be ready by end of this sprint.
"""

# ── History for recurring issue testing ─────────────────────────────────────

MEETING_HISTORY = [
    {
        "id": "mtg_001",
        "date": "2026-05-05",
        "text": "We discussed the login bug again. Authentication service is still down. "
                "Performance issues with the API were also mentioned. Need to fix urgently.",
    },
    {
        "id": "mtg_002",
        "date": "2026-05-12",
        "text": "Login issues came up again. The authentication service needs attention. "
                "Backend performance continues to be a concern.",
    },
    {
        "id": "mtg_003",
        "date": "2026-05-19",
        "text": "Still dealing with login problems and authentication failures. "
                "Performance degradation reported by multiple users.",
    },
]


# ── Test Functions ───────────────────────────────────────────────────────────

def print_header(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def print_section(title: str):
    print(f"\n── {title} ──────────────────────────────────")


def test_action_extraction():
    print_header("TEST 1: Action Item Extraction")

    print_section("Good meeting notes")
    items = extract_action_items(GOOD_MEETING)
    print(f"Found {len(items)} action items:\n")
    for i, item in enumerate(items, 1):
        print(f"  {i}. Task:     {item['task'][:75]}...")
        print(f"     Owner:    {item['owner'] or 'Not assigned'}")
        print(f"     Deadline: {item['deadline'] or 'Not specified'}")
        print(f"     Priority: {item['priority']}")
        print()

    print_section("Poor meeting notes")
    items_poor = extract_action_items(POOR_MEETING)
    print(f"Found {len(items_poor)} action items (expected: 0-1)")

    assert len(items) >= 3, f"Expected ≥3 action items in good meeting, got {len(items)}"
    print("✓ Action extraction test passed")


def test_scoring():
    print_header("TEST 2: Meeting Effectiveness Scoring")

    for label, text in [("Good", GOOD_MEETING), ("Medium", MEDIUM_MEETING), ("Poor", POOR_MEETING)]:
        items = extract_action_items(text)
        result = score_meeting(text, items)

        print(f"\n  [{label} meeting]")
        print(f"  Score: {result['score']}/100 — {result['grade']['label']} ({result['grade']['color']})")
        print(f"  Breakdown:")
        for b in result["breakdown"]:
            bar = "█" * b["points"] + "░" * (b["max"] - b["points"])
            print(f"    {b['criterion'][:35]:<35} {b['points']:>3}/{b['max']} {bar}")
            print(f"    → {b['note']}")

    # Assertions
    good_items = extract_action_items(GOOD_MEETING)
    good_score = score_meeting(GOOD_MEETING, good_items)
    poor_items = extract_action_items(POOR_MEETING)
    poor_score = score_meeting(POOR_MEETING, poor_items)

    assert good_score["score"] > poor_score["score"], "Good meeting should score higher than poor meeting"
    assert good_score["score"] >= 50, f"Good meeting should score ≥50, got {good_score['score']}"
    print("\n✓ Scoring test passed")


def test_recurring_detection():
    print_header("TEST 3: Recurring Issue Detection")

    current = """
    Login issues are still occurring. Authentication service is down again.
    Performance problems continue to affect users. Need immediate action.
    """

    flagged = detect_recurring_issues(current, MEETING_HISTORY)

    print(f"\n  Detected {len(flagged)} recurring issue(s):\n")
    for issue in flagged:
        print(f"  • Topic:       '{issue['topic']}'")
        print(f"    Appearances: {issue['appearances']} meetings")
        print(f"    Last seen:   {issue['last_seen']}")
        print(f"    Severity:    {issue['severity']}")
        print()

    assert len(flagged) >= 1, "Should detect at least 1 recurring issue"
    print("✓ Recurring detection test passed")


def test_full_pipeline():
    print_header("TEST 4: Full Analysis Pipeline")

    result = analyze_meeting(
        text=MEDIUM_MEETING,
        meeting_history=MEETING_HISTORY,
        meeting_id="test_mtg_001",
    )

    print(f"\n  Meeting ID:    {result['meeting_id']}")
    print(f"  Word count:    {result['word_count']}")
    print(f"  Score:         {result['score']['score']}/100 ({result['score']['grade']['label']})")
    print(f"  Action items:  {result['action_item_count']}")
    print(f"  Recurring:     {len(result['recurring_issues'])} issues")
    print(f"\n  Summary:\n  {result['summary']}")
    print(f"\n  Recurring summary:\n  {result['recurring_summary']}")

    assert "score" in result
    assert "action_items" in result
    assert "recurring_issues" in result
    assert "summary" in result
    print("\n✓ Full pipeline test passed")


def test_edge_cases():
    print_header("TEST 5: Edge Cases")

    # Empty input
    result = analyze_meeting("")
    assert "error" in result, "Should return error for empty input"
    print("  ✓ Empty input handled")

    # Very short input
    items = extract_action_items("ok")
    assert items == [], "Too-short sentences should return no items"
    print("  ✓ Very short input handled")

    # No history
    result = analyze_meeting(GOOD_MEETING, meeting_history=None)
    assert result["recurring_issues"] == [], "No history should return no recurring issues"
    print("  ✓ Missing history handled")

    print("\n✓ Edge case tests passed")


# ── Run all tests ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n🧠 MeetingMind AI — NLP Engine Test Suite")
    print("Phase 2: Testing all NLP modules\n")

    try:
        test_action_extraction()
        test_scoring()
        test_recurring_detection()
        test_full_pipeline()
        test_edge_cases()

        print("\n" + "="*60)
        print("  ✅  ALL TESTS PASSED — Phase 2 NLP Engine is ready!")
        print("="*60 + "\n")

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
