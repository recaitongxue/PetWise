"""
管理端样本管理路由
支持难样本收集、审核、导出
"""
import os
import json
import zipfile
from datetime import datetime
from flask import Blueprint, request, jsonify, session, send_file
from models.db import get_db
from utils import log_action, admin_required
from config import Config

sample_admin_bp = Blueprint('sample_admin', __name__)

@sample_admin_bp.route('/admin/samples/hard', methods=['GET'])
@admin_required
def get_hard_examples():
    """获取难样本列表"""
    try:
        status = request.args.get('status', 'pending')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        offset = (page - 1) * per_page

        db = get_db()

        query = '''
            SELECT he.*, u.username as user_name, r.confidence as recognition_confidence
            FROM hard_examples he
            LEFT JOIN users u ON he.user_id = u.id
            LEFT JOIN recognitions r ON he.recognition_id = r.id
            WHERE 1=1
        '''
        params = []

        if status != 'all':
            query += ' AND he.status = ?'
            params.append(status)

        query += ' ORDER BY he.created_at DESC LIMIT ? OFFSET ?'
        params.extend([per_page, offset])

        samples = db.execute(query, params).fetchall()

        total_query = 'SELECT COUNT(*) FROM hard_examples WHERE 1=1'
        total_params = []

        if status != 'all':
            total_query += ' AND status = ?'
            total_params.append(status)

        total = db.execute(total_query, total_params).fetchone()[0]

        return jsonify({
            "success": True,
            "data": [dict(s) for s in samples],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@sample_admin_bp.route('/admin/samples/hard/<int:sample_id>/review', methods=['PUT'])
@admin_required
def review_hard_example(sample_id):
    """审核难样本"""
    try:
        data = request.get_json()
        action = data.get('action')  # 'approve', 'reject', 'relabel'
        new_label = data.get('new_label')
        notes = data.get('notes', '')

        if not action:
            return jsonify({"error": "action is required"}), 400

        admin_id = session['user_id']
        db = get_db()

        sample = db.execute('SELECT * FROM hard_examples WHERE id = ?', (sample_id,)).fetchone()
        if not sample:
            return jsonify({"error": "Sample not found"}), 404

        status = 'approved' if action == 'approve' else 'rejected'

        if action == 'relabel' and new_label:
            db.execute('''
                UPDATE hard_examples
                SET corrected_breed = ?, status = ?, reviewed_by = ?, reviewed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (new_label, status, admin_id, sample_id))
        else:
            db.execute('''
                UPDATE hard_examples
                SET status = ?, reviewed_by = ?, reviewed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (status, admin_id, sample_id))

        db.commit()

        log_action(db, admin_id, 'review_hard_example', {'sample_id': sample_id, 'action': action})

        return jsonify({
            "success": True,
            "message": f"Sample {action}d successfully"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@sample_admin_bp.route('/admin/samples/hard/export', methods=['POST'])
@admin_required
def export_hard_examples():
    """导出难样本为PyTorch训练集格式"""
    try:
        data = request.get_json()
        status = data.get('status', 'approved')
        include_relabel = data.get('include_relabel', True)

        db = get_db()

        query = 'SELECT * FROM hard_examples WHERE status = ?'
        params = [status]

        if include_relabel:
            query += ' AND corrected_breed IS NOT NULL'

        samples = db.execute(query, params).fetchall()

        if not samples:
            return jsonify({"error": "No samples to export"}), 400

        # 创建导出目录
        export_dir = os.path.join(Config.UPLOAD_FOLDER, 'exports')
        os.makedirs(export_dir, exist_ok=True)

        # 创建数据集结构
        dataset_dir = os.path.join(export_dir, 'hard_examples_dataset')
        os.makedirs(dataset_dir, exist_ok=True)

        # 按品种分类
        breed_to_samples = {}
        for sample in samples:
            breed = sample['corrected_breed'] if sample['corrected_breed'] else sample['predicted_breed']
            if breed not in breed_to_samples:
                breed_to_samples[breed] = []
            breed_to_samples[breed].append(dict(sample))

        # 复制图片并创建标签文件
        label_mapping = {}
        for breed, samples_list in breed_to_samples.items():
            breed_dir = os.path.join(dataset_dir, breed)
            os.makedirs(breed_dir, exist_ok=True)

            for idx, sample in enumerate(samples_list):
                if os.path.exists(sample['image_path']):
                    # 复制图片
                    src_path = sample['image_path']
                    dst_path = os.path.join(breed_dir, f"{sample['id']}_{idx}.jpg")
                    import shutil
                    shutil.copy2(src_path, dst_path)

        # 创建标签映射文件
        labels_file = os.path.join(dataset_dir, 'labels.txt')
        with open(labels_file, 'w', encoding='utf-8') as f:
            for idx, breed in enumerate(breed_to_samples.keys()):
                f.write(f"{idx},{breed}\n")
                label_mapping[breed] = idx

        # 创建元数据文件
        metadata_file = os.path.join(dataset_dir, 'metadata.json')
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump({
                'total_samples': len(samples),
                'breeds': list(breed_to_samples.keys()),
                'label_mapping': label_mapping,
                'exported_at': str(datetime.now()),
                'status': status
            }, f, ensure_ascii=False, indent=2)

        # 创建压缩包
        zip_path = os.path.join(export_dir, 'hard_examples.zip')
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(dataset_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, dataset_dir)
                    zipf.write(file_path, arcname)

        admin_id = session['user_id']
        log_action(db, admin_id, 'export_hard_examples', {'count': len(samples), 'status': status})

        return send_file(zip_path, as_attachment=True, download_name='hard_examples.zip')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@sample_admin_bp.route('/admin/samples/hard/<int:sample_id>', methods=['DELETE'])
@admin_required
def delete_hard_example(sample_id):
    """删除难样本"""
    try:
        admin_id = session['user_id']
        db = get_db()

        sample = db.execute('SELECT * FROM hard_examples WHERE id = ?', (sample_id,)).fetchone()
        if not sample:
            return jsonify({"error": "Sample not found"}), 404

        db.execute('DELETE FROM hard_examples WHERE id = ?', (sample_id,))
        db.commit()

        log_action(db, admin_id, 'delete_hard_example', {'sample_id': sample_id})

        return jsonify({"success": True, "message": "Sample deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@sample_admin_bp.route('/admin/samples/hard/stats', methods=['GET'])
@admin_required
def get_hard_examples_stats():
    """获取难样本统计信息"""
    try:
        db = get_db()

        stats = {
            'total': db.execute('SELECT COUNT(*) FROM hard_examples').fetchone()[0],
            'pending': db.execute('SELECT COUNT(*) FROM hard_examples WHERE status = "pending"').fetchone()[0],
            'approved': db.execute('SELECT COUNT(*) FROM hard_examples WHERE status = "approved"').fetchone()[0],
            'rejected': db.execute('SELECT COUNT(*) FROM hard_examples WHERE status = "rejected"').fetchone()[0],
            'low_confidence': db.execute('SELECT COUNT(*) FROM hard_examples WHERE is_low_confidence = 1').fetchone()[0],
            'user_corrected': db.execute('SELECT COUNT(*) FROM hard_examples WHERE is_user_corrected = 1').fetchone()[0]
        }

        # 按品种统计
        breed_stats = db.execute('''
            SELECT predicted_breed, COUNT(*) as count
            FROM hard_examples
            GROUP BY predicted_breed
            ORDER BY count DESC
            LIMIT 10
        ''').fetchall()

        return jsonify({
            "success": True,
            "stats": stats,
            "top_breeds": [dict(b) for b in breed_stats]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500