import os
import hashlib
import uuid
import json
from functools import wraps
from flask import jsonify, session

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    return hashlib.sha256(password.encode()).hexdigest() == password_hash

def generate_token():
    return str(uuid.uuid4())

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def log_action(db, user_id, action, details=None, ip_address=None):
    db.execute(
        'INSERT INTO system_logs (user_id, action, details, ip_address) VALUES (?, ?, ?, ?)',
        (user_id, action, json.dumps(details) if details else None, ip_address)
    )
    db.commit()

def admin_required(f):
    """管理员权限装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            return jsonify({"error": "Admin permission required", "code": "ADMIN_REQUIRED"}), 403
        return f(*args, **kwargs)
    return decorated_function