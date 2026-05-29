from flask import Blueprint, request, jsonify, session
from models.db import get_db, init_db
from utils import hash_password, verify_password, log_action

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')

        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400

        if len(password) < 6:
            return jsonify({"error": "Password must be at least 6 characters"}), 400

        db = get_db()
        
        if db.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone():
            return jsonify({"error": "Username already exists"}), 409

        if email and db.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone():
            return jsonify({"error": "Email already exists"}), 409

        role = 'admin' if username.lower() == 'admin' else 'user'
        password_hash = hash_password(password)

        db.execute('''
            INSERT INTO users (username, password_hash, email, role)
            VALUES (?, ?, ?, ?)
        ''', (username, password_hash, email, role))
        db.commit()

        user = db.execute('SELECT id, username, role FROM users WHERE username = ?', (username,)).fetchone()

        return jsonify({
            "success": True,
            "message": "Registration successful",
            "user": {
                "id": user['id'],
                "username": user['username'],
                "role": user['role']
            }
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400

        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()

        if not user or not verify_password(password, user['password_hash']):
            return jsonify({"error": "Invalid credentials", "code": "INVALID_TOKEN"}), 401

        if user['is_active'] != 1:
            return jsonify({"error": "Account is disabled"}), 403

        db.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?', (user['id'],))
        db.commit()

        session['user_id'] = user['id']
        session['role'] = user['role']

        log_action(db, user['id'], 'login', {'username': username})

        return jsonify({
            "success": True,
            "message": "Login successful",
            "token": str(user['id']),
            "user": {
                "id": user['id'],
                "username": user['username'],
                "email": user['email'],
                "role": user['role'],
                "avatar": user['avatar'],
                "bio": user['bio']
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"success": True, "message": "Logout successful"})

@auth_bp.route('/profile', methods=['GET'])
def get_profile():
    if 'user_id' not in session:
        return jsonify({"error": "Authentication required", "code": "AUTH_REQUIRED"}), 401

    try:
        user_id = session['user_id']
        db = get_db()
        user = db.execute('SELECT id, username, email, role, avatar, bio, created_at, last_login FROM users WHERE id = ?', (user_id,)).fetchone()

        if not user:
            return jsonify({"error": "User not found"}), 404

        stats = {
            "pets_count": db.execute('SELECT COUNT(*) FROM pets WHERE user_id = ?', (user_id,)).fetchone()[0],
            "recognitions_count": db.execute('SELECT COUNT(*) FROM recognitions WHERE user_id = ?', (user_id,)).fetchone()[0],
            "favorites_count": db.execute('SELECT COUNT(*) FROM favorites WHERE user_id = ?', (user_id,)).fetchone()[0],
            "comments_count": db.execute('SELECT COUNT(*) FROM comments WHERE user_id = ?', (user_id,)).fetchone()[0]
        }

        return jsonify({
            "user": {
                "id": user['id'],
                "username": user['username'],
                "email": user['email'],
                "role": user['role'],
                "avatar": user['avatar'],
                "bio": user['bio'],
                "created_at": user['created_at'],
                "last_login": user['last_login']
            },
            "stats": stats
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/profile', methods=['PUT'])
def update_profile():
    if 'user_id' not in session:
        return jsonify({"error": "Authentication required", "code": "AUTH_REQUIRED"}), 401

    try:
        user_id = session['user_id']
        data = request.get_json()
        db = get_db()

        updates = []
        params = []

        if 'email' in data:
            updates.append('email = ?')
            params.append(data['email'])

        if 'bio' in data:
            updates.append('bio = ?')
            params.append(data['bio'])

        if 'password' in data:
            if len(data['password']) < 6:
                return jsonify({"error": "Password must be at least 6 characters"}), 400
            updates.append('password_hash = ?')
            params.append(hash_password(data['password']))

        if updates:
            params.append(user_id)
            db.execute(f'UPDATE users SET {", ".join(updates)} WHERE id = ?', params)
            db.commit()

        return jsonify({"success": True, "message": "Profile updated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500