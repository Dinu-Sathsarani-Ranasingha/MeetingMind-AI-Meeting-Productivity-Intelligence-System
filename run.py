"""
MeetingMind AI - Application Entry Point
==========================================
Run the Flask API server.

Usage:
    python run.py

Environment variables:
    FLASK_DEBUG=true        Enable debug mode
    SECRET_KEY=your-key     JWT secret (change in production!)
    MONGO_URI=mongodb://... MongoDB connection string
    PORT=5000               Port number (default 5000)
"""

import os
import sys

# Add project root to path so NLP modules are importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"

    print("\n" + "="*50)
    print("  🧠 MeetingMind AI — Backend API")
    print("="*50)
    print(f"  Running on: http://localhost:{port}")
    print(f"  Debug mode: {debug}")
    print(f"  Health check: http://localhost:{port}/api/health")
    print("="*50 + "\n")

    app.run(host="0.0.0.0", port=port, debug=debug)
