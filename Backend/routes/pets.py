from flask import Blueprint, request, jsonify, session
from models.db import get_db
from utils import log_action

pets_bp = Blueprint('pets', __name__)

@pets_bp.route('/pets', methods=['GET'])
def get_pets():
    if 'user_id' not in session:
        return jsonify({"error": "Authentication required", "code": "AUTH_REQUIRED"}), 401

    try:
        user_id = session['user_id']
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        offset = (page - 1) * per_page

        db = get_db()
        pets = db.execute('''
            SELECT id, name, breed, category, age, gender, avatar, bio, created_at, updated_at
            FROM pets 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
        ''', (user_id, per_page, offset)).fetchall()

        total = db.execute('SELECT COUNT(*) FROM pets WHERE user_id = ?', (user_id,)).fetchone()[0]

        return jsonify({
            "success": True,
            "data": [dict(pet) for pet in pets],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@pets_bp.route('/pets', methods=['POST'])
def add_pet():
    if 'user_id' not in session:
        return jsonify({"error": "Authentication required", "code": "AUTH_REQUIRED"}), 401

    try:
        user_id = session['user_id']
        data = request.get_json()

        name = data.get('name')
        if not name:
            return jsonify({"error": "Pet name is required"}), 400

        db = get_db()
        db.execute('''
            INSERT INTO pets (user_id, name, breed, category, age, gender, bio)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, name, data.get('breed'), data.get('category'), 
              data.get('age'), data.get('gender'), data.get('bio')))
        db.commit()

        pet_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
        pet = db.execute('SELECT * FROM pets WHERE id = ?', (pet_id,)).fetchone()

        log_action(db, user_id, 'add_pet', {'name': name, 'breed': data.get('breed')})

        return jsonify({
            "success": True,
            "message": "Pet added successfully",
            "pet": dict(pet)
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@pets_bp.route('/pets/<int:pet_id>', methods=['GET'])
def get_pet(pet_id):
    if 'user_id' not in session:
        return jsonify({"error": "Authentication required", "code": "AUTH_REQUIRED"}), 401

    try:
        user_id = session['user_id']
        db = get_db()
        
        pet = db.execute('SELECT * FROM pets WHERE id = ? AND user_id = ?', (pet_id, user_id)).fetchone()
        
        if not pet:
            return jsonify({"error": "Pet not found"}), 404

        return jsonify({"success": True, "pet": dict(pet)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@pets_bp.route('/pets/<int:pet_id>', methods=['PUT'])
def update_pet(pet_id):
    if 'user_id' not in session:
        return jsonify({"error": "Authentication required", "code": "AUTH_REQUIRED"}), 401

    try:
        user_id = session['user_id']
        data = request.get_json()
        db = get_db()

        pet = db.execute('SELECT * FROM pets WHERE id = ? AND user_id = ?', (pet_id, user_id)).fetchone()
        if not pet:
            return jsonify({"error": "Pet not found"}), 404

        updates = []
        params = []

        if 'name' in data:
            updates.append('name = ?')
            params.append(data['name'])
        if 'breed' in data:
            updates.append('breed = ?')
            params.append(data['breed'])
        if 'category' in data:
            updates.append('category = ?')
            params.append(data['category'])
        if 'age' in data:
            updates.append('age = ?')
            params.append(data['age'])
        if 'gender' in data:
            updates.append('gender = ?')
            params.append(data['gender'])
        if 'bio' in data:
            updates.append('bio = ?')
            params.append(data['bio'])
        
        updates.append('updated_at = CURRENT_TIMESTAMP')

        if updates:
            params.append(pet_id)
            db.execute(f'UPDATE pets SET {", ".join(updates)} WHERE id = ?', params)
            db.commit()

        log_action(db, user_id, 'update_pet', {'pet_id': pet_id})

        return jsonify({"success": True, "message": "Pet updated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@pets_bp.route('/pets/<int:pet_id>', methods=['DELETE'])
def delete_pet(pet_id):
    if 'user_id' not in session:
        return jsonify({"error": "Authentication required", "code": "AUTH_REQUIRED"}), 401

    try:
        user_id = session['user_id']
        db = get_db()

        pet = db.execute('SELECT * FROM pets WHERE id = ? AND user_id = ?', (pet_id, user_id)).fetchone()
        if not pet:
            return jsonify({"error": "Pet not found"}), 404

        db.execute('DELETE FROM pets WHERE id = ?', (pet_id,))
        db.commit()

        log_action(db, user_id, 'delete_pet', {'pet_id': pet_id})

        return jsonify({"success": True, "message": "Pet deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500