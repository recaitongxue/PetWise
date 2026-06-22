import os
import json
import uuid
import base64
from flask import Blueprint, request, jsonify
from models.db import get_db
from utils import allowed_file, log_action, get_current_user_id, login_required
from config import Config

recognize_bp = Blueprint('recognize', __name__)

MODEL_AVAILABLE = False
try:
    import torch
    import torch.nn as nn
    import torchvision.transforms as transforms
    from torchvision import models
    from PIL import Image
    MODEL_AVAILABLE = True
except Exception as e:
    print(f"Model loading failed: {e}")

class_names = [
    "中华田园犬", "吉娃娃", "哈士奇", "德牧", "拉布拉多", "杜宾",
    "柴犬", "法国斗牛", "萨摩耶", "藏獒", "金毛",
    "阿比西尼亚猫", "埃及猫", "豹猫", "布偶猫", "波斯猫", "缅甸猫",
    "俄罗斯蓝猫", "孟买猫", "缅因猫", "无毛猫", "暹罗猫", "英国短毛猫"
]

def create_model(num_classes):
    """Create model with same architecture as training"""
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

def load_model():
    """Load the pet recognition model"""
    try:
        model = create_model(len(class_names))
        
        if os.path.exists(Config.MODEL_PATH):
            checkpoint = torch.load(Config.MODEL_PATH, map_location='cpu')
            if 'model_state_dict' in checkpoint:
                model.load_state_dict(checkpoint['model_state_dict'])
                print(f"Model loaded from checkpoint (epoch {checkpoint.get('epoch', 'unknown')}, val_acc: {checkpoint.get('val_acc', 'unknown')})")
            else:
                model.load_state_dict(checkpoint)
                print("Model loaded from state_dict")
            model.eval()
            print("Model loaded successfully")
            return model
        else:
            print(f"Model file not found: {Config.MODEL_PATH}")
            return None
    except Exception as e:
        print(f"Failed to load model: {e}")
        import traceback
        traceback.print_exc()
        return None

model = load_model() if MODEL_AVAILABLE else None

def predict_image(image_path):
    """Predict pet breed from image"""
    try:
        if not model:
            print("Model not loaded")
            return {"breed": "未知", "confidence": 0.0, "category": "unknown", "top5": []}

        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

        img = Image.open(image_path).convert('RGB')
        img_tensor = transform(img).unsqueeze(0)

        with torch.no_grad():
            outputs = model(img_tensor)
            probs = torch.nn.functional.softmax(outputs, dim=1)
            top5_probs, top5_indices = torch.topk(probs, 5)

        top5 = []
        for i in range(5):
            top5.append({
                "class": class_names[top5_indices[0][i].item()],
                "confidence": round(top5_probs[0][i].item(), 4)
            })

        breed = class_names[top5_indices[0][0].item()]
        confidence = round(top5_probs[0][0].item(), 4)
        category = "dog" if class_names.index(breed) < 11 else "cat"

        print(f"Prediction: {breed}, Confidence: {confidence}")
        return {"breed": breed, "confidence": confidence, "category": category, "top5": top5}
    except Exception as e:
        print(f"Prediction failed: {e}")
        import traceback
        traceback.print_exc()
        return {"breed": "未知", "confidence": 0.0, "category": "unknown", "top5": []}

@recognize_bp.route('/recognize', methods=['POST'])
@login_required
def recognize():
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No image selected"}), 400

    if not allowed_file(file.filename, Config.ALLOWED_EXTENSIONS):
        return jsonify({"error": "Invalid file type"}), 400

    try:
        filename = f"{uuid.uuid4().hex}.jpg"
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        print(f"Image saved to: {filepath}")

        result = predict_image(filepath)

        user_id = get_current_user_id()
        db = get_db()

        db.execute('''
            INSERT INTO recognitions (user_id, image_path, result, confidence, breed, top5)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, filename, result['breed'], result['confidence'], result['breed'], json.dumps(result['top5'])))
        db.commit()

        recognition_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]

        db.execute('UPDATE breed_info SET views = views + 1 WHERE breed = ?', (result['breed'],))
        db.commit()

        breed_info = db.execute('SELECT * FROM breed_info WHERE breed = ?', (result['breed'],)).fetchone()

        log_action(db, user_id, 'recognize', {'breed': result['breed'], 'confidence': result['confidence']})

        return jsonify({
            "success": True,
            "result": result,
            "recognition_id": recognition_id,
            "breed_info": dict(breed_info) if breed_info else None,
            "model_available": MODEL_AVAILABLE
        })
    except Exception as e:
        print(f"Recognize error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@recognize_bp.route('/recognize/base64', methods=['POST'])
@login_required
def recognize_base64():
    try:
        data = request.get_json()
        image_base64 = data.get('image_base64')
        
        if not image_base64:
            return jsonify({"error": "No image data provided"}), 400

        filename = f"{uuid.uuid4().hex}.jpg"
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        
        image_data = base64.b64decode(image_base64)
        with open(filepath, 'wb') as f:
            f.write(image_data)

        result = predict_image(filepath)

        user_id = get_current_user_id()
        db = get_db()

        db.execute('''
            INSERT INTO recognitions (user_id, image_path, result, confidence, breed, top5)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, filename, result['breed'], result['confidence'], result['breed'], json.dumps(result['top5'])))
        db.commit()

        db.execute('UPDATE breed_info SET views = views + 1 WHERE breed = ?', (result['breed'],))
        db.commit()

        breed_info = db.execute('SELECT * FROM breed_info WHERE breed = ?', (result['breed'],)).fetchone()

        log_action(db, user_id, 'recognize_base64', {'breed': result['breed'], 'confidence': result['confidence']})

        return jsonify({
            "success": True,
            "result": result,
            "breed_info": dict(breed_info) if breed_info else None,
            "model_available": MODEL_AVAILABLE
        })
    except Exception as e:
        print(f"Recognize base64 error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@recognize_bp.route('/recognize/history', methods=['GET'])
@login_required
def recognize_history():
    try:
        user_id = get_current_user_id()
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        offset = (page - 1) * per_page

        db = get_db()
        histories = db.execute('''
            SELECT id, image_path, result, confidence, breed, top5, created_at 
            FROM recognitions 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
        ''', (user_id, per_page, offset)).fetchall()

        total = db.execute('SELECT COUNT(*) FROM recognitions WHERE user_id = ?', (user_id,)).fetchone()[0]

        return jsonify({
            "success": True,
            "data": [dict(h) for h in histories],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@recognize_bp.route('/recognize/history/<int:history_id>', methods=['DELETE'])
@login_required
def delete_recognition(history_id):
    try:
        user_id = get_current_user_id()
        db = get_db()

        recognition = db.execute('SELECT * FROM recognitions WHERE id = ? AND user_id = ?', (history_id, user_id)).fetchone()
        if not recognition:
            return jsonify({"error": "Recognition not found"}), 404

        db.execute('DELETE FROM recognitions WHERE id = ?', (history_id,))
        db.commit()

        return jsonify({"success": True, "message": "Recognition deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@recognize_bp.route('/breeds', methods=['GET'])
def get_breeds():
    try:
        db = get_db()
        breeds = db.execute('SELECT * FROM breed_info ORDER BY views DESC, category, breed').fetchall()
        
        return jsonify({
            "success": True,
            "breeds": [dict(b) for b in breeds],
            "total": len(breeds),
            "model_available": MODEL_AVAILABLE
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@recognize_bp.route('/classes', methods=['GET'])
def get_classes():
    try:
        db = get_db()
        breeds = db.execute('SELECT breed, category FROM breed_info ORDER BY category, breed').fetchall()
        
        return jsonify({
            "success": True,
            "categories": {
                "dog": [b['breed'] for b in breeds if b['category'] == 'dog'],
                "cat": [b['breed'] for b in breeds if b['category'] == 'cat']
            },
            "total_classes": len(breeds),
            "model_available": MODEL_AVAILABLE
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@recognize_bp.route('/breeds/popular', methods=['GET'])
def get_popular_breeds():
    try:
        db = get_db()
        breeds = db.execute('SELECT * FROM breed_info ORDER BY views DESC LIMIT 10').fetchall()
        
        return jsonify({
            "success": True,
            "breeds": [dict(b) for b in breeds],
            "total": len(breeds)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@recognize_bp.route('/breed/<breed_name>', methods=['GET'])
def get_breed_detail(breed_name):
    try:
        db = get_db()
        breed = db.execute('SELECT * FROM breed_info WHERE breed = ?', (breed_name,)).fetchone()
        
        if not breed:
            return jsonify({"error": "Breed not found"}), 404

        return jsonify({
            "success": True,
            "breed": dict(breed)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@recognize_bp.route('/model/status', methods=['GET'])
def model_status():
    try:
        return jsonify({
            "success": True,
            "model_available": MODEL_AVAILABLE and model is not None,
            "model_path": Config.MODEL_PATH,
            "model_exists": os.path.exists(Config.MODEL_PATH),
            "num_classes": len(class_names),
            "classes": class_names
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@recognize_bp.route('/recognize/camera', methods=['POST'])
@login_required
def recognize_camera():
    try:
        data = request.get_json()
        image_base64 = data.get('image_base64')
        session_id = data.get('session_id', str(uuid.uuid4()))
        
        if not image_base64:
            return jsonify({"error": "No image data provided"}), 400

        filename = f"camera_{uuid.uuid4().hex}.jpg"
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        
        image_data = base64.b64decode(image_base64)
        with open(filepath, 'wb') as f:
            f.write(image_data)

        result = predict_image(filepath)

        user_id = get_current_user_id()
        db = get_db()

        db.execute('''
            INSERT INTO recognitions (user_id, session_id, image_path, result, confidence, breed, top5)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, session_id, filepath, result['breed'], result['confidence'], result['breed'], json.dumps(result['top5'])))
        db.commit()

        db.execute('UPDATE breed_info SET views = views + 1 WHERE breed = ?', (result['breed'],))
        db.commit()

        breed_info = db.execute('SELECT * FROM breed_info WHERE breed = ?', (result['breed'],)).fetchone()

        log_action(db, user_id, 'recognize_camera', {'breed': result['breed'], 'confidence': result['confidence'], 'session_id': session_id})

        return jsonify({
            "success": True,
            "result": result,
            "breed_info": dict(breed_info) if breed_info else None,
            "model_available": MODEL_AVAILABLE,
            "session_id": session_id
        })
    except Exception as e:
        print(f"Camera recognition error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@recognize_bp.route('/recognize/camera/stream', methods=['POST'])
@login_required
def recognize_camera_stream():
    try:
        data = request.get_json()
        images = data.get('images', [])
        session_id = data.get('session_id', str(uuid.uuid4()))
        
        if not images or len(images) == 0:
            return jsonify({"error": "No images provided"}), 400

        results = []
        user_id = get_current_user_id()
        db = get_db()

        for idx, image_base64 in enumerate(images):
            try:
                filename = f"stream_{session_id}_{idx}_{uuid.uuid4().hex}.jpg"
                filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
                
                image_data = base64.b64decode(image_base64)
                with open(filepath, 'wb') as f:
                    f.write(image_data)

                result = predict_image(filepath)
                result['frame_index'] = idx
                result['image_path'] = filename
                
                db.execute('''
                    INSERT INTO recognitions (user_id, session_id, image_path, result, confidence, breed, top5)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, session_id, filename, result['breed'], result['confidence'], result['breed'], json.dumps(result['top5'])))
                
                db.execute('UPDATE breed_info SET views = views + 1 WHERE breed = ?', (result['breed'],))
                
                results.append(result)
            except Exception as e:
                print(f"Frame {idx} error: {e}")
                results.append({"breed": "未知", "confidence": 0.0, "category": "unknown", "top5": [], "frame_index": idx})

        db.commit()

        log_action(db, user_id, 'recognize_camera_stream', {'session_id': session_id, 'frame_count': len(images)})

        return jsonify({
            "success": True,
            "results": results,
            "session_id": session_id,
            "model_available": MODEL_AVAILABLE
        })
    except Exception as e:
        print(f"Camera stream error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@recognize_bp.route('/recognize/camera/session/<session_id>', methods=['GET'])
@login_required
def get_camera_session(session_id):
    try:
        user_id = get_current_user_id()
        db = get_db()

        records = db.execute('''
            SELECT id, result, confidence, breed, top5, created_at 
            FROM recognitions 
            WHERE user_id = ? AND session_id = ? 
            ORDER BY created_at DESC
        ''', (user_id, session_id)).fetchall()

        return jsonify({
            "success": True,
            "data": [dict(r) for r in records]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@recognize_bp.route('/recognize/camera/sessions', methods=['GET'])
@login_required
def get_camera_sessions():
    try:
        user_id = get_current_user_id()
        db = get_db()

        sessions = db.execute('''
            SELECT session_id, COUNT(*) as count, MIN(created_at) as start_time, MAX(created_at) as end_time
            FROM recognitions 
            WHERE user_id = ? AND session_id IS NOT NULL 
            GROUP BY session_id 
            ORDER BY start_time DESC
        ''', (user_id,)).fetchall()

        return jsonify({
            "success": True,
            "data": [dict(s) for s in sessions]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@recognize_bp.route('/recognize/batch', methods=['POST'])
@login_required
def recognize_batch():
    if 'images' not in request.files:
        return jsonify({"error": "No images provided"}), 400

    files = request.files.getlist('images')
    if len(files) == 0:
        return jsonify({"error": "No images selected"}), 400

    if len(files) > 10:
        return jsonify({"error": "Maximum 10 images per batch"}), 400

    try:
        results = []
        user_id = get_current_user_id()
        db = get_db()

        for idx, file in enumerate(files):
            if not allowed_file(file.filename, Config.ALLOWED_EXTENSIONS):
                results.append({
                    "index": idx,
                    "filename": file.filename,
                    "error": "Invalid file type"
                })
                continue

            filename = f"batch_{uuid.uuid4().hex}.jpg"
            filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
            file.save(filepath)

            result = predict_image(filepath)

            db.execute('''
                INSERT INTO recognitions (user_id, image_path, result, confidence, breed, top5)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, filename, result['breed'], result['confidence'], result['breed'], json.dumps(result['top5'])))
            
            db.execute('UPDATE breed_info SET views = views + 1 WHERE breed = ?', (result['breed'],))

            results.append({
                "index": idx,
                "filename": file.filename,
                "success": True,
                "result": result,
                "image_path": filename
            })

            if result['confidence'] < 0.5:
                db.execute('''
                    INSERT INTO hard_examples (user_id, image_path, predicted_breed, confidence, is_low_confidence, collected_reason, status)
                    VALUES (?, ?, ?, ?, 1, ?, 'pending')
                ''', (user_id, filename, result['breed'], result['confidence'], 'low_confidence'))

        db.commit()

        log_action(db, user_id, 'recognize_batch', {'count': len(files), 'success_count': len([r for r in results if r.get('success')])})

        return jsonify({
            "success": True,
            "results": results,
            "total": len(files),
            "success_count": len([r for r in results if r.get('success')])
        })
    except Exception as e:
        print(f"Batch recognition error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@recognize_bp.route('/recognize/correct', methods=['POST'])
@login_required
def correct_recognition():
    try:
        data = request.get_json()
        recognition_id = data.get('recognition_id')
        corrected_breed = data.get('corrected_breed')
        reason = data.get('reason', '')

        if not recognition_id or not corrected_breed:
            return jsonify({"error": "recognition_id and corrected_breed are required"}), 400

        user_id = get_current_user_id()
        db = get_db()

        recognition = db.execute('SELECT * FROM recognitions WHERE id = ? AND user_id = ?', (recognition_id, user_id)).fetchone()
        if not recognition:
            return jsonify({"error": "Recognition not found"}), 404

        db.execute('''
            INSERT INTO corrections (recognition_id, user_id, original_breed, corrected_breed, confidence, reason, status)
            VALUES (?, ?, ?, ?, ?, ?, 'pending')
        ''', (recognition_id, user_id, recognition['breed'], corrected_breed, recognition['confidence'], reason))

        db.execute('''
            INSERT INTO hard_examples (recognition_id, user_id, image_path, predicted_breed, confidence, is_user_corrected, corrected_breed, collected_reason, status)
            VALUES (?, ?, ?, ?, ?, 1, ?, ?, 'pending')
        ''', (recognition_id, user_id, recognition['image_path'], recognition['breed'], recognition['confidence'], corrected_breed, 'user_correction'))

        db.commit()
        
        cursor = db.cursor()
        correction_id = cursor.execute('SELECT last_insert_rowid()').fetchone()[0]

        log_action(db, user_id, 'correct_recognition', {
            'recognition_id': recognition_id,
            'original_breed': recognition['breed'],
            'corrected_breed': corrected_breed
        })

        return jsonify({
            "success": True,
            "message": "Correction submitted successfully",
            "correction_id": correction_id
        })
    except Exception as e:
        print(f"Correction error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@recognize_bp.route('/recognize/corrections', methods=['GET'])
@login_required
def get_corrections():
    try:
        user_id = get_current_user_id()
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        status = request.args.get('status', 'all')
        offset = (page - 1) * per_page

        db = get_db()

        query = '''
            SELECT c.*, r.image_path, r.confidence as original_confidence
            FROM corrections c
            LEFT JOIN recognitions r ON c.recognition_id = r.id
            WHERE c.user_id = ?
        '''
        params = [user_id]

        if status != 'all':
            query += ' AND c.status = ?'
            params.append(status)

        query += ' ORDER BY c.created_at DESC LIMIT ? OFFSET ?'
        params.extend([per_page, offset])

        corrections = db.execute(query, params).fetchall()

        total_query = '''
            SELECT COUNT(*)
            FROM corrections
            WHERE user_id = ?
        '''
        total_params = [user_id]

        if status != 'all':
            total_query += ' AND status = ?'
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