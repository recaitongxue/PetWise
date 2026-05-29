from flask import Blueprint, request, jsonify, session
from models.db import get_db
from utils import log_action

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            return jsonify({"error": "Admin permission required", "code": "ADMIN_REQUIRED"}), 403
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@admin_bp.route('/admin/users', methods=['GET'])
@admin_required
def get_users():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        role = request.args.get('role')
        offset = (page - 1) * per_page

        db = get_db()
        query = 'SELECT id, username, email, role, is_active, created_at, last_login FROM users'
        params = []

        if role:
            query += ' WHERE role = ?'
            params.append(role)
        
        query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?'
        params.extend([per_page, offset])

        users = db.execute(query, params).fetchall()

        count_query = 'SELECT COUNT(*) FROM users'
        count_params = []
        if role:
            count_query += ' WHERE role = ?'
            count_params.append(role)
        total = db.execute(count_query, count_params).fetchone()[0]

        return jsonify({
            "success": True,
            "data": [dict(u) for u in users],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/admin/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    try:
        admin_id = session['user_id']
        data = request.get_json()
        db = get_db()

        user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404

        updates = []
        params = []

        if 'role' in data:
            updates.append('role = ?')
            params.append(data['role'])
        if 'is_active' in data:
            updates.append('is_active = ?')
            params.append(data['is_active'])

        if updates:
            params.append(user_id)
            db.execute(f'UPDATE users SET {", ".join(updates)} WHERE id = ?', params)
            db.commit()

        log_action(db, admin_id, 'admin_update_user', {'user_id': user_id, 'updates': data})

        return jsonify({"success": True, "message": "User updated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/admin/stats', methods=['GET'])
@admin_required
def get_stats():
    try:
        db = get_db()

        stats = {
            "total_users": db.execute('SELECT COUNT(*) FROM users').fetchone()[0],
            "total_pets": db.execute('SELECT COUNT(*) FROM pets').fetchone()[0],
            "total_recognitions": db.execute('SELECT COUNT(*) FROM recognitions').fetchone()[0],
            "total_favorites": db.execute('SELECT COUNT(*) FROM favorites').fetchone()[0],
            "total_comments": db.execute('SELECT COUNT(*) FROM comments').fetchone()[0],
            "total_chats": db.execute('SELECT COUNT(*) FROM chat_history WHERE role = ?', ('user',)).fetchone()[0],
            "pending_feedback": db.execute('SELECT COUNT(*) FROM feedback WHERE status = ?', ('pending',)).fetchone()[0]
        }

        breed_stats = db.execute('''
            SELECT breed, views, likes, (SELECT COUNT(*) FROM comments WHERE breed = bi.breed) as comment_count
            FROM breed_info bi
            ORDER BY views DESC
            LIMIT 10
        ''').fetchall()
        stats['breed_stats'] = [dict(b) for b in breed_stats]

        recent_registrations = db.execute('''
            SELECT username, created_at FROM users ORDER BY created_at DESC LIMIT 5
        ''').fetchall()
        stats['recent_registrations'] = [dict(r) for r in recent_registrations]

        daily_recognitions = db.execute('''
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM recognitions
            WHERE created_at >= DATE('now', '-7 days')
            GROUP BY DATE(created_at)
            ORDER BY date
        ''').fetchall()
        stats['daily_recognitions'] = [dict(d) for d in daily_recognitions]

        return jsonify({"success": True, **stats})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/admin/logs', methods=['GET'])
@admin_required
def get_logs():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        offset = (page - 1) * per_page

        db = get_db()
        logs = db.execute('''
            SELECT l.id, l.action, l.details, l.ip_address, l.created_at, u.username
            FROM system_logs l
            LEFT JOIN users u ON l.user_id = u.id
            ORDER BY l.created_at DESC
            LIMIT ? OFFSET ?
        ''', (per_page, offset)).fetchall()

        total = db.execute('SELECT COUNT(*) FROM system_logs').fetchone()[0]

        return jsonify({
            "success": True,
            "data": [dict(l) for l in logs],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/admin/announcements', methods=['GET'])
def get_announcements():
    try:
        db = get_db()
        announcements = db.execute('''
            SELECT id, title, content, is_pinned, created_at 
            FROM announcements 
            WHERE is_active = 1 
            ORDER BY is_pinned DESC, created_at DESC
        ''').fetchall()

        return jsonify({"success": True, "data": [dict(a) for a in announcements]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/admin/announcements', methods=['POST'])
@admin_required
def add_announcement():
    try:
        admin_id = session['user_id']
        data = request.get_json()

        title = data.get('title')
        content = data.get('content')

        if not title or not content:
            return jsonify({"error": "Title and content are required"}), 400

        db = get_db()
        db.execute('''
            INSERT INTO announcements (title, content, author_id, is_pinned)
            VALUES (?, ?, ?, ?)
        ''', (title, content, admin_id, data.get('is_pinned', 0)))
        db.commit()

        log_action(db, admin_id, 'admin_add_announcement', {'title': title})

        return jsonify({"success": True, "message": "Announcement created"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/admin/feedback', methods=['GET'])
@admin_required
def get_feedback():
    try:
        status = request.args.get('status')

        db = get_db()
        query = 'SELECT f.*, u.username FROM feedback f LEFT JOIN users u ON f.user_id = u.id'
        params = []

        if status:
            query += ' WHERE status = ?'
            params.append(status)
        
        query += ' ORDER BY f.created_at DESC'
        feedback = db.execute(query, params).fetchall()

        return jsonify({"success": True, "data": [dict(f) for f in feedback]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/admin/feedback/<int:feedback_id>', methods=['PUT'])
@admin_required
def reply_feedback(feedback_id):
    try:
        admin_id = session['user_id']
        data = request.get_json()
        reply = data.get('reply')

        if not reply:
            return jsonify({"error": "Reply content is required"}), 400

        db = get_db()
        db.execute('''
            UPDATE feedback 
            SET status = ?, admin_reply = ?, replied_by = ?, replied_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', ('replied', reply, admin_id, feedback_id))
        db.commit()

        log_action(db, admin_id, 'admin_reply_feedback', {'feedback_id': feedback_id})

        return jsonify({"success": True, "message": "Feedback replied"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/admin/breeds/<breed>', methods=['PUT'])
@admin_required
def update_breed(breed):
    try:
        admin_id = session['user_id']
        data = request.get_json()
        db = get_db()

        updates = []
        params = []

        fields = ['category', 'origin', 'personality', 'lifespan', 'feeding', 'care', 'common_issues', 'suitable_for']
        for field in fields:
            if field in data:
                updates.append(f'{field} = ?')
                params.append(data[field])

        if updates:
            params.append(breed)
            db.execute(f'UPDATE breed_info SET {", ".join(updates)} WHERE breed = ?', params)
            db.commit()

        log_action(db, admin_id, 'admin_update_breed', {'breed': breed})

        return jsonify({"success": True, "message": "Breed info updated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500