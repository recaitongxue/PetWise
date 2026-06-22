import requests

def safe_print(text):
    """安全打印包含特殊字符的文本"""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('utf-8', errors='replace').decode('gbk', errors='replace'))

# 测试1：查看知识库统计
print("=== 测试1：知识库统计 ===")
try:
    response = requests.get("http://localhost:8000/knowledge/stats")
    print("状态码:", response.status_code)
    result = response.json()
    print("总条目数:", result.get("total_entries"))
    print("分类:", result.get("categories"))
except Exception as e:
    print("错误:", e)

# 测试2：获取所有分类
print("\n=== 测试2：获取分类列表 ===")
try:
    response = requests.get("http://localhost:8000/knowledge/categories")
    print("状态码:", response.status_code)
    result = response.json()
    print("分类:", result.get("categories"))
except Exception as e:
    print("错误:", e)

# 测试3：查询知识库
print("\n=== 测试3：查询知识库 ===")
try:
    response = requests.post("http://localhost:8000/knowledge/query", json={
        "query": "金毛",
        "limit": 3
    })
    print("状态码:", response.status_code)
    result = response.json()
    print("查询结果数:", result.get("count"))
    for item in result.get("results", []):
        print(f"- ID: {item['id']}")
        print(f"  分类: {item['category']}")
        print(f"  相关性: {item['relevance']:.2f}")
except Exception as e:
    print("错误:", e)

# 测试4：添加新的知识
print("\n=== 测试4：添加新知识 ===")
try:
    new_knowledge = {
        "title": "猫咪疫苗接种指南",
        "content": {
            "core_vaccines": ["猫瘟", "猫疱疹病毒", "猫杯状病毒"],
            "schedule": ["8周", "12周", "16周", "1年后加强"],
            "notes": "接种后观察30分钟，保持接种部位清洁"
        }
    }
    
    response = requests.post("http://localhost:8000/knowledge/import", json={
        "knowledge_data": new_knowledge,
        "category": "cat_health"
    })
    print("状态码:", response.status_code)
    result = response.json()
    print("成功:", result.get("success"))
    if result.get("knowledge_id"):
        print("新添知识ID:", result.get("knowledge_id"))
        new_knowledge_id = result.get("knowledge_id")
except Exception as e:
    print("错误:", e)
    new_knowledge_id = None

# 测试5：查询新增的知识
print("\n=== 测试5：查询新增知识 ===")
if new_knowledge_id:
    try:
        response = requests.get(f"http://localhost:8000/knowledge/{new_knowledge_id}")
        print("状态码:", response.status_code)
        result = response.json()
        if result.get("success"):
            print("知识标题:", result["data"]["data"].get("title"))
    except Exception as e:
        print("错误:", e)

# 测试6：使用知识库进行对话
print("\n=== 测试6：使用知识库对话 ===")
try:
    response = requests.post("http://localhost:8000/chat", json={
        "user_message": "猫咪需要接种哪些疫苗？",
        "use_knowledge_base": True,
        "temperature": 0.7
    })
    print("状态码:", response.status_code)
    result = response.json()
    print("成功:", result.get("success"))
    content = result.get("content", "")
    safe_print("回复: " + content[:200] + "..." if len(content) > 200 else content)
except Exception as e:
    print("错误:", e)

# 测试7：更新知识
print("\n=== 测试7：更新知识 ===")
if new_knowledge_id:
    try:
        updated_data = {
            "title": "猫咪疫苗接种指南（更新版）",
            "content": {
                "core_vaccines": ["猫瘟", "猫疱疹病毒", "猫杯状病毒", "狂犬病"],
                "schedule": ["8周", "12周", "16周", "1年后加强"],
                "notes": "接种后观察30分钟，保持接种部位清洁",
                "updated_at": "2026-05-21"
            }
        }
        
        response = requests.put("http://localhost:8000/knowledge", json={
            "knowledge_id": new_knowledge_id,
            "knowledge_data": updated_data
        })
        print("状态码:", response.status_code)
        result = response.json()
        print("成功:", result.get("success"))
    except Exception as e:
        print("错误:", e)

# 测试8：最终统计
print("\n=== 测试8：最终统计 ===")
try:
    response = requests.get("http://localhost:8000/knowledge/stats")
    print("状态码:", response.status_code)
    result = response.json()
    print("总条目数:", result.get("total_entries"))
except Exception as e:
    print("错误:", e)