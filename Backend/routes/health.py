"""
宠物健康记录路由
支持健康打卡、体重记录、饮食记录等功能
"""
from flask import Blueprint, request, jsonify
from models.db import get_db
from utils import log_action, login_required, get_current_user_id

health_bp = Blueprint('health', __name__)

@health_bp.route('/pets/<int:pet_id>/health', methods=['POST'])
@login_required
def add_health_record(pet_id):
    """添加健康记录"""
    try:
        data = request.get_json()
        record_type = data.get('record_type')
        weight = data.get('weight')
        food_amount = data.get('food_amount')
        food_type = data.get('food_type')
        stool_status = data.get('stool_status')
        activity_level = data.get('activity_level')
        mood = data.get('mood')
        notes = data.get('notes', '')

        if not record_type:
            return jsonify({"error": "record_type is required"}), 400

        user_id = get_current_user_id()
        db = get_db()

        # 验证宠物所有权
        pet = db.execute('SELECT * FROM pets WHERE id = ? AND user_id = ?', (pet_id, user_id)).fetchone()
        if not pet:
            return jsonify({"error": "Pet not found"}), 404

        db.execute('''
            INSERT INTO health_records (pet_id, record_type, weight, food_amount, food_type, stool_status, activity_level, mood, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (pet_id, record_type, weight, food_amount, food_type, stool_status, activity_level, mood, notes))
        db.commit()

        cursor = db.cursor()
        record_id = cursor.execute('SELECT last_insert_rowid()').fetchone()[0]
        
        log_action(db, user_id, 'add_health_record', {'pet_id': pet_id, 'record_type': record_type})

        return jsonify({
            "success": True,
            "message": "Health record added",
            "record_id": record_id
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@health_bp.route('/pets/<int:pet_id>/health', methods=['GET'])
@login_required
def get_health_records(pet_id):
    """获取宠物健康记录"""
    try:
        user_id = get_current_user_id()
        record_type = request.args.get('record_type')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        offset = (page - 1) * per_page

        db = get_db()

        # 验证宠物所有权
        pet = db.execute('SELECT * FROM pets WHERE id = ? AND user_id = ?', (pet_id, user_id)).fetchone()
        if not pet:
            return jsonify({"error": "Pet not found"}), 404

        query = 'SELECT * FROM health_records WHERE pet_id = ?'
        params = [pet_id]

        if record_type:
            query += ' AND record_type = ?'
            params.append(record_type)

        query += ' ORDER BY record_date DESC LIMIT ? OFFSET ?'
        params.extend([per_page, offset])

        records = db.execute(query, params).fetchall()

        total_query = 'SELECT COUNT(*) FROM health_records WHERE pet_id = ?'
        total_params = [pet_id]

        if record_type:
            total_query += ' AND record_type = ?'
            total_params.append(record_type)

        total = db.execute(total_query, total_params).fetchone()[0]

        return jsonify({
            "success": True,
            "data": [dict(r) for r in records],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@health_bp.route('/pets/<int:pet_id>/health/trends', methods=['GET'])
@login_required
def get_health_trends(pet_id):
    """获取健康趋势数据"""
    try:
        user_id = get_current_user_id()
        db = get_db()

        # 验证宠物所有权
        pet = db.execute('SELECT * FROM pets WHERE id = ? AND user_id = ?', (pet_id, user_id)).fetchone()
        if not pet:
            return jsonify({"error": "Pet not found"}), 404

        # 获取体重趋势
        weight_records = db.execute('''
            SELECT record_date, weight
            FROM health_records
            WHERE pet_id = ? AND weight IS NOT NULL
            ORDER BY record_date ASC
            LIMIT 30
        ''', (pet_id,)).fetchall()

        # 获取饮食趋势
        food_records = db.execute('''
            SELECT record_date, food_amount, food_type
            FROM health_records
            WHERE pet_id = ? AND food_amount IS NOT NULL
            ORDER BY record_date ASC
            LIMIT 30
        ''', (pet_id,)).fetchall()

        return jsonify({
            "success": True,
            "weight_trends": [dict(r) for r in weight_records],
            "food_trends": [dict(r) for r in food_records]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@health_bp.route('/pets/<int:pet_id>/health/<int:record_id>', methods=['DELETE'])
@login_required
def delete_health_record(pet_id, record_id):
    """删除健康记录"""
    try:
        user_id = get_current_user_id()
        db = get_db()

        # 验证宠物所有权
        pet = db.execute('SELECT * FROM pets WHERE id = ? AND user_id = ?', (pet_id, user_id)).fetchone()
        if not pet:
            return jsonify({"error": "Pet not found"}), 404

        db.execute('DELETE FROM health_records WHERE id = ? AND pet_id = ?', (record_id, pet_id))
        db.commit()

        log_action(db, user_id, 'delete_health_record', {'pet_id': pet_id, 'record_id': record_id})

        return jsonify({"success": True, "message": "Health record deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500