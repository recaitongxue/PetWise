"""
后端API测试脚本
测试所有主要API端点是否正常工作
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_endpoint(method, endpoint, data=None, files=None, token=None):
    """测试单个API端点"""
    url = f"{BASE_URL}{endpoint}"
    headers = {}
    if token:
        headers['Cookie'] = f"session={token}"

    try:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            if files:
                response = requests.post(url, headers=headers, files=files)
            else:
                response = requests.post(url, headers=headers, json=data)
        elif method == 'PUT':
            response = requests.put(url, headers=headers, json=data)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)

        status = "✓" if response.status_code < 400 else "✗"
        return {
            "endpoint": endpoint,
            "method": method,
            "status_code": response.status_code,
            "success": response.status_code < 400,
            "status": status,
            "response": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text[:100]
        }
    except Exception as e:
        return {
            "endpoint": endpoint,
            "method": method,
            "status_code": 0,
            "success": False,
            "status": "✗",
            "response": str(e)
        }

def main():
    print("=" * 60)
    print("PetWise 后端API测试")
    print("=" * 60)

    results = []

    # 测试用户认证
    print("\n📋 测试用户认证模块...")
    results.append(test_endpoint('POST', '/api/auth/register', {
        "username": "testuser_new",
        "password": "test123",
        "email": "test_new@example.com"
    }))
    results.append(test_endpoint('POST', '/api/auth/login', {
        "username": "admin",
        "password": "admin123"
    }))

    # 获取token用于后续测试
    login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    token = login_response.cookies.get('session')

    # 测试模型状态
    print("\n📋 测试模型模块...")
    results.append(test_endpoint('GET', '/api/model/status', token=token))
    results.append(test_endpoint('GET', '/api/classes', token=token))

    # 测试识别模块
    print("\n📋 测试识别模块...")
    results.append(test_endpoint('GET', '/api/recognize/history', token=token))
    results.append(test_endpoint('GET', '/api/recognize/camera/sessions', token=token))

    # 测试AI智能体模块
    print("\n📋 测试AI智能体模块...")
    results.append(test_endpoint('POST', '/api/agent/chat', {
        "message": "你好",
        "session_id": "test"
    }, token=token))
    results.append(test_endpoint('GET', '/api/agent/history', token=token))
    results.append(test_endpoint('GET', '/api/agent/health', token=token))

    # 测试宠物档案模块
    print("\n📋 测试宠物档案模块...")
    results.append(test_endpoint('GET', '/api/pets', token=token))

    # 测试收藏模块
    print("\n📋 测试收藏模块...")
    results.append(test_endpoint('GET', '/api/favorites', token=token))

    # 测试评论模块
    print("\n📋 测试评论模块...")
    results.append(test_endpoint('GET', '/api/comments/金毛', token=token))

    # 测试健康记录模块
    print("\n📋 测试健康记录模块...")
    results.append(test_endpoint('GET', '/api/schedule/upcoming', token=token))

    # 测试管理端模块
    print("\n📋 测试管理端模块...")
    results.append(test_endpoint('GET', '/api/admin/stats', token=token))
    results.append(test_endpoint('GET', '/api/admin/users', token=token))
    results.append(test_endpoint('GET', '/api/admin/models', token=token))
    results.append(test_endpoint('GET', '/api/admin/knowledge', token=token))
    results.append(test_endpoint('GET', '/api/admin/announcements', token=token))

    # 测试模型管理
    print("\n📋 测试模型管理模块...")
    results.append(test_endpoint('GET', '/api/admin/models/accuracy', token=token))
    results.append(test_endpoint('GET', '/api/admin/models/status', token=token))

    # 测试样本管理
    print("\n📋 测试样本管理模块...")
    results.append(test_endpoint('GET', '/api/admin/samples/hard', token=token))
    results.append(test_endpoint('GET', '/api/admin/samples/hard/stats', token=token))

    # 打印测试结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)

    success_count = sum(1 for r in results if r['success'])
    total_count = len(results)

    for result in results:
        status_color = "\033[92m" if result['success'] else "\033[91m"
        print(f"{status_color}{result['status']}\033[0m {result['method']:6} {result['endpoint']:40} [{result['status_code']}]")

    print("\n" + "=" * 60)
    print(f"总计: {success_count}/{total_count} 个端点测试通过")
    print("=" * 60)

    # 保存详细结果到文件
    with open('api_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("\n详细测试结果已保存到 api_test_results.json")

if __name__ == '__main__':
    main()