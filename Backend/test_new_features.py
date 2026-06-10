import requests
import json

BASE_URL = 'http://localhost:5000'

def print_separator(test_name):
    print('\n' + '='*60)
    print(f' 测试: {test_name}')
    print('='*60)

def test_result(success, message):
    status = '✅ PASS' if success else '❌ FAIL'
    print(f'{status}: {message}')

test_stats = {'total': 0, 'passed': 0, 'failed': 0}

def run_test(name, func):
    test_stats['total'] += 1
    try:
        result = func()
        if result:
            test_stats['passed'] += 1
            test_result(True, name)
        else:
            test_stats['failed'] += 1
            test_result(False, name)
    except Exception as e:
        test_stats['failed'] += 1
        test_result(False, f'{name} - 异常: {e}')

print('\n' + '#'*60)
print('# PetWise 新增功能测试')
print('#'*60)

# 管理员登录
admin_token = None
try:
    resp = requests.post(f'{BASE_URL}/api/auth/login',
        json={'username': 'admin', 'password': 'admin123'},
        timeout=10)
    result = resp.json()
    if result.get('success') and result.get('token'):
        admin_token = result['token']
        test_result(True, '管理员登录成功')
    else:
        test_result(False, '管理员登录失败')
except Exception as e:
    test_result(False, f'管理员登录异常: {e}')

admin_headers = {'Authorization': f'Bearer {admin_token}'} if admin_token else {}

# ==================== 限流配置测试 ====================
print_separator('限流配置管理')

def test_rate_limit_add():
    try:
        resp = requests.post(f'{BASE_URL}/api/admin/rate-limits',
            json={'endpoint': '/api/recognize_test', 'daily_limit': 50, 'hourly_limit': 10, 'description': '测试限流'},
            headers=admin_headers, timeout=10)
        return resp.status_code in [200, 201] or 'already exists' in resp.text
    except:
        return False

def test_rate_limit_list():
    try:
        resp = requests.get(f'{BASE_URL}/api/admin/rate-limits', headers=admin_headers, timeout=10)
        result = resp.json()
        return result.get('success') and len(result.get('data', [])) > 0
    except:
        return False

run_test('添加限流配置', test_rate_limit_add)
run_test('获取限流配置列表', test_rate_limit_list)

# ==================== 敏感词管理测试 ====================
print_separator('敏感词管理')

def test_sensitive_word_add():
    try:
        resp = requests.post(f'{BASE_URL}/api/admin/sensitive-words',
            json={'word': '手术测试', 'category': 'medical', 'severity': 'high'},
            headers=admin_headers, timeout=10)
        return resp.status_code in [200, 201] or 'exists' in resp.text
    except:
        return False

def test_sensitive_word_list():
    try:
        resp = requests.get(f'{BASE_URL}/api/admin/sensitive-words', headers=admin_headers, timeout=10)
        result = resp.json()
        return result.get('success') and len(result.get('data', [])) > 0
    except:
        return False

run_test('添加敏感词', test_sensitive_word_add)
run_test('获取敏感词列表', test_sensitive_word_list)

# ==================== Prompt模板管理测试 ====================
print_separator('Prompt模板管理')

def test_prompt_add():
    try:
        resp = requests.post(f'{BASE_URL}/api/admin/prompt-templates',
            json={
                'name': '通用对话模板',
                'prompt_type': 'general',
                'content': '你是一个宠物助手，请回答关于宠物的问题。',
                'variables': '{user_question}',
                'is_active': 1
            },
            headers=admin_headers, timeout=10)
        return resp.status_code in [200, 201]
    except:
        return False

def test_prompt_list():
    try:
        resp = requests.get(f'{BASE_URL}/api/admin/prompt-templates', headers=admin_headers, timeout=10)
        result = resp.json()
        return result.get('success') and len(result.get('data', [])) > 0
    except:
        return False

run_test('添加Prompt模板', test_prompt_add)
run_test('获取Prompt模板列表', test_prompt_list)

# ==================== 实时监控测试 ====================
print_separator('实时监控')

def test_realtime_stats():
    try:
        resp = requests.get(f'{BASE_URL}/api/admin/monitor/realtime', headers=admin_headers, timeout=10)
        result = resp.json()
        return result.get('success') and 'today' in result.get('data', {})
    except:
        return False

run_test('获取实时监控数据', test_realtime_stats)

print('\n' + '='*60)
print(' 新功能测试完成！')
print('='*60)
print(f' 总计: {test_stats["total"]} 测试')
print(f' 通过: {test_stats["passed"]} ✅')
print(f' 失败: {test_stats["failed"]} ❌')
print(f' 通过率: {(test_stats["passed"]/test_stats["total"]*100):.1f}%')
print('='*60 + '\n')
