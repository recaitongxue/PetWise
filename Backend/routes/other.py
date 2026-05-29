from flask import Blueprint, request, jsonify, session
from models.db import get_db
from utils import log_action

other_bp = Blueprint('other', __name__)

@other_bp.route('/breed/<breed>', methods=['GET'])
def get_breed_info(breed):
    try:
        db = get_db()
        breed_info = db.execute('SELECT * FROM breed_info WHERE breed = ?', (breed,)).fetchone()

        if not breed_info:
            return jsonify({"error": "Breed not found"}), 404

        comments_count = db.execute('SELECT COUNT(*) FROM comments WHERE breed = ?', (breed,)).fetchone()[0]

        return jsonify({
            "success": True,
            "breed_info": dict(breed_info),
            "comments_count": comments_count
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@other_bp.route('/feedback', methods=['POST'])
def submit_feedback():
    if 'user_id' not in session:
        return jsonify({"error": "Authentication required", "code": "AUTH_REQUIRED"}), 401

    try:
        user_id = session['user_id']
        data = request.get_json()

        feedback_type = data.get('type')
        content = data.get('content')

        if not feedback_type or not content:
            return jsonify({"error": "Type and content are required"}), 400

        db = get_db()
        db.execute('''
            INSERT INTO feedback (user_id, type, content)
            VALUES (?, ?, ?)
        ''', (user_id, feedback_type, content))
        db.commit()

        log_action(db, user_id, 'submit_feedback', {'type': feedback_type})

        return jsonify({"success": True, "message": "Feedback submitted"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@other_bp.route('/health_check', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "PetWise API"})