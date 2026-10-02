"""
MeetingMind AI - Authentication Routes
========================================
POST /api/auth/register   → create new account
POST /api/auth/login      → login and get JWT token
GET  /api/auth/me         → get current user profile
"""

import re
import bcrypt
from flask import Blueprint, request, jsonify
from ..database import get_db
from ..middleware.auth import generate_token, require_auth

auth_bp = Blueprint("auth", __name__)


def _validate_email(email: str) -> bool:
    return bool(re.match(r"^[^@]+@[^@]+\.[^@]+$", email))


# ── POST /api/auth/register ──────────────────────────────────────────────────
@auth_bp.route("/register", methods=["POST"])
def register():
    """Register a new user account."""
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body is required"}), 400

    name     = (data.get("name") or "").strip()
    email    = (data.get("email") or "").strip().lower()
    password = (data.get("password") or "").strip()
    team     = (data.get("team") or "").strip()
    role     = (data.get("role") or "member").strip()  # member | manager | admin

    # Validation
    if not name:
        return jsonify({"error": "Name is required"}), 400
    if not email or not _validate_email(email):
        return jsonify({"error": "A valid email address is required"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    db = get_db()

    # Check if email already exists
    if db.find_user_by_email(email):
        return jsonify({"error": "An account with this email already exists"}), 409

    # Hash password
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    user = db.create_user({
        "name":     name,
        "email":    email,
        "password": hashed,
        "team":     team,
        "role":     role,
    })

    token = generate_token(user["_id"], user["email"])

    return jsonify({
        "message": "Account created successfully",
        "token":   token,
        "user": {
            "id":    user["_id"],
            "name":  user["name"],
            "email": user["email"],
            "team":  user["team"],
            "role":  user["role"],
        }
    }), 201


# ── POST /api/auth/login ─────────────────────────────────────────────────────
@auth_bp.route("/login", methods=["POST"])
def login():
    """Login and receive a JWT token."""
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body is required"}), 400

    email    = (data.get("email") or "").strip().lower()
    password = (data.get("password") or "").strip()

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    db   = get_db()
    user = db.find_user_by_email(email)

    if not user or not bcrypt.checkpw(password.encode(), user["password"].encode()):
        return jsonify({"error": "Invalid email or password"}), 401

    token = generate_token(user["_id"], user["email"])

    return jsonify({
        "message": "Login successful",
        "token": token,
        "user": {
            "id":    user["_id"],
            "name":  user["name"],
            "email": user["email"],
            "team":  user["team"],
            "role":  user["role"],
        }
    }), 200


# ── GET /api/auth/me ─────────────────────────────────────────────────────────
@auth_bp.route("/me", methods=["GET"])
@require_auth
def get_me(current_user):
    """Return the currently authenticated user's profile."""
    db   = get_db()
    user = db.find_user_by_id(current_user["user_id"])

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "id":         user["_id"],
        "name":       user["name"],
        "email":      user["email"],
        "team":       user["team"],
        "role":       user["role"],
        "created_at": user.get("created_at"),
    }), 200
