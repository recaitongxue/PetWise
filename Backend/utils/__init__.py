import os
import hashlib
import uuid
import json
import base64
import time
from functools import wraps
from flask import jsonify, session, request
from models.db import get_db

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    return hashlib.sha256(password.encode()).hexdigest() == password_hash

def generate_token():
    return str(uuid.uuid4())

def generate_auth_token(user_id, role='user'):
    """生成认证token (base64编码的简单token，生产环境请用JWT)"""
    payload = f"{user_id}:{role}:{int(time.time())}"
    token = base64.b64encode(payload.encode()).decode()
    return token

def parse_auth_token(token):
    """解析认证token"""
    try:
        if not token:
            return None
        decoded = base64.b64decode(token.encode()).decode()
        parts = decoded.split(':')
        if len(parts) >= 2:
            return {"user_id": int(parts[0]), "role": parts[1]}
        return None
    except Exception:
        return None

def get_current_user():
    """获取当前登录用户 - 同时支持session和token两种方式"""
    user_id = session.get('user_id')
    role = session.get('role')
    
    if user_id:
        return {"user_id": user_id, "role": role or 'user'}
    
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        token = auth_header[7:]
        parsed = parse_auth_token(token)
        if parsed:
            return parsed
    
    return None

def get_current_user_id():
    """获取当前登录用户ID"""
    user = get_current_user()
    return user['user_id'] if user else None

def login_required(f):
    """登录认证装饰器 - 同时支持session和Bearer token"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({"error": "Authentication required", "code": "AUTH_REQUIRED"}), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """管理员权限装饰器 - 同时支持session和Bearer token"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({"error": "Authentication required", "code": "AUTH_REQUIRED"}), 401
        if user.get('role') != 'admin':
            return jsonify({"error": "Admin permission required", "code": "ADMIN_REQUIRED"}), 403
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def log_action(db, user_id, action, details=None, ip_address=None):
    db.execute(
        'INSERT INTO system_logs (user_id, action, details, ip_address) VALUES (?, ?, ?, ?)',
        (user_id, action, json.dumps(details) if details else None, ip_address)
    )
    db.commit()