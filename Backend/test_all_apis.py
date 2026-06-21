import requests
import json
import os
import base64

BASE_URL = 'http://localhost:5000'

def print_separator(test_name):
    print('\n' + '='*60)
    print(f' 测试: {test_name}')
    print('='*60)

def test_result(success, message, response=None):
    status = '✅ PASS' if success else '❌ FAIL'
    print(f'{status}: {message}')
    if response is not None and not success:
        try:
            data = response.json() if hasattr(response, 'json') else response
            print(f'  响应: {json.dumps(data, ensure_ascii=False, indent=2)[:500]}')
        except:
            print(f'  原始响应: {str(response)[:500]}')

# 测试结果统计
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
print('# PetWise API 全面测试')
print('#'*60)

# ==================== 认证模块测试 ====================
print_separator('1. 认证模块')

# 1.1 注册测试
try:
    resp = requests.post(f'{BASE_URL}/api/auth/register', 
        json={'username': 'testuser_api', 'email': 'test_api@test.com', 'password': 'test123456'},
        timeout=10)
    result = resp.json()
    if result.get('success') or resp.status_code == 409:
        test_stats['total'] += 1
        test_stats['passed'] += 1
        test_result(True, f'注册接口 (status={resp.status_code})')
    else:
        test_stats['total'] += 1
        test_stats['failed'] += 1
        test_result(False, f'注册接口 (status={resp.status_code})', result)
except Exception as e:
    test_stats['total'] += 1
    test_stats['failed'] += 1
    test_result(False, f'注册接口异常: {e}')

# 1.2 登录测试
token = None
try:
    resp = requests.post(f'{BASE_URL}/api/auth/login',
        json={'username': 'testuser_api', 'password': 'test123456'},
        timeout=10)
    result = resp.json()
    if result.get('success') and result.get('token'):
        token = result['token']
        test_stats['total'] += 1
        test_stats['passed'] += 1
        test_result(True, f'登录接口 - 获取token成功')
    else:
        test_stats['total'] += 1
        test_stats['failed'] += 1
        test_result(False, f'登录接口 (status={resp.status_code})', result)
except Exception as e:
    test_stats['total'] += 1
    test_stats['failed'] += 1
    test_result(False, f'登录接口异常: {e}')

auth_headers = {'Authorization': f'Bearer {token}'} if token else {}

# 1.3 获取用户信息
try:
    resp = requests.get(f'{BASE_URL}/api/auth/profile', headers=auth_headers, timeout=10)
    result = resp.json()
    test_stats['total'] += 1
    if resp.status_code == 200:
        test_stats['passed'] += 1
        test_result(True, f'获取用户信息接口')
    else:
        test_stats['failed'] += 1
        test_result(False, f'获取用户信息接口 (status={resp.status_code})', result)
except Exception as e:
    test_stats['total'] += 1
    test_stats['failed'] += 1
    test_result(False, f'获取用户信息接口异常: {e}')

# ==================== 宠物识别模块测试 ====================
print_separator('2. 宠物识别模块')

# 2.1 获取品种列表
try:
    resp = requests.get(f'{BASE_URL}/api/breeds', timeout=10)
    result = resp.json()
    test_stats['total'] += 1
    if resp.status_code == 200 and isinstance(result.get('breeds'), list):
        test_stats['passed'] += 1
        test_result(True, f'获取品种列表 (数量: {len(result.get("breeds", []))})')
    else:
        test_stats['failed'] += 1
        test_result(False, f'获取品种列表 (status={resp.status_code})', result)
except Exception as e:
    test_stats['total'] += 1
    test_stats['failed'] += 1
    test_result(False, f'获取品种列表异常: {e}')

# 2.2 热门品种
try:
    resp = requests.get(f'{BASE_URL}/api/breeds/popular', timeout=10)
    result = resp.json()
    test_stats['total'] += 1
    if resp.status_code == 200:
        test_stats['passed'] += 1
        test_result(True, f'热门品种接口')
    else:
        test_stats['failed'] += 1
        test_result(False, f'热门品种接口 (status={resp.status_code})', result)
except Exception as e:
    test_stats['total'] += 1
    test_stats['failed'] += 1
    test_result(False, f'热门品种接口异常: {e}')

# 2.3 模型状态
try:
    resp = requests.get(f'{BASE_URL}/api/model/status', timeout=10)
    result = resp.json()
    test_stats['total'] += 1
    if resp.status_code == 200:
        test_stats['passed'] += 1
        test_result(True, f'模型状态接口 - 可用: {result.get("model_available", "N/A")}')
    else:
        test_stats['failed'] += 1
        test_result(False, f'模型状态接口 (status={resp.status_code})', result)
except Exception as e:
    test_stats['total'] += 1
    test_stats['failed'] += 1
    test_result(False, f'模型状态接口异常: {e}')

# 2.4 测试图片识别
test_image_path = r'e:\PetWise\model\image.png'
if os.path.exists(test_image_path):
    try:
        with open(test_image_path, 'rb') as f:
            files = {'image': ('test.png', f, 'image/png')}
            resp = requests.post(f'{BASE_URL}/api/recognize', files=files, headers=auth_headers, timeout=30)
            result = resp.json()
            test_stats['total'] += 1
            if result.get('success'):
                test_stats['passed'] += 1
                test_result(True, f'图片识别接口 - breed: {result.get("result", {}).get("breed", "N/A")}, confidence: {result.get("result", {}).get("confidence", 0):.2f}')
            else:
                test_stats['failed'] += 1
                test_result(False, f'图片识别接口', result)
    except Exception as e:
        test_stats['total'] += 1
        test_stats['failed'] += 1
        test_result(False, f'图片识别接口异常: {e}')
else:
    test_stats['total'] += 1
    test_stats['failed'] += 1
    test_result(False, f'测试图片不存在: {test_image_path}')

# 2.5 获取识别历史
try:
    resp = requests.get(f'{BASE_URL}/api/recognize/history', headers=auth_headers, timeout=10)
    result = resp.json()
    test_stats['total'] += 1
    if resp.status_code == 200:
        test_stats['passed'] += 1
        test_result(True, f'识别历史接口')
    else:
        test_stats['failed'] += 1
        test_result(False, f'识别历史接口 (status={resp.status_code})', result)
except Exception as e:
    test_stats['total'] += 1
    test_stats['failed'] += 1
    test_result(False, f'识别历史接口异常: {e}')

# 2.6 所有类别
try:
    resp = requests.get(f'{BASE_URL}/api/classes', timeout=10)
    result = resp.json()
    test_stats['total'] += 1
    if resp.status_code == 200:
        test_stats['passed'] += 1
        test_result(True, f'所有类别接口')
    else:
        test_stats['failed'] += 1
        test_result(False, f'所有类别接口 (status={resp.status_code})', result)
except Exception as e:
    test_stats['total'] += 1
    test_stats['failed'] += 1
    test_result(False, f'所有类别接口异常: {e}')

# ==================== AI智能体模块测试 ====================
print_separator('3. AI智能体模块')

# 3.1 简单对话测试
try:
    resp = requests.post(f'{BASE_URL}/api/agent/chat',
        json={'message': '你好，请简单介绍一下柴犬', 'session_id': 'test_session_001'},
        headers=auth_headers, timeout=60)
    result = resp.json()
    test_stats['total'] += 1
    if result.get('success'):
        test_stats['passed'] += 1
        test_result(True, f'AI对话接口 - 收到响应')
    else:
        test_stats['failed'] += 1
        test_result(False, f'AI对话接口', result)
except Exception as e:
    test_stats['total'] += 1
    test_stats['failed'] += 1
    test_result(False, f'AI对话接口异常: {e}')

# 3.2 获取历史对话
try:
    resp = requests.get(f'{BASE_URL}/api/agent/history?session_id=test_session_001', headers=auth_headers, timeout=10)
    result = resp.json()
    test_stats['total'] += 1
    if resp.status_code == 200:
        test_stats['passed'] += 1
        test_result(True, f'对话历史接口')
    else:
        test_stats['failed'] += 1
        test_result(False, f'对话历史接口 (status={resp.status_code})', result)
except Exception as e:
    test_stats['total'] += 1
    test_stats['failed'] += 1
    test_result(False, f'对话历史接口异常: {e}')

# 3.3 获取AI模型列表
try:
    resp = requests.get(f'{BASE_URL}/api/agent/models', headers=auth_headers, timeout=10)
    result = resp.json()
    test_stats['total'] += 1
    if resp.status_code == 200:
        test_stats['passed'] += 1
        test_result(True, f'AI模型列表接口')
    else:
        test_stats['failed'] += 1
        test_result(False, f'AI模型列表接口 (status={resp.status_code})', result)
except Exception as e:
    test_stats['total'] += 1
    test_stats['failed'] += 1
    test_result(False, f'AI模型列表接口异常: {e}')

# 3.4 获取AI健康状态
try:
    resp = requests.get(f'{BASE_URL}/api/agent/health', headers=auth_headers, timeout=10)
    result = resp.json()
    test_stats['total'] += 1
    if resp.status_code == 200:
        test_stats['passed'] += 1
        test_result(True, f'AI健康状态接口')
    else:
        test_stats['failed'] += 1
        test_result(False, f'AI健康状态接口 (status={resp.status_code})', result)
except Exception as e:
    test_stats['total'] += 1
    test_stats['failed'] += 1
    test_result(False, f'AI健康状态接口异常: {e}')

# ==================== 宠物档案模块测试 ====================
print_separator('4. 宠物档案模块')

pet_id = None

# 4.1 创建宠物档案
try:
    resp = requests.post(f'{BASE_URL}/api/pets',
        json={'name': '测试宠物', 'breed': '柴犬', 'category': 'dog', 'age': 2, 'gender': 'male'},
        headers=auth_headers, timeout=10)
    result = resp.json()
    test_stats['total'] += 1
    if result.get('success') and result.get('pet', {}).get('id'):
        pet_id = result['pet']['id']
        test_stats['passed'] += 1
        test_result(True, f'创建宠物档案 - ID: {pet_id}')
    else:
        test_stats['failed'] += 1
        test_result(False, f'创建宠物档案接口', result)
except Exception as e:
    test_stats['total'] += 1
    test_stats['failed'] += 1
    test_result(False, f'创建宠物档案接口异常: {e}')

# 4.2 获取宠物列表
try:
    resp = requests.get(f'{BASE_URL}/api/pets', headers=auth_headers, timeout=10)
    result = resp.json()
    test_stats['total'] += 1
    if resp.status_code == 200:
        test_stats['passed'] += 1
        test_result(True, f'获取宠物列表 (数量: {len(result.get("data", []))})')
    else:
        test_stats['failed'] += 1
        test_result(False, f'获取宠物列表 (status={resp.status_code})', result)
except Exception as e:
    test_stats['total'] += 1
    test_stats['failed'] += 1
    test_result(False, f'获取宠物列表异常: {e}')

# 4.3 更新宠物档案
if pet_id:
    try:
        resp = requests.put(f'{BASE_URL}/api/pets/{pet_id}',
            json={'name': '测试宠物-更新', 'bio': '这是一只测试用的可爱宠物'},
            headers=auth_headers, timeout=10)
        result = resp.json()
        test_stats['total'] += 1
        if result.get('success'):
            test_stats['passed'] += 1
            test_result(True, f'更新宠物档案接口')
        else:
            test_stats['failed'] += 1
            test_result(False, f'更新宠物档案接口', result)
    except Exception as e:
        test_stats['total'] += 1
        test_stats['failed'] += 1
        test_result(False, f'更新宠物档案异常: {e}')

# 4.4 获取单个宠物详情
if pet_id:
    try:
        resp = requests.get(f'{BASE_URL}/api/pets/{pet_id}', headers=auth_headers, timeout=10)
        result = resp.json()
        test_stats['total'] += 1
        if resp.status_code == 200:
            test_stats['passed'] += 1
            test_result(True, f'获取宠物详情接口')
        else:
            test_stats['failed'] += 1
            test_result(False, f'获取宠物详情接口 (status={resp.status_code})', result)
    except Exception as e:
        test_stats['total'] += 1
        test_stats['failed'] += 1
        test_result(False, f'获取宠物详情异常: {e}')

# ==================== 健康记录模块测试 ====================
print_separator('5. 健康记录模块')

# 5.1 添加健康记录
if pet_id:
    try:
        resp = requests.post(f'{BASE_URL}/api/pets/{pet_id}/health',
            json={'record_type': 'weight', 'weight': 8.5, 'notes': '体重正常'},
            headers=auth_headers, timeout=10)
        result = resp.json()
        test_stats['total'] += 1
        if result.get('success'):
            test_stats['passed'] += 1
            test_result(True, f'添加健康记录接口')
        else:
            test_stats['failed'] += 1
            test_result(False, f'添加健康记录接口', result)
    except Exception as e:
        test_stats['total'] += 1
        test_stats['failed'] += 1
        test_result(False, f'添加健康记录异常: {e}')

# 5.2 获取健康记录
if pet_id:
    try:
        resp = requests.get(f'{BASE_URL}/api/pets/{pet_id}/health', headers=auth_headers, timeout=10)
        result = resp.json()
        test_stats['total'] += 1
        if resp.status_code == 200:
            test_stats['passed'] += 1
            test_result(True, f'获取健康记录接口')
        else:
            test_stats['failed'] += 1
            test_result(False, f'获取健康记录接口 (status={resp.status_code})', result)
    except Exception as e:
        test_stats['total'] += 1
        test_stats['failed'] += 1
        test_result(False, f'获取健康记录异常: {e}')

# 5.3 获取健康趋势
if pet_id:
    try:
        resp = requests.get(f'{BASE_URL}/api/pets/{pet_id}/health/trends', headers=auth_headers, timeout=10)
        result = resp.json()
        test_stats['total'] += 1
        if resp.status_code == 200:
            test_stats['passed'] += 1
            test_result(True, f'获取健康趋势接口')
        else:
            test_stats['failed'] += 1
            test_result(False, f'获取健康趋势接口 (status={resp.status_code})', result)
    except Exception as e:
        test_stats['total'] += 1
        test_stats['failed'] += 1
        test_result(False, f'获取健康趋势异常: {e}')

# ==================== 日程提醒模块测试 ====================
print_separator('6. 日程提醒模块')

# 6.1 添加日程提醒
if pet_id:
    try:
        resp = requests.post(f'{BASE_URL}/api/pets/{pet_id}/schedule',
            json={'reminder_type': 'vaccination', 'title': '疫苗接种', 'scheduled_date': '2026-06-15'},
            headers=auth_headers, timeout=10)
        result = resp.json()
        test_stats['total'] += 1
        if result.get('success'):
            test_stats['passed'] += 1
            test_result(True, f'添加日程提醒接口')
        else:
            test_stats['failed'] += 1
            test_result(False, f'添加日程提醒接口', result)
    except Exception as e:
        test_stats['total'] += 1
        test_stats['failed'] += 1
        test_result(False, f'添加日程提醒异常: {e}')

# 6.2 获取日程列表
if pet_id:
    try:
        resp = requests.get(f'{BASE_URL}/api/pets/{pet_id}/schedule', headers=auth_headers, timeout=10)
        result = resp.json()
        test_stats['total'] += 1
        if resp.status_code == 200:
            test_stats['passed'] += 1
            test_result(True, f'获取日程列表接口')
        else:
            test_stats['failed'] += 1
            test_result(False, f'获取日程列表接口 (status={resp.status_code})', result)
    except Exception as e:
        test_stats['total'] += 1
        test_stats['failed'] += 1
        test_result(False, f'获取日程列表异常: {e}')

# 6.3 获取即将到来的提醒
try:
    resp = requests.get(f'{BASE_URL}/api/schedule/upcoming', headers=auth_headers, timeout=10)
    result = resp.json()
    test_stats['total'] += 1
    if resp.status_code == 200:
        test_stats['passed'] += 1
        test_result(True, f'即将到来的提醒接口')
    else:
        test_stats['failed'] += 1
        test_result(False, f'即将到来的提醒接口 (status={resp.status_code})', result)
except Exception as e:
    test_stats['total'] += 1
    test_stats['failed'] += 1
    test_result(False, f'即将到来的提醒异常: {e}')

# ==================== 收藏评论模块测试 ====================
print_separator('7. 收藏评论模块')

# 7.1 添加收藏
try:
    resp = requests.post(f'{BASE_URL}/api/favorites',
        json={'breed': '柴犬'},
        headers=auth_headers, timeout=10)
    result = resp.json()
    test_stats['total'] += 1
    if result.get('success') or resp.status_code == 409:
        test_stats['passed'] += 1
        test_result(True, f'添加收藏接口')
    else:
        test_stats['failed'] += 1
        test_result(False, f'添加收藏接口', result)
except Exception as e:
    test_stats['total'] += 1
    test_stats['failed'] += 1
    test_result(False, f'添加收藏异常: {e}')

# 7.2 获取收藏列表
try:
    resp = requests.get(f'{BASE_URL}/api/favorites', headers=auth_headers, timeout=10)
    result = resp.json()
    test_stats['total'] += 1
    if resp.status_code == 200:
        test_stats['passed'] += 1
        test_result(True, f'获取收藏列表接口')
    else:
        test_stats['failed'] += 1
        test_result(False, f'获取收藏列表接口 (status={resp.status_code})', result)
except Exception as e:
    test_stats['total'] += 1
    test_stats['failed'] += 1
    test_result(False, f'获取收藏列表异常: {e}')

# 7.3 添加评论
try:
    resp = requests.post(f'{BASE_URL}/api/comments',
        json={'breed': '柴犬', 'content': '这是一只非常聪明可爱的狗狗！', 'rating': 5},
        headers=auth_headers, timeout=10)
    result = resp.json()
    test_stats['total'] += 1
    if result.get('success'):
        test_stats['passed'] += 1
        test_result(True, f'添加评论接口')
    else:
        test_stats['failed'] += 1
        test_result(False, f'添加评论接口', result)
except Exception as e:
    test_stats['total'] += 1
    test_stats['failed'] += 1
    test_result(False, f'添加评论异常: {e}')

# 7.4 获取评论列表
try:
    resp = requests.get(f'{BASE_URL}/api/comments/柴犬', timeout=10)
    result = resp.json()
    test_stats['total'] += 1
    if resp.status_code == 200:
        test_stats['passed'] += 1
        test_result(True, f'获取评论列表接口')
    else:
        test_stats['failed'] += 1
        test_result(False, f'获取评论列表接口 (status={resp.status_code})', result)
except Exception as e:
    test_stats['total'] += 1
    test_stats['failed'] += 1
    test_result(False, f'获取评论列表异常: {e}')

# ==================== 品种百科模块测试 ====================
print_separator('8. 品种百科模块')

# 8.1 获取品种详情
try:
    resp = requests.get(f'{BASE_URL}/api/breed/柴犬', timeout=10)
    result = resp.json()
    test_stats['total'] += 1
    if result.get('success'):
        test_stats['passed'] += 1
        test_result(True, f'获取品种详情接口 (柴犬)')
    else:
        test_stats['failed'] += 1
        test_result(False, f'获取品种详情接口 (status={resp.status_code})', result)
except Exception as e:
    test_stats['total'] += 1
    test_stats['failed'] += 1
    test_result(False, f'获取品种详情异常: {e}')

# ==================== 系统其他接口测试 ====================
print_separator('9. 系统其他接口')

# 9.1 系统健康检查
try:
    resp = requests.get(f'{BASE_URL}/api/health_check', timeout=10)
    result = resp.json()
    test_stats['total'] += 1
    if resp.status_code == 200:
        test_stats['passed'] += 1
        test_result(True, f'系统健康检查接口')
    else:
        test_stats['failed'] += 1
        test_result(False, f'系统健康检查接口 (status={resp.status_code})', result)
except Exception as e:
    test_stats['total'] += 1
    test_stats['failed'] += 1
    test_result(False, f'系统健康检查异常: {e}')

# 9.2 提交反馈
try:
    resp = requests.post(f'{BASE_URL}/api/feedback',
        json={'type': 'suggestion', 'content': '建议增加更多宠物品种'},
        headers=auth_headers, timeout=10)
    result = resp.json()
    test_stats['total'] += 1
    if result.get('success'):
        test_stats['passed'] += 1
        test_result(True, f'提交反馈接口')
    else:
        test_stats['failed'] += 1
        test_result(False, f'提交反馈接口', result)
except Exception as e:
    test_stats['total'] += 1
    test_stats['failed'] += 1
    test_result(False, f'提交反馈异常: {e}')

# ==================== 管理后台测试 ====================
print_separator('10. 管理后台接口')

# 先用管理员账号登录测试
admin_token = None
try:
    resp = requests.post(f'{BASE_URL}/api/auth/login',
        json={'username': 'admin', 'password': 'admin123'},
        timeout=10)
    result = resp.json()
    if result.get('success') and result.get('token'):
        admin_token = result['token']
        test_stats['total'] += 1
        test_stats['passed'] += 1
        test_result(True, '管理员登录成功')
    else:
        test_stats['total'] += 1
        test_stats['failed'] += 1
        test_result(False, '管理员登录失败', result)
except Exception as e:
    test_stats['total'] += 1
    test_stats['failed'] += 1
    test_result(False, f'管理员登录异常: {e}')

admin_headers = {'Authorization': f'Bearer {admin_token}'} if admin_token else {}

# 10.1 获取用户列表 (管理员)
if admin_token:
    try:
        resp = requests.get(f'{BASE_URL}/api/admin/users', headers=admin_headers, timeout=10)
        result = resp.json()
        test_stats['total'] += 1
        if result.get('success'):
            test_stats['passed'] += 1
            test_result(True, f'获取用户列表 (管理员)')
        else:
            test_stats['failed'] += 1
            test_result(False, f'获取用户列表 (管理员)', result)
    except Exception as e:
        test_stats['total'] += 1
        test_stats['failed'] += 1
        test_result(False, f'获取用户列表异常: {e}')

# 10.2 获取系统统计 (管理员)
if admin_token:
    try:
        resp = requests.get(f'{BASE_URL}/api/admin/stats', headers=admin_headers, timeout=10)
        result = resp.json()
        test_stats['total'] += 1
        if result.get('success'):
            test_stats['passed'] += 1
            test_result(True, f'系统统计接口')
        else:
            test_stats['failed'] += 1
            test_result(False, f'系统统计接口', result)
    except Exception as e:
        test_stats['total'] += 1
        test_stats['failed'] += 1
        test_result(False, f'系统统计接口异常: {e}')

# 10.3 大模型管理 (管理员)
if admin_token:
    try:
        resp = requests.get(f'{BASE_URL}/api/admin/models', headers=admin_headers, timeout=10)
        result = resp.json()
        test_stats['total'] += 1
        if resp.status_code == 200:
            test_stats['passed'] += 1
            test_result(True, f'大模型列表接口')
        else:
            test_stats['failed'] += 1
            test_result(False, f'大模型列表接口', result)
    except Exception as e:
        test_stats['total'] += 1
        test_stats['failed'] += 1
        test_result(False, f'大模型列表接口异常: {e}')

# 10.4 知识库管理 (管理员)
if admin_token:
    try:
        resp = requests.get(f'{BASE_URL}/api/admin/knowledge', headers=admin_headers, timeout=10)
        result = resp.json()
        test_stats['total'] += 1
        if resp.status_code == 200:
            test_stats['passed'] += 1
            test_result(True, f'知识库列表接口')
        else:
            test_stats['failed'] += 1
            test_result(False, f'知识库列表接口', result)
    except Exception as e:
        test_stats['total'] += 1
        test_stats['failed'] += 1
        test_result(False, f'知识库列表接口异常: {e}')

# 10.5 公告接口 (管理员)
if admin_token:
    try:
        resp = requests.get(f'{BASE_URL}/api/admin/announcements', headers=admin_headers, timeout=10)
        result = resp.json()
        test_stats['total'] += 1
        if resp.status_code == 200:
            test_stats['passed'] += 1
            test_result(True, f'系统公告接口')
        else:
            test_stats['failed'] += 1
            test_result(False, f'系统公告接口', result)
    except Exception as e:
        test_stats['total'] += 1
        test_stats['failed'] += 1
        test_result(False, f'系统公告接口异常: {e}')

# 10.6 系统日志 (管理员)
if admin_token:
    try:
        resp = requests.get(f'{BASE_URL}/api/admin/logs', headers=admin_headers, timeout=10)
        result = resp.json()
        test_stats['total'] += 1
        if resp.status_code == 200:
            test_stats['passed'] += 1
            test_result(True, f'系统日志接口')
        else:
            test_stats['failed'] += 1
            test_result(False, f'系统日志接口', result)
    except Exception as e:
        test_stats['total'] += 1
        test_stats['failed'] += 1
        test_result(False, f'系统日志接口异常: {e}')

# 10.7 反馈管理 (管理员)
if admin_token:
    try:
        resp = requests.get(f'{BASE_URL}/api/admin/feedback', headers=admin_headers, timeout=10)
        result = resp.json()
        test_stats['total'] += 1
        if resp.status_code == 200:
            test_stats['passed'] += 1
            test_result(True, f'反馈管理接口')
        else:
            test_stats['failed'] += 1
            test_result(False, f'反馈管理接口', result)
    except Exception as e:
        test_stats['total'] += 1
        test_stats['failed'] += 1
        test_result(False, f'反馈管理接口异常: {e}')

# 10.8 难样本管理 (管理员)
if admin_token:
    try:
        resp = requests.get(f'{BASE_URL}/api/admin/samples/hard', headers=admin_headers, timeout=10)
        result = resp.json()
        test_stats['total'] += 1
        if resp.status_code == 200:
            test_stats['passed'] += 1
            test_result(True, f'难样本管理接口')
        else:
            test_stats['failed'] += 1
            test_result(False, f'难样本管理接口', result)
    except Exception as e:
        test_stats['total'] += 1
        test_stats['failed'] += 1
        test_result(False, f'难样本管理接口异常: {e}')

print('\n' + '='*60)
print(' API测试完成！')
print('='*60)
print(f' 总计: {test_stats["total"]} 测试')
print(f' 通过: {test_stats["passed"]} ✅')
print(f' 失败: {test_stats["failed"]} ❌')
print(f' 通过率: {(test_stats["passed"]/test_stats["total"]*100):.1f}%')
print('='*60 + '\n')
