from flask import Blueprint, request, jsonify, session
from models.db import get_db
from utils import log_action, admin_required, get_current_user_id

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/users', methods=['GET'])
@admin_required
def get_users():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('size', 10))
        role = request.args.get('role')
        status = request.args.get('status')
        search = request.args.get('search')
        offset = (page - 1) * per_page

        db = get_db()
        query = 'SELECT id, username, email, role, is_active, created_at, last_login FROM users'
        params = []
        conditions = []

        if role:
            conditions.append('role = ?')
            params.append(role)
        
        if status == 'active':
            conditions.append('is_active = 1')
        elif status == 'disabled':
            conditions.append('is_active = 0')
        
        if search:
            conditions.append('(username LIKE ? OR email LIKE ?)')
            params.extend([f'%{search}%', f'%{search}%'])

        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)
        
        query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?'
        params.extend([per_page, offset])

        users = db.execute(query, params).fetchall()

        count_query = 'SELECT COUNT(*) FROM users'
        count_params = []
        if conditions:
            count_query += ' WHERE ' + ' AND '.join(conditions)
            count_params = params[:-2]
        total = db.execute(count_query, count_params).fetchone()[0]

        return jsonify({
            "success": True,
            "data": {
                "data": [dict(u) for u in users],
                "total": total
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/admin/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    try:
        admin_id = get_current_user_id()
        data = request.get_json()
        db = get_db()

        user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404

        updates = []
        params = []

        if 'email' in data:
            updates.append('email = ?')
            params.append(data['email'])
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

@admin_bp.route('/admin/users', methods=['POST'])
@admin_required
def create_user():
    try:
        admin_id = get_current_user_id()
        data = request.get_json()
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'user')

        if not username or not email or not password:
            return jsonify({"error": "Username, email and password are required"}), 400

        db = get_db()
        
        # 检查用户名是否已存在
        existing = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        if existing:
            return jsonify({"error": "Username already exists"}), 400
        
        # 检查邮箱是否已存在
        existing_email = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        if existing_email:
            return jsonify({"error": "Email already exists"}), 400

        # 密码哈希
        import hashlib
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        db.execute('''
            INSERT INTO users (username, email, password_hash, role)
            VALUES (?, ?, ?, ?)
        ''', (username, email, password_hash, role))
        db.commit()

        log_action(db, admin_id, 'admin_create_user', {'username': username, 'role': role})

        return jsonify({"success": True, "message": "User created"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/admin/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    try:
        admin_id = get_current_user_id()
        db = get_db()

        user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # 禁止删除管理员
        if user['role'] == 'admin':
            return jsonify({"error": "Cannot delete admin user"}), 403

        db.execute('DELETE FROM users WHERE id = ?', (user_id,))
        db.commit()

        log_action(db, admin_id, 'admin_delete_user', {'user_id': user_id})

        return jsonify({"success": True, "message": "User deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/admin/users/stats', methods=['GET'])
@admin_required
def get_user_stats():
    try:
        db = get_db()
        
        stats = {
            "total": db.execute('SELECT COUNT(*) FROM users').fetchone()[0],
            "admin": db.execute('SELECT COUNT(*) FROM users WHERE role = ?', ('admin',)).fetchone()[0],
            "active": db.execute('SELECT COUNT(*) FROM users WHERE is_active = 1').fetchone()[0],
            "new_today": db.execute('SELECT COUNT(*) FROM users WHERE DATE(created_at) = DATE("now")').fetchone()[0]
        }

        return jsonify({"success": True, "data": stats})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/admin/users/export', methods=['GET'])
@admin_required
def export_users():
    try:
        from flask import Response
        db = get_db()
        
        users = db.execute('SELECT id, username, email, role, is_active, created_at, last_login FROM users ORDER BY created_at DESC').fetchall()
        
        # 生成CSV内容
        csv_content = "ID,用户名,邮箱,角色,状态,注册时间,最后登录\n"
        for user in users:
            user_dict = dict(user)
            status = '正常' if user_dict['is_active'] else '禁用'
            csv_content += f"{user_dict['id']},{user_dict['username']},{user_dict['email']},{user_dict['role']},{status},{user_dict['created_at']},{user_dict['last_login'] or ''}\n"
        
        response = Response(csv_content, content_type='text/csv; charset=utf-8')
        response.headers['Content-Disposition'] = 'attachment; filename=users.csv'
        
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/admin/users/import', methods=['POST'])
@admin_required
def import_users():
    try:
        admin_id = get_current_user_id()
        import hashlib
        
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        
        file = request.files['file']
        if not file.filename:
            return jsonify({"error": "No file selected"}), 400
        
        # 读取CSV文件
        import csv
        stream = file.stream
        reader = csv.DictReader(stream)
        
        db = get_db()
        count = 0
        
        for row in reader:
            username = row.get('username') or row.get('用户名')
            email = row.get('email') or row.get('邮箱')
            password = row.get('password') or row.get('密码')
            role = row.get('role') or row.get('角色') or 'user'
            
            if not username or not email or not password:
                continue
            
            # 检查是否已存在
            existing = db.execute('SELECT * FROM users WHERE username = ? OR email = ?', (username, email)).fetchone()
            if existing:
                continue
            
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            is_active = 1
            
            db.execute('''
                INSERT INTO users (username, email, password_hash, role, is_active)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, email, password_hash, role, is_active))
            count += 1
        
        db.commit()
        
        log_action(db, admin_id, 'admin_import_users', {'count': count})
        
        return jsonify({"success": True, "data": {"count": count}})
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
        
        action = request.args.get('action')
        user = request.args.get('user')
        ip = request.args.get('ip')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        db = get_db()
        
        query = '''
            SELECT l.id, l.action, l.details, l.ip_address, l.created_at, u.username
            FROM system_logs l
            LEFT JOIN users u ON l.user_id = u.id
            WHERE 1=1
        '''
        params = []
        
        if action:
            query += ' AND l.action = ?'
            params.append(action)
        
        if user:
            query += ' AND u.username LIKE ?'
            params.append(f'%{user}%')
        
        if ip:
            query += ' AND l.ip_address LIKE ?'
            params.append(f'%{ip}%')
        
        if start_date:
            query += ' AND l.created_at >= ?'
            params.append(start_date)
        
        if end_date:
            query += ' AND l.created_at <= ?'
            params.append(end_date)
        
        query += ' ORDER BY l.created_at DESC LIMIT ? OFFSET ?'
        params.extend([per_page, offset])
        
        logs = db.execute(query, params).fetchall()

        # 获取总数
        count_query = 'SELECT COUNT(*) FROM system_logs l LEFT JOIN users u ON l.user_id = u.id WHERE 1=1'
        count_params = []
        
        if action:
            count_query += ' AND l.action = ?'
            count_params.append(action)
        
        if user:
            count_query += ' AND u.username LIKE ?'
            count_params.append(f'%{user}%')
        
        if ip:
            count_query += ' AND l.ip_address LIKE ?'
            count_params.append(f'%{ip}%')
        
        if start_date:
            count_query += ' AND l.created_at >= ?'
            count_params.append(start_date)
        
        if end_date:
            count_query += ' AND l.created_at <= ?'
            count_params.append(end_date)
        
        total = db.execute(count_query, count_params).fetchone()[0]

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

@admin_bp.route('/admin/logs/export', methods=['GET'])
@admin_required
def export_logs():
    """导出日志为CSV"""
    try:
        action = request.args.get('action')
        user = request.args.get('user')
        ip = request.args.get('ip')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        db = get_db()
        
        query = '''
            SELECT l.id, l.action, l.details, l.ip_address, l.created_at, u.username
            FROM system_logs l
            LEFT JOIN users u ON l.user_id = u.id
            WHERE 1=1
        '''
        params = []
        
        if action:
            query += ' AND l.action = ?'
            params.append(action)
        
        if user:
            query += ' AND u.username LIKE ?'
            params.append(f'%{user}%')
        
        if ip:
            query += ' AND l.ip_address LIKE ?'
            params.append(f'%{ip}%')
        
        if start_date:
            query += ' AND l.created_at >= ?'
            params.append(start_date)
        
        if end_date:
            query += ' AND l.created_at <= ?'
            params.append(end_date)
        
        query += ' ORDER BY l.created_at DESC LIMIT 10000'
        
        logs = db.execute(query, params).fetchall()
        
        # 生成CSV内容
        csv_content = 'ID,用户,操作,详情,IP地址,时间\n'
        for log in logs:
            csv_content += f'{log["id"]},{log["username"] or "匿名"},{log["action"]},{log["details"] or ""},{log["ip_address"] or "未知"},{log["created_at"]}\n'
        
        return jsonify({
            "success": True,
            "data": csv_content
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
        admin_id = get_current_user_id()
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
        admin_id = get_current_user_id()
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
        admin_id = get_current_user_id()
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

@admin_bp.route('/admin/models', methods=['GET'])
@admin_required
def get_models():
    try:
        db = get_db()
        models = db.execute('SELECT * FROM llm_models ORDER BY is_default DESC, created_at DESC').fetchall()
        return jsonify({"success": True, "data": [dict(m) for m in models]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/admin/models', methods=['POST'])
@admin_required
def add_model():
    try:
        admin_id = get_current_user_id()
        data = request.get_json()

        required_fields = ['name', 'provider', 'model_name']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"{field} is required"}), 400

        db = get_db()

        if data.get('is_default', 0) == 1:
            db.execute('UPDATE llm_models SET is_default = 0 WHERE is_default = 1')

        db.execute('''
            INSERT INTO llm_models (name, provider, api_key, base_url, model_name, max_tokens, temperature, top_p, is_active, is_default, description, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (
            data['name'],
            data['provider'],
            data.get('api_key'),
            data.get('base_url'),
            data['model_name'],
            data.get('max_tokens', 2048),
            data.get('temperature', 0.7),
            data.get('top_p', 0.9),
            data.get('is_active', 1),
            data.get('is_default', 0),
            data.get('description')
        ))
        db.commit()

        log_action(db, admin_id, 'admin_add_model', {'name': data['name'], 'provider': data['provider']})

        return jsonify({"success": True, "message": "Model added"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/admin/models/<int:model_id>', methods=['PUT'])
@admin_required
def update_model(model_id):
    try:
        admin_id = get_current_user_id()
        data = request.get_json()
        db = get_db()

        model = db.execute('SELECT * FROM llm_models WHERE id = ?', (model_id,)).fetchone()
        if not model:
            return jsonify({"error": "Model not found"}), 404

        if data.get('is_default', 0) == 1:
            db.execute('UPDATE llm_models SET is_default = 0 WHERE is_default = 1')

        updates = []
        params = []

        fields = ['name', 'provider', 'api_key', 'base_url', 'model_name', 'max_tokens', 'temperature', 'top_p', 'is_active', 'is_default', 'description']
        for field in fields:
            if field in data:
                updates.append(f'{field} = ?')
                params.append(data[field])

        if updates:
            updates.append('updated_at = CURRENT_TIMESTAMP')
            params.append(model_id)
            db.execute(f'UPDATE llm_models SET {", ".join(updates)} WHERE id = ?', params)
            db.commit()

        log_action(db, admin_id, 'admin_update_model', {'model_id': model_id})

        return jsonify({"success": True, "message": "Model updated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/admin/models/<int:model_id>', methods=['DELETE'])
@admin_required
def delete_model(model_id):
    try:
        admin_id = get_current_user_id()
        db = get_db()

        model = db.execute('SELECT * FROM llm_models WHERE id = ?', (model_id,)).fetchone()
        if not model:
            return jsonify({"error": "Model not found"}), 404

        db.execute('DELETE FROM llm_models WHERE id = ?', (model_id,))
        db.commit()

        log_action(db, admin_id, 'admin_delete_model', {'model_id': model_id})

        return jsonify({"success": True, "message": "Model deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/admin/models/default/<int:model_id>', methods=['POST'])
@admin_required
def set_default_model(model_id):
    try:
        admin_id = get_current_user_id()
        db = get_db()

        model = db.execute('SELECT * FROM llm_models WHERE id = ?', (model_id,)).fetchone()
        if not model:
            return jsonify({"error": "Model not found"}), 404

        db.execute('UPDATE llm_models SET is_default = 0 WHERE is_default = 1')
        db.execute('UPDATE llm_models SET is_default = 1, updated_at = CURRENT_TIMESTAMP WHERE id = ?', (model_id,))
        db.commit()

        log_action(db, admin_id, 'admin_set_default_model', {'model_id': model_id})

        return jsonify({"success": True, "message": "Default model updated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/admin/knowledge', methods=['GET'])
@admin_required
def get_knowledge():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        category = request.args.get('category')
        offset = (page - 1) * per_page

        db = get_db()
        query = 'SELECT k.*, u.username as creator FROM knowledge_base k LEFT JOIN users u ON k.created_by = u.id'
        params = []

        if category:
            query += ' WHERE category = ?'
            params.append(category)
        
        query += ' ORDER BY k.created_at DESC LIMIT ? OFFSET ?'
        params.extend([per_page, offset])

        knowledge = db.execute(query, params).fetchall()

        count_query = 'SELECT COUNT(*) FROM knowledge_base'
        count_params = []
        if category:
            count_query += ' WHERE category = ?'
            count_params.append(category)
        total = db.execute(count_query, count_params).fetchone()[0]

        return jsonify({
            "success": True,
            "data": [dict(k) for k in knowledge],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/admin/knowledge', methods=['POST'])
@admin_required
def add_knowledge():
    try:
        admin_id = get_current_user_id()
        data = request.get_json()

        required_fields = ['title', 'content']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"{field} is required"}), 400

        db = get_db()
        db.execute('''
            INSERT INTO knowledge_base (title, content, category, tags, source, is_active, created_by, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (
            data['title'],
            data['content'],
            data.get('category', 'general'),
            data.get('tags'),
            data.get('source'),
            data.get('is_active', 1),
            admin_id
        ))
        db.commit()

        log_action(db, admin_id, 'admin_add_knowledge', {'title': data['title']})

        return jsonify({"success": True, "message": "Knowledge added"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/admin/knowledge/<int:knowledge_id>', methods=['PUT'])
@admin_required
def update_knowledge(knowledge_id):
    try:
        admin_id = get_current_user_id()
        data = request.get_json()
        db = get_db()

        knowledge = db.execute('SELECT * FROM knowledge_base WHERE id = ?', (knowledge_id,)).fetchone()
        if not knowledge:
            return jsonify({"error": "Knowledge not found"}), 404

        updates = []
        params = []

        fields = ['title', 'content', 'category', 'tags', 'source', 'is_active']
        for field in fields:
            if field in data:
                updates.append(f'{field} = ?')
                params.append(data[field])

        if updates:
            updates.append('updated_at = CURRENT_TIMESTAMP')
            params.append(knowledge_id)
            db.execute(f'UPDATE knowledge_base SET {", ".join(updates)} WHERE id = ?', params)
            db.commit()

        log_action(db, admin_id, 'admin_update_knowledge', {'knowledge_id': knowledge_id})

        return jsonify({"success": True, "message": "Knowledge updated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/admin/knowledge/<int:knowledge_id>', methods=['DELETE'])
@admin_required
def delete_knowledge(knowledge_id):
    try:
        admin_id = get_current_user_id()
        db = get_db()

        knowledge = db.execute('SELECT * FROM knowledge_base WHERE id = ?', (knowledge_id,)).fetchone()
        if not knowledge:
            return jsonify({"error": "Knowledge not found"}), 404

        db.execute('DELETE FROM knowledge_base WHERE id = ?', (knowledge_id,))
        db.commit()

        log_action(db, admin_id, 'admin_delete_knowledge', {'knowledge_id': knowledge_id})

        return jsonify({"success": True, "message": "Knowledge deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/admin/knowledge/categories', methods=['GET'])
@admin_required
def get_knowledge_categories():
    try:
        db = get_db()
        categories = db.execute('SELECT category, COUNT(*) as count FROM knowledge_base GROUP BY category').fetchall()
        return jsonify({"success": True, "data": [dict(c) for c in categories]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==================== 限流配置管理 ====================

@admin_bp.route('/admin/rate-limits', methods=['GET'])
@admin_required
def get_rate_limit_configs():
    """获取所有限流配置"""
    try:
        db = get_db()
        configs = db.execute('SELECT * FROM rate_limit_config ORDER BY endpoint').fetchall()
        return jsonify({"success": True, "data": [dict(c) for c in configs]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/admin/rate-limits', methods=['POST'])
@admin_required
def add_rate_limit_config():
    """添加限流配置"""
    try:
        admin_id = get_current_user_id()
        data = request.get_json()
        
        endpoint = data.get('endpoint')
        daily_limit = data.get('daily_limit', 100)
        hourly_limit = data.get('hourly_limit', 20)
        per_minute_limit = data.get('per_minute_limit', 5)
        description = data.get('description', '')
        
        if not endpoint:
            return jsonify({"error": "Endpoint is required"}), 400
        
        db = get_db()
        
        # 检查是否已存在
        existing = db.execute('SELECT * FROM rate_limit_config WHERE endpoint = ?', (endpoint,)).fetchone()
        if existing:
            return jsonify({"error": "Endpoint config already exists"}), 400
        
        db.execute('''
            INSERT INTO rate_limit_config (endpoint, daily_limit, hourly_limit, per_minute_limit, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (endpoint, daily_limit, hourly_limit, per_minute_limit, description))
        db.commit()
        
        log_action(db, admin_id, 'admin_add_rate_limit', {'endpoint': endpoint})
        
        return jsonify({"success": True, "message": "Rate limit config added"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/admin/rate-limits/<int:config_id>', methods=['PUT'])
@admin_required
def update_rate_limit_config(config_id):
    """更新限流配置"""
    try:
        admin_id = get_current_user_id()
        data = request.get_json()
        db = get_db()
        
        updates = []
        params = []
        
        fields = ['daily_limit', 'hourly_limit', 'per_minute_limit', 'is_enabled', 'description']
        for field in fields:
            if field in data:
                updates.append(f'{field} = ?')
                params.append(data[field])
        
        if not updates:
            return jsonify({"error": "No fields to update"}), 400
        
        params.append(config_id)
        db.execute(f'UPDATE rate_limit_config SET {", ".join(updates)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?', params)
        db.commit()
        
        log_action(db, admin_id, 'admin_update_rate_limit', {'config_id': config_id})
        
        return jsonify({"success": True, "message": "Rate limit config updated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/admin/rate-limits/<int:config_id>', methods=['DELETE'])
@admin_required
def delete_rate_limit_config(config_id):
    """删除限流配置"""
    try:
        admin_id = get_current_user_id()
        db = get_db()
        
        db.execute('DELETE FROM rate_limit_config WHERE id = ?', (config_id,))
        db.commit()
        
        log_action(db, admin_id, 'admin_delete_rate_limit', {'config_id': config_id})
        
        return jsonify({"success": True, "message": "Rate limit config deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/admin/rate-limits/logs', methods=['GET'])
@admin_required
def get_rate_limit_logs():
    """获取用户限流记录"""
    try:
        db = get_db()
        user_id = request.args.get('user_id', '')
        endpoint = request.args.get('endpoint', '')
        
        query = 'SELECT * FROM rate_limits WHERE 1=1'
        params = []
        
        if user_id:
            query += ' AND user_id = ?'
            params.append(user_id)
        if endpoint:
            query += ' AND endpoint LIKE ?'
            params.append(f'%{endpoint}%')
        
        logs = db.execute(query, params).fetchall()
        return jsonify({"success": True, "data": [dict(l) for l in logs]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==================== 敏感词管理 ====================

@admin_bp.route('/admin/sensitive-words', methods=['GET'])
@admin_required
def get_sensitive_words():
    """获取敏感词列表"""
    try:
        db = get_db()
        words = db.execute('SELECT * FROM sensitive_words ORDER BY category, severity DESC').fetchall()
        return jsonify({"success": True, "data": [dict(w) for w in words]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/admin/sensitive-words', methods=['POST'])
@admin_required
def add_sensitive_word():
    """添加敏感词"""
    try:
        admin_id = get_current_user_id()
        data = request.get_json()
        
        word = data.get('word')
        category = data.get('category', 'medical')
        severity = data.get('severity', 'medium')
        
        if not word:
            return jsonify({"error": "Word is required"}), 400
        
        db = get_db()
        db.execute('''
            INSERT INTO sensitive_words (word, category, severity)
            VALUES (?, ?, ?)
        ''', (word, category, severity))
        db.commit()
        
        log_action(db, admin_id, 'admin_add_sensitive_word', {'word': word, 'category': category})
        
        return jsonify({"success": True, "message": "Sensitive word added"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/admin/sensitive-words/<int:word_id>', methods=['DELETE'])
@admin_required
def delete_sensitive_word(word_id):
    """删除敏感词"""
    try:
        admin_id = get_current_user_id()
        db = get_db()
        
        db.execute('DELETE FROM sensitive_words WHERE id = ?', (word_id,))
        db.commit()
        
        log_action(db, admin_id, 'admin_delete_sensitive_word', {'word_id': word_id})
        
        return jsonify({"success": True, "message": "Sensitive word deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/admin/sensitive-words/<int:word_id>', methods=['PUT'])
@admin_required
def update_sensitive_word(word_id):
    """更新敏感词"""
    try:
        admin_id = get_current_user_id()
        data = request.get_json()
        db = get_db()
        
        updates = []
        params = []
        
        fields = ['word', 'category', 'severity', 'is_enabled']
        for field in fields:
            if field in data:
                updates.append(f'{field} = ?')
                params.append(data[field])
        
        if updates:
            params.append(word_id)
            db.execute(f'UPDATE sensitive_words SET {", ".join(updates)} WHERE id = ?', params)
            db.commit()
        
        log_action(db, admin_id, 'admin_update_sensitive_word', {'word_id': word_id})
        
        return jsonify({"success": True, "message": "Sensitive word updated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==================== Prompt模板管理 ====================

@admin_bp.route('/admin/prompt-templates', methods=['GET'])
@admin_required
def get_prompt_templates():
    """获取Prompt模板列表"""
    try:
        db = get_db()
        templates = db.execute('SELECT * FROM prompt_templates ORDER BY prompt_type, is_active DESC').fetchall()
        return jsonify({"success": True, "data": [dict(t) for t in templates]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/admin/prompt-templates', methods=['POST'])
@admin_required
def add_prompt_template():
    """添加Prompt模板"""
    try:
        admin_id = get_current_user_id()
        data = request.get_json()
        
        name = data.get('name')
        prompt_type = data.get('prompt_type')
        content = data.get('content')
        variables = data.get('variables', '')
        
        if not name or not prompt_type or not content:
            return jsonify({"error": "Name, prompt_type and content are required"}), 400
        
        db = get_db()
        
        # 如果设为active，先取消其他同类型的active状态
        if data.get('is_active', 1) == 1:
            db.execute('UPDATE prompt_templates SET is_active = 0 WHERE prompt_type = ?', (prompt_type,))
        
        db.execute('''
            INSERT INTO prompt_templates (name, prompt_type, content, variables, created_by)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, prompt_type, content, variables, admin_id))
        db.commit()
        
        cursor = db.cursor()
        template_id = cursor.execute('SELECT last_insert_rowid()').fetchone()[0]
        
        log_action(db, admin_id, 'admin_add_prompt_template', {'name': name, 'prompt_type': prompt_type})
        
        return jsonify({"success": True, "message": "Prompt template added", "template_id": template_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/admin/prompt-templates/<int:template_id>', methods=['PUT'])
@admin_required
def update_prompt_template(template_id):
    """更新Prompt模板"""
    try:
        admin_id = get_current_user_id()
        data = request.get_json()
        db = get_db()
        
        updates = []
        params = []
        
        fields = ['name', 'content', 'variables', 'is_active']
        for field in fields:
            if field in data:
                updates.append(f'{field} = ?')
                params.append(data[field])
        
        # 版本号+1
        updates.append('version = version + 1')
        
        if updates:
            params.append(template_id)
            db.execute(f'UPDATE prompt_templates SET {", ".join(updates)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?', params)
            
            # 如果设为active，先取消其他同类型的active状态
            if data.get('is_active') == 1:
                template = db.execute('SELECT prompt_type FROM prompt_templates WHERE id = ?', (template_id,)).fetchone()
                if template:
                    db.execute('UPDATE prompt_templates SET is_active = 0 WHERE prompt_type = ? AND id != ?', 
                             (template['prompt_type'], template_id))
            
            db.commit()
        
        log_action(db, admin_id, 'admin_update_prompt_template', {'template_id': template_id})
        
        return jsonify({"success": True, "message": "Prompt template updated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/admin/prompt-templates/<int:template_id>', methods=['DELETE'])
@admin_required
def delete_prompt_template(template_id):
    """删除Prompt模板"""
    try:
        admin_id = get_current_user_id()
        db = get_db()
        
        db.execute('DELETE FROM prompt_templates WHERE id = ?', (template_id,))
        db.commit()
        
        log_action(db, admin_id, 'admin_delete_prompt_template', {'template_id': template_id})
        
        return jsonify({"success": True, "message": "Prompt template deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==================== Prompts管理 (兼容前端) ====================

@admin_bp.route('/admin/prompts', methods=['GET'])
@admin_required
def get_prompts():
    """获取Prompt列表（兼容前端调用）"""
    try:
        db = get_db()
        prompt_type = request.args.get('prompt_type', '')
        search = request.args.get('search', '')
        
        query = 'SELECT * FROM prompt_templates WHERE 1=1'
        params = []
        
        if prompt_type:
            query += ' AND prompt_type = ?'
            params.append(prompt_type)
        if search:
            query += ' AND name LIKE ?'
            params.append(f'%{search}%')
        
        query += ' ORDER BY prompt_type, name'
        
        prompts = db.execute(query, params).fetchall()
        return jsonify({"success": True, "data": [dict(p) for p in prompts]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==================== 系统监控数据 ====================

@admin_bp.route('/admin/monitor/realtime', methods=['GET'])
@admin_required
def get_realtime_stats():
    """获取实时监控数据"""
    try:
        db = get_db()
        
        # 获取今日统计数据
        today_stats = db.execute('''
            SELECT 
                COUNT(DISTINCT user_id) as today_users,
                COUNT(*) as today_requests,
                COUNT(CASE WHEN action = 'recognize' THEN 1 END) as today_recognitions,
                COUNT(CASE WHEN action = 'agent_chat' THEN 1 END) as today_chats
            FROM system_logs 
            WHERE date(created_at) = date('now')
        ''').fetchone()
        
        # 获取最近7天的请求趋势
        weekly_trend = db.execute('''
            SELECT 
                date(created_at) as date,
                COUNT(*) as count
            FROM system_logs 
            WHERE created_at >= datetime('now', '-7 days')
            GROUP BY date(created_at)
            ORDER BY date
        ''').fetchall()
        
        # 获取系统指标
        metrics = db.execute('''
            SELECT * FROM system_metrics 
            WHERE recorded_at >= datetime('now', '-1 hour')
            ORDER BY recorded_at DESC
        ''').fetchall()
        
        # 获取CPU和内存使用情况
        system_info = {}
        try:
            import psutil
            cpu_usage = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            system_info = {
                "cpu_usage": cpu_usage,
                "memory_usage": memory.percent,
                "memory_total": memory.total,
                "memory_available": memory.available
            }
        except ImportError:
            system_info = {
                "cpu_usage": 0,
                "memory_usage": 0,
                "message": "psutil not installed"
            }
        except Exception:
            system_info = {
                "cpu_usage": 0,
                "memory_usage": 0,
                "message": "Failed to get system info"
            }
        
        return jsonify({
            "success": True,
            "data": {
                "today": dict(today_stats) if today_stats else {},
                "weekly_trend": [dict(w) for w in weekly_trend],
                "metrics": [dict(m) for m in metrics] if metrics else [],
                "system": system_info
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==================== 公告管理完整API ====================

@admin_bp.route('/admin/announcements/<int:announcement_id>', methods=['PUT'])
@admin_required
def update_announcement(announcement_id):
    """更新公告"""
    try:
        admin_id = get_current_user_id()
        data = request.get_json()
        db = get_db()
        
        updates = []
        params = []
        
        fields = ['title', 'content', 'is_pinned', 'is_active']
        for field in fields:
            if field in data:
                updates.append(f'{field} = ?')
                params.append(data[field])
        
        if updates:
            params.append(announcement_id)
            db.execute(f'UPDATE announcements SET {", ".join(updates)} WHERE id = ?', params)
            db.commit()
        
        log_action(db, admin_id, 'admin_update_announcement', {'announcement_id': announcement_id})
        
        return jsonify({"success": True, "message": "Announcement updated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/admin/announcements/<int:announcement_id>', methods=['DELETE'])
@admin_required
def delete_announcement(announcement_id):
    """删除公告"""
    try:
        admin_id = get_current_user_id()
        db = get_db()
        
        db.execute('DELETE FROM announcements WHERE id = ?', (announcement_id,))
        db.commit()
        
        log_action(db, admin_id, 'admin_delete_announcement', {'announcement_id': announcement_id})
        
        return jsonify({"success": True, "message": "Announcement deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==================== 纠错管理 ====================

@admin_bp.route('/admin/corrections', methods=['GET'])
@admin_required
def get_corrections():
    """获取纠错记录列表"""
    try:
        status = request.args.get('status')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        offset = (page - 1) * per_page
        
        db = get_db()
        
        query = '''
            SELECT c.*, u.username, r.image_path
            FROM corrections c
            LEFT JOIN users u ON c.user_id = u.id
            LEFT JOIN recognitions r ON c.recognition_id = r.id
        '''
        params = []
        
        if status:
            query += ' WHERE c.status = ?'
            params.append(status)
        
        query += ' ORDER BY c.created_at DESC LIMIT ? OFFSET ?'
        params.extend([per_page, offset])
        
        corrections = db.execute(query, params).fetchall()
        
        total_query = 'SELECT COUNT(*) FROM corrections'
        total_params = []
        if status:
            total_query += ' WHERE status = ?'
            total_params.append(status)
        
        total = db.execute(total_query, total_params).fetchone()[0]
        
        return jsonify({
            "success": True,
            "data": [dict(c) for c in corrections],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/admin/corrections/<int:correction_id>', methods=['PUT'])
@admin_required
def update_correction(correction_id):
    """审核纠错记录"""
    try:
        admin_id = get_current_user_id()
        data = request.get_json()
        db = get_db()
        
        status = data.get('status')
        if not status:
            return jsonify({"error": "Status is required"}), 400
        
        db.execute('''
            UPDATE corrections 
            SET status = ?, reviewed_by = ?, reviewed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (status, admin_id, correction_id))
        db.commit()
        
        # 如果批准纠错，添加到难样本库
        if status == 'approved':
            correction = db.execute('SELECT * FROM corrections WHERE id = ?', (correction_id,)).fetchone()
            if correction:
                recognition = db.execute('SELECT * FROM recognitions WHERE id = ?', (correction['recognition_id'],)).fetchone()
                if recognition:
                    db.execute('''
                        INSERT INTO hard_examples (recognition_id, user_id, image_path, predicted_breed, confidence, is_user_corrected, corrected_breed, status)
                        VALUES (?, ?, ?, ?, ?, 1, ?, 'approved')
                    ''', (recognition['id'], correction['user_id'], recognition['image_path'],
                          correction['original_breed'], correction['confidence'], correction['corrected_breed']))
                    db.commit()
        
        log_action(db, admin_id, 'admin_update_correction', {'correction_id': correction_id, 'status': status})
        
        return jsonify({"success": True, "message": "Correction updated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==================== 系统指标记录 ====================

@admin_bp.route('/admin/metrics', methods=['POST'])
@admin_required
def record_system_metric():
    """记录系统指标"""
    try:
        admin_id = get_current_user_id()
        data = request.get_json()
        
        metric_type = data.get('metric_type')
        metric_name = data.get('metric_name')
        metric_value = data.get('metric_value')
        
        if not metric_type or not metric_name or metric_value is None:
            return jsonify({"error": "metric_type, metric_name and metric_value are required"}), 400
        
        db = get_db()
        db.execute('''
            INSERT INTO system_metrics (metric_type, metric_name, metric_value, unit)
            VALUES (?, ?, ?, ?)
        ''', (metric_type, metric_name, metric_value, data.get('unit', '')))
        db.commit()
        
        return jsonify({"success": True, "message": "Metric recorded"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/admin/metrics', methods=['GET'])
@admin_required
def get_system_metrics():
    """获取系统指标"""
    try:
        metric_type = request.args.get('metric_type')
        hours = int(request.args.get('hours', 24))
        
        db = get_db()
        
        query = 'SELECT * FROM system_metrics WHERE recorded_at >= datetime("now", "-" || ? || " hours")'
        params = [hours]
        
        if metric_type:
            query += ' AND metric_type = ?'
            params.append(metric_type)
        
        query += ' ORDER BY recorded_at DESC'
        
        metrics = db.execute(query, params).fetchall()
        
        return jsonify({"success": True, "data": [dict(m) for m in metrics]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500