"""
MeetingMind AI - Analytics Routes
====================================
GET /api/analytics/dashboard     → summary stats for the user's dashboard
GET /api/analytics/trend         → score trend over time
GET /api/analytics/recurring     → top recurring issues across all meetings
GET /api/analytics/action-stats  → action item completion rates
"""

from flask import Blueprint, request, jsonify
from ..database import get_db
from ..middleware.auth import require_auth
from collections import Counter

analytics_bp = Blueprint("analytics", __name__)


def _get_user_meetings(current_user: dict, team_id: str = "") -> list[dict]:
    """Helper: fetch all meetings for a user or team."""
    db = get_db()
    if team_id:
        return db.get_meetings_by_team(team_id)
    return db.get_meetings_by_user(current_user["user_id"])


# ── GET /api/analytics/dashboard ────────────────────────────────────────────
@analytics_bp.route("/dashboard", methods=["GET"])
@require_auth
def dashboard_stats(current_user):
    """
    Return summary statistics for the main dashboard card row.
    {
        total_meetings, avg_score, total_action_items,
        completed_actions, completion_rate, recurring_count,
        latest_score, score_trend (up/down/stable)
    }
    """
    team_id  = request.args.get("team_id", "")
    meetings = _get_user_meetings(current_user, team_id)

    if not meetings:
        return jsonify({
            "success": True,
            "stats": {
                "total_meetings":    0,
                "avg_score":         0,
                "total_action_items": 0,
                "completed_actions": 0,
                "completion_rate":   0,
                "recurring_count":   0,
                "latest_score":      0,
                "score_trend":       "stable",
            }
        }), 200

    scores       = [m.get("score", {}).get("score", 0) for m in meetings]
    avg_score    = round(sum(scores) / len(scores), 1)
    latest_score = scores[0] if scores else 0

    # Score trend: compare last meeting vs previous
    if len(scores) >= 2:
        diff = scores[0] - scores[1]
        trend = "up" if diff > 5 else ("down" if diff < -5 else "stable")
    else:
        trend = "stable"

    # Action items
    all_items     = [item for m in meetings for item in m.get("action_items", [])]
    completed     = [i for i in all_items if i.get("completed")]
    completion_rate = round(len(completed) / len(all_items) * 100) if all_items else 0

    # Recurring issues (across all meetings, deduplicated)
    all_recurring  = [r["topic"] for m in meetings for r in m.get("recurring_issues", [])]
    unique_recurring = len(set(all_recurring))

    return jsonify({
        "success": True,
        "stats": {
            "total_meetings":     len(meetings),
            "avg_score":          avg_score,
            "total_action_items": len(all_items),
            "completed_actions":  len(completed),
            "completion_rate":    completion_rate,
            "recurring_count":    unique_recurring,
            "latest_score":       latest_score,
            "score_trend":        trend,
        }
    }), 200


# ── GET /api/analytics/trend ─────────────────────────────────────────────────
@analytics_bp.route("/trend", methods=["GET"])
@require_auth
def score_trend(current_user):
    """
    Return meeting scores over time for a line chart.
    [{ date, score, grade, title }, ...]  sorted oldest → newest
    """
    team_id  = request.args.get("team_id", "")
    limit    = int(request.args.get("limit", 20))
    meetings = _get_user_meetings(current_user, team_id)

    # Sort oldest first for the chart
    meetings.sort(key=lambda m: m.get("saved_at", ""))
    meetings = meetings[-limit:]  # last N meetings

    trend_data = [
        {
            "meeting_id": m.get("meeting_id"),
            "title":      m.get("title", "Untitled"),
            "date":       m.get("date") or m.get("saved_at", "")[:10],
            "score":      m.get("score", {}).get("score", 0),
            "grade":      m.get("score", {}).get("grade", {}).get("label", ""),
        }
        for m in meetings
    ]

    return jsonify({
        "success":    True,
        "trend_data": trend_data,
        "count":      len(trend_data),
    }), 200


# ── GET /api/analytics/recurring ─────────────────────────────────────────────
@analytics_bp.route("/recurring", methods=["GET"])
@require_auth
def top_recurring(current_user):
    """
    Return the top recurring issues across all meetings.
    [{ topic, total_appearances, severity, last_seen }, ...]
    """
    team_id  = request.args.get("team_id", "")
    meetings = _get_user_meetings(current_user, team_id)

    topic_counter: dict[str, dict] = {}

    for m in meetings:
        for issue in m.get("recurring_issues", []):
            topic = issue["topic"]
            if topic not in topic_counter:
                topic_counter[topic] = {
                    "topic":             topic,
                    "total_appearances": 0,
                    "severity":          issue.get("severity", "Medium"),
                    "last_seen":         issue.get("last_seen", ""),
                }
            topic_counter[topic]["total_appearances"] += issue.get("appearances", 1)
            # Keep the most recent last_seen
            if issue.get("last_seen", "") > topic_counter[topic]["last_seen"]:
                topic_counter[topic]["last_seen"] = issue["last_seen"]

    top = sorted(topic_counter.values(), key=lambda x: x["total_appearances"], reverse=True)[:10]

    return jsonify({
        "success":         True,
        "recurring_issues": top,
        "count":           len(top),
    }), 200


# ── GET /api/analytics/action-stats ──────────────────────────────────────────
@analytics_bp.route("/action-stats", methods=["GET"])
@require_auth
def action_stats(current_user):
    """
    Return action item statistics broken down by priority and owner.
    Useful for the dashboard's action tracker section.
    """
    team_id  = request.args.get("team_id", "")
    meetings = _get_user_meetings(current_user, team_id)

    all_items = [item for m in meetings for item in m.get("action_items", [])]

    # By priority
    priority_counts = Counter(i.get("priority", "Medium") for i in all_items)

    # By owner
    owner_counts = Counter(
        i.get("owner", "Unassigned") or "Unassigned"
        for i in all_items
    )

    # Completion by priority
    completed_by_priority = Counter(
        i.get("priority", "Medium")
        for i in all_items if i.get("completed")
    )

    return jsonify({
        "success":       True,
        "total":         len(all_items),
        "completed":     sum(1 for i in all_items if i.get("completed")),
        "by_priority": [
            {
                "priority":  p,
                "total":     priority_counts[p],
                "completed": completed_by_priority.get(p, 0),
            }
            for p in ["High", "Medium", "Low"] if p in priority_counts
        ],
        "by_owner": [
            {"owner": owner, "count": count}
            for owner, count in owner_counts.most_common(10)
        ],
    }), 200
