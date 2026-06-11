from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from models.db import get_db
from utils import log_action, login_required, get_current_user_id

pets_bp = Blueprint('pets', __name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@pets_bp.route('/pets', methods=['GET'])
@login_required
def get_pets():
    try:
        user_id = get_current_user_id()
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 100))
        offset = (page - 1) * per_page

        db = get_db()
        pets = db.execute('''
            SELECT id, name, breed, category, age, gender, avatar, bio, 
                   birthday, weight, color, neutered, created_at, updated_at
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
@login_required
def add_pet():
    try:
        user_id = get_current_user_id()
        
        # 检查是否是文件上传
        if request.content_type and 'multipart/form-data' in request.content_type:
            name = request.form.get('name')
            if not name:
                return jsonify({"error": "Pet name is required"}), 400
            
            # 处理头像上传
            avatar_filename = None
            if 'avatar' in request.files:
                file = request.files['avatar']
                if file and file.filename and allowed_file(file.filename):
                    import uuid
                    ext = file.filename.rsplit('.', 1)[1].lower()
                    avatar_filename = f"{uuid.uuid4().hex[:16]}.{ext}"
                    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                    file.save(os.path.join(UPLOAD_FOLDER, avatar_filename))
            
            data = {
                'name': name,
                'breed': request.form.get('breed'),
                'category': request.form.get('category', 'cat'),
                'age': request.form.get('age', type=int),
                'gender': request.form.get('gender', 'male'),
                'bio': request.form.get('bio'),
                'birthday': request.form.get('birthday'),
                'weight': request.form.get('weight', type=float),
                'color': request.form.get('color'),
                'neutered': str(request.form.get('neutered', 'false')).lower() in ['true', '1'],
                'avatar': avatar_filename
            }
        else:
            data = request.get_json()
            if not data.get('name'):
                return jsonify({"error": "Pet name is required"}), 400

        db = get_db()
        db.execute('''
            INSERT INTO pets (user_id, name, breed, category, age, gender, bio, avatar, birthday, weight, color, neutered)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, data.get('name'), data.get('breed'), data.get('category'), 
              data.get('age'), data.get('gender'), data.get('bio'), data.get('avatar'),
              data.get('birthday'), data.get('weight'), data.get('color'), 
              1 if data.get('neutered') else 0))
        db.commit()

        pet_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
        pet = db.execute('SELECT * FROM pets WHERE id = ?', (pet_id,)).fetchone()

        log_action(db, user_id, 'add_pet', {'name': data.get('name'), 'breed': data.get('breed')})

        return jsonify({
            "success": True,
            "message": "Pet added successfully",
            "data": dict(pet)
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@pets_bp.route('/pets/<int:pet_id>', methods=['GET'])
@login_required
def get_pet(pet_id):
    try:
        user_id = get_current_user_id()
        db = get_db()
        
        pet = db.execute('SELECT * FROM pets WHERE id = ? AND user_id = ?', (pet_id, user_id)).fetchone()
        
        if not pet:
            return jsonify({"error": "Pet not found"}), 404

        return jsonify({"success": True, "data": dict(pet)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@pets_bp.route('/pets/<int:pet_id>', methods=['PUT'])
@login_required
def update_pet(pet_id):
    try:
        user_id = get_current_user_id()
        db = get_db()

        pet = db.execute('SELECT * FROM pets WHERE id = ? AND user_id = ?', (pet_id, user_id)).fetchone()
        if not pet:
            return jsonify({"error": "Pet not found"}), 404

        # 检查是否是文件上传
        if request.content_type and 'multipart/form-data' in request.content_type:
            data = {
                'name': request.form.get('name'),
                'breed': request.form.get('breed'),
                'category': request.form.get('category'),
                'age': request.form.get('age', type=int),
                'gender': request.form.get('gender'),
                'bio': request.form.get('bio'),
                'birthday': request.form.get('birthday'),
                'weight': request.form.get('weight', type=float),
                'color': request.form.get('color'),
                'neutered': str(request.form.get('neutered', 'false')).lower() in ['true', '1']
            }
            
            # 处理头像上传
            if 'avatar' in request.files:
                file = request.files['avatar']
                if file and file.filename and allowed_file(file.filename):
                    import uuid
                    ext = file.filename.rsplit('.', 1)[1].lower()
                    avatar_filename = f"{uuid.uuid4().hex[:16]}.{ext}"
                    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                    file.save(os.path.join(UPLOAD_FOLDER, avatar_filename))
                    data['avatar'] = avatar_filename
        else:
            data = request.get_json()

        updates = []
        params = []

        for field in ['name', 'breed', 'category', 'age', 'gender', 'bio', 'avatar', 'birthday', 'weight', 'color']:
            if field in data and data[field] is not None:
                updates.append(f'{field} = ?')
                params.append(data[field])
        
        if 'neutered' in data:
            updates.append('neutered = ?')
            params.append(1 if data.get('neutered') else 0)
        
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
@login_required
def delete_pet(pet_id):
    try:
        user_id = get_current_user_id()
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
