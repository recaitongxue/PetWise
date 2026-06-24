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
        status = request.args.get('status', '')
        sample_type = request.args.get('type', '')
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

        if status and status != 'all':
            query += ' AND he.status = ?'
            params.append(status)

        if sample_type == 'hard':
            query += ' AND he.is_low_confidence = 1'
        elif sample_type == 'correction':
            query += ' AND he.is_user_corrected = 1'

        query += ' ORDER BY he.created_at DESC LIMIT ? OFFSET ?'
        params.extend([per_page, offset])

        samples = db.execute(query, params).fetchall()

        total_query = 'SELECT COUNT(*) FROM hard_examples WHERE 1=1'
        total_params = []

        if status and status != 'all':
            total_query += ' AND status = ?'
            total_params.append(status)

        if sample_type == 'hard':
            total_query += ' AND is_low_confidence = 1'
        elif sample_type == 'correction':
            total_query += ' AND is_user_corrected = 1'

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

        if action not in ['approve', 'reject', 'relabel']:
            return jsonify({"error": "Invalid action. Must be 'approve', 'reject', or 'relabel'"}), 400

        if action == 'relabel' and not new_label:
            return jsonify({"error": "new_label is required for relabel action"}), 400

        admin_id = session.get('user_id')
        if not admin_id:
            return jsonify({"error": "Admin not authenticated"}), 401

        db = get_db()

        sample = db.execute('SELECT * FROM hard_examples WHERE id = ?', (sample_id,)).fetchone()
        if not sample:
            return jsonify({"error": "Sample not found"}), 404

        status = 'approved' if action in ['approve', 'relabel'] else 'rejected'

        if action == 'relabel':
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
        import traceback
        print(f"Review error: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500

@sample_admin_bp.route('/admin/samples/hard/export', methods=['POST'])
@admin_required
def export_hard_examples():
    """导出难样本为PyTorch训练集格式（类别文件夹结构）"""
    try:
        import shutil as shutil_mod
        data = request.get_json() or {}
        status = data.get('status', 'approved')
        include_relabel = data.get('include_relabel', True)

        db = get_db()

        query = 'SELECT * FROM hard_examples WHERE status = ?'
        params = [status]

        samples = db.execute(query, params).fetchall()

        if not samples:
            return jsonify({"error": f"No {status} samples to export"}), 400

        filtered_samples = []
        for sample in samples:
            if include_relabel:
                if sample['corrected_breed']:
                    filtered_samples.append(sample)
            else:
                filtered_samples.append(sample)

        if not filtered_samples:
            return jsonify({"error": f"No {status} samples with corrected breed to export"}), 400

        # 创建导出目录
        export_dir = os.path.join(Config.UPLOAD_FOLDER, 'exports')
        os.makedirs(export_dir, exist_ok=True)

        # 每次导出前清理旧的dataset目录，避免残留文件
        dataset_dir = os.path.join(export_dir, 'hard_examples_dataset')
        if os.path.exists(dataset_dir):
            shutil_mod.rmtree(dataset_dir)
        os.makedirs(dataset_dir)

        # 按品种分类
        breed_to_samples = {}
        for sample in filtered_samples:
            breed = sample['corrected_breed'] if (include_relabel and sample['corrected_breed']) else sample['predicted_breed']
            # 清理品种名中的非法字符
            breed_clean = breed.replace('/', '_').replace('\\', '_').replace(':', '_').strip()
            if breed_clean not in breed_to_samples:
                breed_to_samples[breed_clean] = []
            breed_to_samples[breed_clean].append(dict(sample))

        # 复制图片到对应品种文件夹
        label_mapping = {}
        for idx, (breed, samples_list) in enumerate(breed_to_samples.items()):
            breed_dir = os.path.join(dataset_dir, breed)
            os.makedirs(breed_dir, exist_ok=True)

            for sample_idx, sample in enumerate(samples_list):
                if os.path.exists(sample['image_path']):
                    src_path = sample['image_path']
                    # 使用原始文件扩展名
                    ext = os.path.splitext(src_path)[1] or '.jpg'
                    dst_path = os.path.join(breed_dir, f"{sample['id']}_{sample_idx}{ext}")
                    shutil_mod.copy2(src_path, dst_path)

            label_mapping[breed] = idx

        # 创建标签映射文件
        labels_file = os.path.join(dataset_dir, 'labels.txt')
        with open(labels_file, 'w', encoding='utf-8') as f:
            for idx, breed in enumerate(breed_to_samples.keys()):
                f.write(f"{idx},{breed}\n")

        # 创建元数据文件
        metadata_file = os.path.join(dataset_dir, 'metadata.json')
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump({
                'total_samples': len(filtered_samples),
                'breeds': list(breed_to_samples.keys()),
                'label_mapping': label_mapping,
                'exported_at': str(datetime.now()),
                'status': status,
                'include_relabel': include_relabel
            }, f, ensure_ascii=False, indent=2)

        # 创建压缩包（使用正斜杠确保跨平台兼容）
        zip_path = os.path.join(export_dir, 'hard_examples.zip')
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(dataset_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    # 使用正斜杠作为zip内部路径分隔符
                    arcname = os.path.relpath(file_path, dataset_dir).replace(os.sep, '/')
                    zipf.write(file_path, arcname)

        admin_id = session.get('user_id')
        if admin_id:
            log_action(db, admin_id, 'export_hard_examples', {'count': len(filtered_samples), 'status': status})

        return send_file(zip_path, as_attachment=True, download_name='hard_examples.zip')
    except Exception as e:
        import traceback
        print(f"Export error: {traceback.format_exc()}")
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