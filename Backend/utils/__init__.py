import os
import hashlib
import uuid
import json

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

def generate_suggestions(message, breed_context):
    if not breed_context:
        return [
            "我可以帮你识别宠物的品种",
            "问我关于宠物饲养的问题",
            "了解宠物的健康护理知识"
        ]
    return [
        f"告诉我关于{breed_context}的性格特点",
        f"{breed_context}一天需要喂几次？",
        f"{breed_context}容易患什么疾病？",
        f"如何训练{breed_context}？"
    ]

def generate_fallback_response(prompt, breed_context):
    prompt_lower = prompt.lower()

    if any(k in prompt_lower for k in ['怎么', '饲养', '喂养', '吃', '喂']):
        return f"关于饲养建议：{breed_context}需要均衡饮食，建议使用专用宠物粮，每日定时定量喂养。"
    elif any(k in prompt_lower for k in ['健康', '生病', '症状', '不舒服']):
        return f"健康提示：定期带{breed_context}进行体检，接种疫苗很重要。"
    elif any(k in prompt_lower for k in ['训练', '教', '上厕所', '规矩']):
        return f"训练建议：对{breed_context}进行基础训练时，请保持耐心，使用正向激励法。"
    elif any(k in prompt_lower for k in ['美容', '洗澡', '毛发', '护理']):
        return f"护理建议：{breed_context}需要定期梳理毛发，一般每月1-2次洗澡。"
    elif any(k in prompt_lower for k in ['性格', '特点', '习性']):
        return f"性格特点：{breed_context}通常性格独特，了解其品种特点有助于更好地相处。"
    else:
        return f"感谢您的提问！关于{breed_context}，如果您有具体问题，建议咨询专业兽医。"