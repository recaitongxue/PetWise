"""
智能日程提醒路由
支持宠物健康日历、疫苗接种、驱虫等提醒
"""
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from models.db import get_db
from utils import log_action, login_required, get_current_user_id

schedule_bp = Blueprint('schedule', __name__)

def generate_pet_schedule(pet_id, db):
    """根据宠物档案生成智能日程"""
    pet = db.execute('SELECT * FROM pets WHERE id = ?', (pet_id,)).fetchone()
    if not pet:
        return []

    schedules = []
    today = datetime.now()

    # 疫苗接种提醒（每年一次）
    schedules.append({
        'pet_id': pet_id,
        'reminder_type': 'vaccination',
        'title': '年度疫苗接种',
        'description': f'{pet["name"]}需要接种年度疫苗',
        'scheduled_date': (today + timedelta(days=30)).strftime('%Y-%m-%d'),
        'is_generated': True
    })

    # 驱虫提醒（每3个月一次）
    schedules.append({
        'pet_id': pet_id,
        'reminder_type': 'deworming',
        'title': '季度驱虫',
        'description': f'{pet["name"]}需要进行驱虫',
        'scheduled_date': (today + timedelta(days=90)).strftime('%Y-%m-%d'),
        'is_generated': True
    })

    # 体检提醒（每年一次）
    schedules.append({
        'pet_id': pet_id,
        'reminder_type': 'checkup',
        'title': '年度体检',
        'description': f'{pet["name"]}需要进行年度健康体检',
        'scheduled_date': (today + timedelta(days=365)).strftime('%Y-%m-%d'),
        'is_generated': True
    })

    # 老龄宠物额外提醒
    if pet['age'] and pet['age'] > 7:
        schedules.append({
            'pet_id': pet_id,
            'reminder_type': 'senior_checkup',
            'title': '老龄宠物专项检查',
            'description': f'{pet["name"]}是老龄宠物，建议每6个月进行一次专项检查',
            'scheduled_date': (today + timedelta(days=180)).strftime('%Y-%m-%d'),
            'is_generated': True
        })

    return schedules

@schedule_bp.route('/pets/<int:pet_id>/schedule', methods=['POST'])
@login_required
def add_reminder(pet_id):
    """添加提醒"""
    try:
        data = request.get_json()
        reminder_type = data.get('reminder_type')
        title = data.get('title')
        description = data.get('description', '')
        scheduled_date = data.get('scheduled_date')

        if not reminder_type or not title or not scheduled_date:
            return jsonify({"error": "reminder_type, title and scheduled_date are required"}), 400

        user_id = get_current_user_id()
        db = get_db()

        # 验证宠物所有权
        pet = db.execute('SELECT * FROM pets WHERE id = ? AND user_id = ?', (pet_id, user_id)).fetchone()
        if not pet:
            return jsonify({"error": "Pet not found"}), 404

        db.execute('''
            INSERT INTO schedule_reminders (pet_id, reminder_type, title, description, scheduled_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (pet_id, reminder_type, title, description, scheduled_date))
        db.commit()

        cursor = db.cursor()
        reminder_id = cursor.execute('SELECT last_insert_rowid()').fetchone()[0]

        log_action(db, user_id, 'add_reminder', {'pet_id': pet_id, 'reminder_type': reminder_type})

        return jsonify({
            "success": True,
            "message": "Reminder added",
            "reminder_id": reminder_id
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@schedule_bp.route('/pets/<int:pet_id>/schedule', methods=['GET'])
@login_required
def get_reminders(pet_id):
    """获取宠物提醒"""
    try:
        user_id = get_current_user_id()
        reminder_type = request.args.get('reminder_type')
        status = request.args.get('status', 'all')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        offset = (page - 1) * per_page

        db = get_db()

        # 验证宠物所有权
        pet = db.execute('SELECT * FROM pets WHERE id = ? AND user_id = ?', (pet_id, user_id)).fetchone()
        if not pet:
            return jsonify({"error": "Pet not found"}), 404

        query = 'SELECT * FROM schedule_reminders WHERE pet_id = ?'
        params = [pet_id]

        if reminder_type:
            query += ' AND reminder_type = ?'
            params.append(reminder_type)

        if status != 'all':
            if status == 'completed':
                query += ' AND is_completed = 1'
            elif status == 'pending':
                query += ' AND is_completed = 0'

        query += ' ORDER BY scheduled_date ASC LIMIT ? OFFSET ?'
        params.extend([per_page, offset])

        reminders = db.execute(query, params).fetchall()

        total_query = 'SELECT COUNT(*) FROM schedule_reminders WHERE pet_id = ?'
        total_params = [pet_id]

        if reminder_type:
            total_query += ' AND reminder_type = ?'
            total_params.append(reminder_type)

        if status != 'all':
            if status == 'completed':
                total_query += ' AND is_completed = 1'
            elif status == 'pending':
                total_query += ' AND is_completed = 0'

        total = db.execute(total_query, total_params).fetchone()[0]

        return jsonify({
            "success": True,
            "data": [dict(r) for r in reminders],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@schedule_bp.route('/pets/<int:pet_id>/schedule/generate', methods=['POST'])
@login_required
def generate_schedule(pet_id):
    """生成智能日程"""
    try:
        user_id = get_current_user_id()
        db = get_db()

        # 验证宠物所有权
        pet = db.execute('SELECT * FROM pets WHERE id = ? AND user_id = ?', (pet_id, user_id)).fetchone()
        if not pet:
            return jsonify({"error": "Pet not found"}), 404

        schedules = generate_pet_schedule(pet_id, db)
        added_count = 0

        for schedule in schedules:
            db.execute('''
                INSERT INTO schedule_reminders (pet_id, reminder_type, title, description, scheduled_date)
                VALUES (?, ?, ?, ?, ?)
            ''', (schedule['pet_id'], schedule['reminder_type'], schedule['title'],
                  schedule['description'], schedule['scheduled_date']))
            added_count += 1

        db.commit()

        log_action(db, user_id, 'generate_schedule', {'pet_id': pet_id, 'count': added_count})

        return jsonify({
            "success": True,
            "message": f"Generated {added_count} reminders",
            "count": added_count
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@schedule_bp.route('/schedule/<int:reminder_id>/complete', methods=['PUT'])
@login_required
def complete_reminder(reminder_id):
    """完成提醒"""
    try:
        user_id = get_current_user_id()
        db = get_db()

        # 验证提醒所有权
        reminder = db.execute('''
            SELECT sr.*, p.user_id
            FROM schedule_reminders sr
            JOIN pets p ON sr.pet_id = p.id
            WHERE sr.id = ?
        ''', (reminder_id,)).fetchone()

        if not reminder or reminder['user_id'] != user_id:
            return jsonify({"error": "Reminder not found"}), 404

        db.execute('''
            UPDATE schedule_reminders
            SET is_completed = 1, completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (reminder_id,))
        db.commit()

        log_action(db, user_id, 'complete_reminder', {'reminder_id': reminder_id})

        return jsonify({"success": True, "message": "Reminder completed"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@schedule_bp.route('/schedule/<int:reminder_id>', methods=['DELETE'])
@login_required
def delete_reminder(reminder_id):
    """删除提醒"""
    try:
        user_id = get_current_user_id()
        db = get_db()

        # 验证提醒所有权
        reminder = db.execute('''
            SELECT sr.*, p.user_id
            FROM schedule_reminders sr
            JOIN pets p ON sr.pet_id = p.id
            WHERE sr.id = ?
        ''', (reminder_id,)).fetchone()

        if not reminder or reminder['user_id'] != user_id:
            return jsonify({"error": "Reminder not found"}), 404

        db.execute('DELETE FROM schedule_reminders WHERE id = ?', (reminder_id,))
        db.commit()

        log_action(db, user_id, 'delete_reminder', {'reminder_id': reminder_id})

        return jsonify({"success": True, "message": "Reminder deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@schedule_bp.route('/schedule/upcoming', methods=['GET'])
@login_required
def get_upcoming_reminders():
    """获取即将到来的提醒"""
    try:
        user_id = get_current_user_id()
        days = int(request.args.get('days', 7))
        db = get_db()

        reminders = db.execute('''
            SELECT sr.*, p.name as pet_name, p.avatar as pet_avatar
            FROM schedule_reminders sr
            JOIN pets p ON sr.pet_id = p.id
            WHERE p.user_id = ?
            AND sr.is_completed = 0
            AND date(sr.scheduled_date) BETWEEN date('now') AND date('now', '+' || ? || ' days')
            ORDER BY sr.scheduled_date ASC
        ''', (user_id, days)).fetchall()

        return jsonify({
            "success": True,
            "data": [dict(r) for r in reminders]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500