"""
管理端模型管理路由
支持模型版本管理、热加载、准确率监控
"""
import os
import torch
import torch.nn as nn
from flask import Blueprint, request, jsonify, session
from models.db import get_db
from utils import log_action, admin_required
from config import Config

model_admin_bp = Blueprint('model_admin', __name__)

# 全局模型实例
current_model = None
current_model_version = None

class_names = [
    "中华田园犬", "吉娃娃", "哈士奇", "德牧", "拉布拉多", "杜宾",
    "柴犬", "法国斗牛", "萨摩耶", "藏獒", "金毛",
    "阿比西尼亚猫", "埃及猫", "豹猫", "布偶猫", "波斯猫", "缅甸猫",
    "俄罗斯蓝猫", "孟买猫", "缅因猫", "无毛猫", "暹罗猫", "英国短毛猫"
]

def create_model(num_classes):
    """Create model with same architecture as training"""
    from torchvision import models
    model = models.efficientnet_b3(weights=None)
    num_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.3, inplace=True),
        nn.Linear(num_features, 512),
        nn.ReLU(inplace=True),
        nn.Dropout(p=0.2),
        nn.Linear(512, num_classes)
    )
    return model

def load_model_from_path(model_path):
    """Load model from specific path"""
    try:
        model = create_model(len(class_names))

        if os.path.exists(model_path):
            checkpoint = torch.load(model_path, map_location='cpu')
            if 'model_state_dict' in checkpoint:
                model.load_state_dict(checkpoint['model_state_dict'])
            else:
                model.load_state_dict(checkpoint)
            model.eval()
            return model
        else:
            return None
    except Exception as e:
        print(f"Failed to load model: {e}")
        return None

@model_admin_bp.route('/admin/models', methods=['POST'])
@admin_required
def add_model_version():
    """添加模型版本"""
    try:
        data = request.get_json()
        version = data.get('version')
        model_path = data.get('model_path')
        framework = data.get('framework', 'PyTorch')
        num_classes = data.get('num_classes', 23)
        training_accuracy = data.get('training_accuracy')
        validation_accuracy = data.get('validation_accuracy')
        top1_accuracy = data.get('top1_accuracy')
        top5_accuracy = data.get('top5_accuracy')
        description = data.get('description', '')

        if not version or not model_path:
            return jsonify({"error": "version and model_path are required"}), 400

        admin_id = session['user_id']
        db = get_db()

        db.execute('''
            INSERT INTO model_versions (version, model_path, framework, num_classes, training_accuracy,
                validation_accuracy, top1_accuracy, top5_accuracy, description, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (version, model_path, framework, num_classes, training_accuracy,
              validation_accuracy, top1_accuracy, top5_accuracy, description, admin_id))
        db.commit()

        cursor = db.cursor()
        model_id = cursor.execute('SELECT last_insert_rowid()').fetchone()[0]

        log_action(db, admin_id, 'add_model_version', {'version': version, 'model_path': model_path})

        return jsonify({
            "success": True,
            "message": "Model version added",
            "model_id": model_id
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@model_admin_bp.route('/admin/models', methods=['GET'])
@admin_required
def get_model_versions():
    """获取所有模型版本"""
    try:
        db = get_db()
        models = db.execute('''
            SELECT mv.*, u.username as created_by_name
            FROM model_versions mv
            LEFT JOIN users u ON mv.created_by = u.id
            ORDER BY mv.created_at DESC
        ''').fetchall()

        return jsonify({
            "success": True,
            "data": [dict(m) for m in models]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@model_admin_bp.route('/admin/models/<int:model_id>/activate', methods=['PUT'])
@admin_required
def activate_model(model_id):
    """激活模型版本"""
    try:
        admin_id = session['user_id']
        db = get_db()

        # 获取模型版本信息
        model_version = db.execute('SELECT * FROM model_versions WHERE id = ?', (model_id,)).fetchone()
        if not model_version:
            return jsonify({"error": "Model version not found"}), 404

        # 取消所有其他模型的激活状态
        db.execute('UPDATE model_versions SET is_active = 0')
        db.execute('UPDATE model_versions SET is_loaded = 0')

        # 激活当前模型
        db.execute('UPDATE model_versions SET is_active = 1 WHERE id = ?', (model_id,))
        db.commit()

        # 尝试加载模型
        global current_model, current_model_version
        new_model = load_model_from_path(model_version['model_path'])

        if new_model:
            current_model = new_model
            current_model_version = model_version['version']
            db.execute('UPDATE model_versions SET is_loaded = 1 WHERE id = ?', (model_id,))
            db.commit()

            log_action(db, admin_id, 'activate_model', {'model_id': model_id, 'version': model_version['version']})

            return jsonify({
                "success": True,
                "message": "Model activated and loaded successfully",
                "version": model_version['version']
            })
        else:
            return jsonify({
                "success": False,
                "error": "Failed to load model"
            }), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@model_admin_bp.route('/admin/models/<int:model_id>', methods=['DELETE'])
@admin_required
def delete_model_version(model_id):
    """删除模型版本"""
    try:
        admin_id = session['user_id']
        db = get_db()

        model_version = db.execute('SELECT * FROM model_versions WHERE id = ?', (model_id,)).fetchone()
        if not model_version:
            return jsonify({"error": "Model version not found"}), 404

        if model_version['is_active']:
            return jsonify({"error": "Cannot delete active model"}), 400

        db.execute('DELETE FROM model_versions WHERE id = ?', (model_id,))
        db.commit()

        log_action(db, admin_id, 'delete_model_version', {'model_id': model_id})

        return jsonify({"success": True, "message": "Model version deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@model_admin_bp.route('/admin/models/accuracy', methods=['GET'])
@admin_required
def get_model_accuracy():
    """获取模型准确率统计"""
    try:
        db = get_db()

        # 计算Top-1准确率（基于用户纠错）
        total_corrections = db.execute('SELECT COUNT(*) FROM hard_examples WHERE is_user_corrected = 1').fetchone()[0]
        if total_corrections > 0:
            correct_predictions = db.execute('''
                SELECT COUNT(*) FROM hard_examples
                WHERE is_user_corrected = 1 AND predicted_breed = corrected_breed
            ''').fetchone()[0]
            top1_accuracy = (correct_predictions / total_corrections) * 100
        else:
            top1_accuracy = 0.0

        # 计算Top-5准确率
        total_recognitions = db.execute('SELECT COUNT(*) FROM recognitions').fetchone()[0]
        if total_recognitions > 0:
            high_confidence = db.execute('''
                SELECT COUNT(*) FROM recognitions
                WHERE confidence >= 0.8
            ''').fetchone()[0]
            top5_accuracy = (high_confidence / total_recognitions) * 100
        else:
            top5_accuracy = 0.0

        # 获取当前激活模型的信息
        active_model = db.execute('SELECT * FROM model_versions WHERE is_active = 1').fetchone()

        return jsonify({
            "success": True,
            "top1_accuracy": round(top1_accuracy, 2),
            "top5_accuracy": round(top5_accuracy, 2),
            "total_corrections": total_corrections,
            "total_recognitions": total_recognitions,
            "active_model": dict(active_model) if active_model else None
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@model_admin_bp.route('/admin/models/status', methods=['GET'])
@admin_required
def get_model_status():
    """获取当前模型状态"""
    try:
        db = get_db()
        active_model = db.execute('SELECT * FROM model_versions WHERE is_active = 1').fetchone()

        return jsonify({
            "success": True,
            "is_loaded": current_model is not None,
            "current_version": current_model_version,
            "active_model": dict(active_model) if active_model else None,
            "num_classes": len(class_names),
            "classes": class_names
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500