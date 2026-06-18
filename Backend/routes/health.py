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


@health_bp.route('/pets/<int:pet_id>/health/consultation', methods=['POST'])
@login_required
def save_consultation_record(pet_id):
    """保存问诊结果到健康记录"""
    try:
        import json
        import traceback
        
        print(f"DEBUG: save_consultation_record called with pet_id={pet_id}")
        
        data = request.get_json()
        print(f"DEBUG: request data: {data}")
        
        symptoms = data.get('symptoms', [])
        duration = data.get('duration', '')
        severity = data.get('severity', '')
        consultation_result = data.get('consultation_result', '')
        recommendation = data.get('recommendation', '')
        additional_info = data.get('additional_info', '')
        full_response = data.get('full_response', {})

        if not consultation_result:
            return jsonify({"error": "consultation_result is required"}), 400

        user_id = get_current_user_id()
        print(f"DEBUG: user_id={user_id}")
        
        db = get_db()

        # 验证宠物所有权
        pet = db.execute('SELECT * FROM pets WHERE id = ? AND user_id = ?', (pet_id, user_id)).fetchone()
        if not pet:
            return jsonify({"error": "Pet not found"}), 404

        pet_info = dict(pet)
        print(f"DEBUG: pet_info={pet_info}")

        # 构建问诊数据JSON（包含所有字段）
        consultation_data = json.dumps({
            'symptoms': symptoms,
            'duration': duration,
            'severity': severity,
            'consultation_result': consultation_result,
            'recommendation': recommendation,
            'additional_info': additional_info,
            'full_response': full_response,
            'pet_name': pet_info.get('name', ''),
            'pet_type': pet_info.get('species', ''),
            'pet_breed': pet_info.get('breed', ''),
            'pet_age': pet_info.get('age', ''),
            'pet_weight': pet_info.get('weight', ''),
            'timestamp': __import__('datetime').datetime.now().isoformat()
        }, ensure_ascii=False)

        # 保存到健康记录
        notes = f"AI问诊记录 - {', '.join(symptoms) if symptoms else '症状分析'}"
        print(f"DEBUG: notes={notes[:50]}...")
        print(f"DEBUG: consultation_data length={len(consultation_data)}")
        
        db.execute('''
            INSERT INTO health_records (pet_id, record_type, notes, consultation_data)
            VALUES (?, 'consultation', ?, ?)
        ''', (pet_id, notes, consultation_data))
        db.commit()

        record_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
        print(f"DEBUG: record_id={record_id}")

        log_action(db, user_id, 'save_consultation_record', {'pet_id': pet_id, 'symptoms': symptoms})

        return jsonify({
            "success": True,
            "message": "Consultation record saved successfully",
            "record_id": record_id
        })
    except Exception as e:
        print(f"ERROR: save_consultation_record failed: {str(e)}")
        print(f"ERROR: traceback: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500


@health_bp.route('/pets/<int:pet_id>/health/consultation/<int:record_id>/export', methods=['GET'])
@login_required
def export_consultation_md(pet_id, record_id):
    """导出问诊记录为Markdown格式"""
    try:
        import json
        user_id = get_current_user_id()
        db = get_db()

        # 验证宠物所有权
        pet = db.execute('SELECT * FROM pets WHERE id = ? AND user_id = ?', (pet_id, user_id)).fetchone()
        if not pet:
            return jsonify({"error": "Pet not found"}), 404

        pet_info = dict(pet)

        # 获取问诊记录
        record = db.execute(
            'SELECT * FROM health_records WHERE id = ? AND pet_id = ? AND record_type = ?',
            (record_id, pet_id, 'consultation')
        ).fetchone()

        if not record:
            return jsonify({"error": "Consultation record not found"}), 404

        record_data = dict(record)
        consultation_data = json.loads(record_data.get('consultation_data', '{}'))

        # 生成Markdown内容
        md_content = f"""# 🏥 PetWise AI问诊记录

## 📋 基本信息

| 项目 | 内容 |
|------|------|
| **宠物名称** | {consultation_data.get('pet_name', '未知')} |
| **宠物类型** | {consultation_data.get('pet_type', '未知')} |
| **宠物品种** | {consultation_data.get('pet_breed', '未知')} |
| **问诊时间** | {consultation_data.get('timestamp', record_data.get('record_date', '未知'))} |

## 🔍 症状信息

### 主要症状
{chr(10).join(['- ' + s for s in consultation_data.get('symptoms', [])]) if consultation_data.get('symptoms') else '- 未记录'}

### 发病时长
{consultation_data.get('duration', '未记录')}

### 严重程度
{consultation_data.get('severity', '未记录')}

### 补充信息
{consultation_data.get('additional_info', '无')}

---

## 💊 AI问诊分析

{consultation_data.get('consultation_result', '无分析结果')}

---

## ⚠️ 免责声明

本问诊结果由PetWise AI助手生成，仅供参考，不能替代专业兽医诊断。
如您的宠物出现严重症状，请尽快联系专业宠物医院就诊。

---

*本记录由 PetWise 智能宠物管理系统自动生成*
*生成时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        return jsonify({
            "success": True,
            "content": md_content,
            "filename": f"问诊记录_{consultation_data.get('pet_name', '宠物')}_{record_data.get('record_date', '')[:10]}.md"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500