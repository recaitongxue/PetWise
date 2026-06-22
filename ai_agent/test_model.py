import requests

def safe_print(text):
    """安全打印包含特殊字符的文本"""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('utf-8', errors='replace').decode('gbk', errors='replace'))

# 测试1：获取可用模型列表
print("=== 测试1：获取可用模型列表 ===")
try:
    response = requests.get("http://localhost:8000/models")
    print("状态码:", response.status_code)
    result = response.json()
    print("默认模型:", result.get("default_model"))
    print("可用模型数:", result.get("count"))
    for model in result.get("models", []):
        print(f"- {model['name']}: {model['description']}")
except Exception as e:
    print("错误:", e)

# 测试2：使用默认模型对话
print("\n=== 测试2：使用默认模型对话 ===")
try:
    response = requests.post("http://localhost:8000/chat", json={
        "user_message": "什么是宠物智能识别？",
        "use_knowledge_base": False,
        "temperature": 0.7
    })
    print("状态码:", response.status_code)
    result = response.json()
    print("成功:", result.get("success"))
    content = result.get("content", "")
    safe_print("回复(默认模型): " + content[:100] + "..." if len(content) > 100 else content)
except Exception as e:
    print("错误:", e)

# 测试3：指定模型对话
print("\n=== 测试3：指定模型对话 ===")
try:
    response = requests.post("http://localhost:8000/chat", json={
        "user_message": "猫咪有哪些常见品种？",
        "use_knowledge_base": True,
        "temperature": 0.7,
        "model": "Qwen/Qwen2-7B-Instruct"
    })
    print("状态码:", response.status_code)
    result = response.json()
    print("成功:", result.get("success"))
    content = result.get("content", "")
    safe_print("回复(指定模型): " + content[:100] + "..." if len(content) > 100 else content)
except Exception as e:
    print("错误:", e)

print("\n=== 测试完成 ===")