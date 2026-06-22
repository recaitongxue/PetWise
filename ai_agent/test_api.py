import requests

def safe_print(text):
    """安全打印包含特殊字符的文本"""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('utf-8', errors='replace').decode('gbk', errors='replace'))

# 测试健康检查
print("=== 测试健康检查 ===")
try:
    response = requests.get("http://localhost:8000/health")
    print("状态码:", response.status_code)
    print("响应:", response.json())
except Exception as e:
    print("错误:", e)

# 测试智能对话
print("\n=== 测试智能对话 ===")
try:
    response = requests.post("http://localhost:8000/chat", json={
        "user_message": "你好，请问你能帮我什么？",
        "use_knowledge_base": False,
        "temperature": 0.7
    })
    print("状态码:", response.status_code)
    result = response.json()
    print("成功:", result.get("success"))
    content = result.get("content", "")
    safe_print("回复: " + content)
except Exception as e:
    print("错误:", e)

# 测试宠物护理建议
print("\n=== 测试宠物护理建议 ===")
try:
    response = requests.post("http://localhost:8000/advice", json={
        "topic": "饮食",
        "pet_type": "狗狗",
        "specific_issue": "食欲不振"
    })
    print("状态码:", response.status_code)
    result = response.json()
    print("成功:", result.get("success"))
    advice = result.get("advice", "")
    safe_print("建议: " + advice)
except Exception as e:
    print("错误:", e)

# 测试获取服务信息
print("\n=== 测试服务信息 ===")
try:
    response = requests.get("http://localhost:8000/info")
    print("状态码:", response.status_code)
    result = response.json()
    print("服务名称:", result.get("service_name"))
    print("功能列表:", result.get("capabilities"))
except Exception as e:
    print("错误:", e)