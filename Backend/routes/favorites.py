from flask import Blueprint, request, jsonify, session
from models.db import get_db
from utils import log_action

favorites_bp = Blueprint('favorites', __name__)

@favorites_bp.route('/favorites', methods=['GET'])
def get_favorites():
    if 'user_id' not in session:
        return jsonify({"error": "Authentication required", "code": "AUTH_REQUIRED"}), 401

    try:
        user_id = session['user_id']
        db = get_db()
        
        favorites = db.execute('''
            SELECT f.breed, f.created_at, b.category, b.origin, b.personality
            FROM favorites f
            LEFT JOIN breed_info b ON f.breed = b.breed
            WHERE f.user_id = ?
            ORDER BY f.created_at DESC
        ''', (user_id,)).fetchall()

        return jsonify({
            "success": True,
            "data": [dict(f) for f in favorites]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@favorites_bp.route('/favorites', methods=['POST'])
def add_favorite():
    if 'user_id' not in session:
        return jsonify({"error": "Authentication required", "code": "AUTH_REQUIRED"}), 401

    try:
        user_id = session['user_id']
        data = request.get_json()
        breed = data.get('breed')

        if not breed:
            return jsonify({"error": "Breed is required"}), 400

        db = get_db()
        
        try:
            db.execute('INSERT INTO favorites (user_id, breed) VALUES (?, ?)', (user_id, breed))
            db.execute('UPDATE breed_info SET likes = likes + 1 WHERE breed = ?', (breed,))
            db.commit()
        except Exception:
            db.rollback()
            return jsonify({"error": "Already favorited"}), 409

        log_action(db, user_id, 'add_favorite', {'breed': breed})

        return jsonify({"success": True, "message": "Added to favorites"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@favorites_bp.route('/favorites/<breed>', methods=['DELETE'])
def remove_favorite(breed):
    if 'user_id' not in session:
        return jsonify({"error": "Authentication required", "code": "AUTH_REQUIRED"}), 401

    try:
        user_id = session['user_id']
        db = get_db()

        favorite = db.execute('SELECT * FROM favorites WHERE user_id = ? AND breed = ?', (user_id, breed)).fetchone()
        if not favorite:
            return jsonify({"error": "Favorite not found"}), 404

        db.execute('DELETE FROM favorites WHERE user_id = ? AND breed = ?', (user_id, breed))
        db.execute('UPDATE breed_info SET likes = MAX(0, likes - 1) WHERE breed = ?', (breed,))
        db.commit()

        log_action(db, user_id, 'remove_favorite', {'breed': breed})

        return jsonify({"success": True, "message": "Removed from favorites"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500