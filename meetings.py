"""
MeetingMind AI - Meeting Routes
=================================
POST /api/meetings/analyze          → analyze meeting text (NLP)
POST /api/meetings/save             → save analyzed meeting
GET  /api/meetings                  → get all meetings for user
GET  /api/meetings/<meeting_id>     → get single meeting
PUT  /api/meetings/<id>/action/<i>  → mark action item complete/incomplete
DELETE /api/meetings/<meeting_id>   → delete a meeting
"""

import sys
import os

from flask import Blueprint, request, jsonify
from ..database import get_db
from ..middleware.auth import require_auth


def _get_analyzer():
    """Lazy import of NLP analyzer to allow path to be set at runtime."""
    _root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if _root not in sys.path:
        sys.path.insert(0, _root)
    from nlp.analyzer import analyze_meeting
    return analyze_meeting

meetings_bp = Blueprint("meetings", __name__)

MAX_TEXT_LENGTH = 50_000


# ── POST /api/meetings/analyze ───────────────────────────────────────────────
@meetings_bp.route("/analyze", methods=["POST"])
@require_auth
def analyze(current_user):
    """
    Analyze raw meeting notes and return NLP results.
    Does NOT save to the database — call /save to persist.
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body is required"}), 400

    text = (data.get("text") or "").strip()

    if not text:
        return jsonify({"error": "Meeting text is required"}), 400

    if len(text) > MAX_TEXT_LENGTH:
        return jsonify({
            "error": f"Meeting text is too long. Maximum is {MAX_TEXT_LENGTH} characters."
        }), 400

    # Fetch meeting history for recurring issue detection
    db       = get_db()
    team_id  = data.get("team_id") or current_user.get("team", "")
    user_id  = current_user["user_id"]

    if team_id:
        history_records = db.get_meetings_by_team(team_id)
    else:
        history_records = db.get_meetings_by_user(user_id)

    # Format history for NLP engine
    meeting_history = [
        {
            "id":   m.get("meeting_id", m.get("_id")),
            "date": m.get("date", ""),
            "text": m.get("original_text", ""),
        }
        for m in history_records
    ]

    # Run NLP analysis
    analyze_meeting = _get_analyzer()
    result = analyze_meeting(
        text=text,
        meeting_history=meeting_history,
    )

    if "error" in result:
        return jsonify(result), 400

    return jsonify({
        "success": True,
        "analysis": result,
    }), 200


# ── POST /api/meetings/save ──────────────────────────────────────────────────
@meetings_bp.route("/save", methods=["POST"])
@require_auth
def save_meeting(current_user):
    """Save an analyzed meeting to the database."""
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body is required"}), 400

    analysis      = data.get("analysis")
    original_text = data.get("text", "")
    title         = (data.get("title") or "Untitled Meeting").strip()
    date          = data.get("date", "")
    team_id       = data.get("team_id", "")

    if not analysis:
        return jsonify({"error": "Analysis result is required. Run /analyze first."}), 400

    db = get_db()

    meeting_record = {
        "meeting_id":    analysis.get("meeting_id"),
        "title":         title,
        "date":          date,
        "user_id":       current_user["user_id"],
        "team_id":       team_id,
        "original_text": original_text,
        "action_items":  analysis.get("action_items", []),
        "score":         analysis.get("score", {}),
        "recurring_issues": analysis.get("recurring_issues", []),
        "summary":       analysis.get("summary", ""),
        "word_count":    analysis.get("word_count", 0),
    }

    # Add completed flag to each action item
    for item in meeting_record["action_items"]:
        item.setdefault("completed", False)

    saved = db.save_meeting(meeting_record)

    return jsonify({
        "success":    True,
        "message":    "Meeting saved successfully",
        "meeting_id": saved["_id"],
    }), 201


# ── GET /api/meetings ────────────────────────────────────────────────────────
@meetings_bp.route("", methods=["GET"])
@require_auth
def get_meetings(current_user):
    """Return all meetings for the current user, newest first."""
    db       = get_db()
    user_id  = current_user["user_id"]
    team_id  = request.args.get("team_id", "")

    if team_id:
        meetings = db.get_meetings_by_team(team_id)
    else:
        meetings = db.get_meetings_by_user(user_id)

    # Sort newest first
    meetings.sort(key=lambda m: m.get("saved_at", ""), reverse=True)

    # Return summary only (not full text)
    summaries = [
        {
            "meeting_id":       m.get("meeting_id"),
            "title":            m.get("title", "Untitled"),
            "date":             m.get("date", ""),
            "score":            m.get("score", {}).get("score", 0),
            "grade":            m.get("score", {}).get("grade", {}),
            "action_item_count": len(m.get("action_items", [])),
            "recurring_count":  len(m.get("recurring_issues", [])),
            "summary":          m.get("summary", ""),
            "saved_at":         m.get("saved_at", ""),
        }
        for m in meetings
    ]

    return jsonify({
        "success":  True,
        "count":    len(summaries),
        "meetings": summaries,
    }), 200


# ── GET /api/meetings/<meeting_id> ───────────────────────────────────────────
@meetings_bp.route("/<meeting_id>", methods=["GET"])
@require_auth
def get_meeting(current_user, meeting_id):
    """Return a single meeting's full details."""
    db      = get_db()
    meeting = db.get_meeting_by_id(meeting_id)

    if not meeting:
        return jsonify({"error": "Meeting not found"}), 404

    # Ensure user owns this meeting
    if meeting.get("user_id") != current_user["user_id"]:
        return jsonify({"error": "Unauthorized"}), 403

    return jsonify({"success": True, "meeting": meeting}), 200


# ── PUT /api/meetings/<meeting_id>/action/<task_index> ───────────────────────
@meetings_bp.route("/<meeting_id>/action/<int:task_index>", methods=["PUT"])
@require_auth
def update_action_item(current_user, meeting_id, task_index):
    """Mark an action item as completed or incomplete."""
    data      = request.get_json()
    completed = bool(data.get("completed", False)) if data else False

    db      = get_db()
    meeting = db.get_meeting_by_id(meeting_id)

    if not meeting:
        return jsonify({"error": "Meeting not found"}), 404

    if meeting.get("user_id") != current_user["user_id"]:
        return jsonify({"error": "Unauthorized"}), 403

    success = db.update_action_item(meeting_id, task_index, completed)

    if not success:
        return jsonify({"error": "Action item index out of range"}), 400

    return jsonify({
        "success":   True,
        "message":   f"Action item marked as {'completed' if completed else 'incomplete'}",
    }), 200


# ── DELETE /api/meetings/<meeting_id> ────────────────────────────────────────
@meetings_bp.route("/<meeting_id>", methods=["DELETE"])
@require_auth
def delete_meeting(current_user, meeting_id):
    """Delete a meeting record."""
    db      = get_db()
    meeting = db.get_meeting_by_id(meeting_id)

    if not meeting:
        return jsonify({"error": "Meeting not found"}), 404

    if meeting.get("user_id") != current_user["user_id"]:
        return jsonify({"error": "Unauthorized"}), 403

    db.delete_meeting(meeting_id)

    return jsonify({"success": True, "message": "Meeting deleted"}), 200
