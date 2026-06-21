@echo off
chcp 65001 > nul
echo ========================================
echo PetWise API 全功能测试
echo ========================================
echo.

:: 获取管理员token
echo [1/20] 测试登录...
for /f "tokens=*" %%i in ('curl -s -X POST http://127.0.0.1:5000/api/auth/login -H "Content-Type: application/json" -d "{\"username\":\"admin\",\"password\":\"admin123\"}"') do set LOGIN_RESP=%%i
echo %LOGIN_RESP% | findstr /i "success" > nul
if %ERRORLEVEL%==0 (
    echo ✓ 登录成功
    for /f "tokens=2 delims=:" %%i in ('echo %LOGIN_RESP% ^| findstr /i "token"') do set ADMIN_TOKEN=%%i
    set ADMIN_TOKEN=%ADMIN_TOKEN:,=%
    set ADMIN_TOKEN=%ADMIN_TOKEN:"=%
    set ADMIN_TOKEN=%ADMIN_TOKEN: =%
) else (
    echo ✗ 登录失败
    set ADMIN_TOKEN=""
)

if "%ADMIN_TOKEN%"=="" (
    echo 无法获取token，测试终止
    exit /b 1
)

echo.
echo ========================================
echo 管理员端API测试
echo ========================================
echo.

:: 设置token
set AUTH_HDR=-H "Authorization: Bearer %ADMIN_TOKEN%"

:: 测试统计数据
echo [2/20] 测试统计数据 API...
curl -s -X GET http://127.0.0.1:5000/api/admin/stats %AUTH_HDR% | findstr /i "success" > nul
if %ERRORLEVEL%==0 (echo ✓ 统计数据 API 正常) else (echo ✗ 统计数据 API 失败)

:: 测试用户列表
echo [3/20] 测试用户列表 API...
curl -s -X GET "http://127.0.0.1:5000/api/admin/users?page=1&per_page=10" %AUTH_HDR% | findstr /i "success" > nul
if %ERRORLEVEL%==0 (echo ✓ 用户列表 API 正常) else (echo ✗ 用户列表 API 失败)

:: 测试公告列表
echo [4/20] 测试公告列表 API...
curl -s -X GET http://127.0.0.1:5000/api/admin/announcements %AUTH_HDR% | findstr /i "success" > nul
if %ERRORLEVEL%==0 (echo ✓ 公告列表 API 正常) else (echo ✗ 公告列表 API 失败)

:: 测试反馈列表
echo [5/20] 测试反馈列表 API...
curl -s -X GET http://127.0.0.1:5000/api/admin/feedback %AUTH_HDR% | findstr /i "success" > nul
if %ERRORLEVEL%==0 (echo ✓ 反馈列表 API 正常) else (echo ✗ 反馈列表 API 失败)

:: 测试纠错列表
echo [6/20] 测试纠错列表 API...
curl -s -X GET http://127.0.0.1:5000/api/admin/corrections %AUTH_HDR% | findstr /i "success" > nul
if %ERRORLEVEL%==0 (echo ✓ 纠错列表 API 正常) else (echo ✗ 纠错列表 API 失败)

:: 测试知识库
echo [7/20] 测试知识库 API...
curl -s -X GET http://127.0.0.1:5000/api/admin/knowledge %AUTH_HDR% | findstr /i "success" > nul
if %ERRORLEVEL%==0 (echo ✓ 知识库 API 正常) else (echo ✗ 知识库 API 失败)

:: 测试难样本列表
echo [8/20] 测试难样本列表 API...
curl -s -X GET http://127.0.0.1:5000/api/admin/samples/hard %AUTH_HDR% | findstr /i "success" > nul
if %ERRORLEVEL%==0 (echo ✓ 难样本列表 API 正常) else (echo ✗ 难样本列表 API 失败)

:: 测试限流配置
echo [9/20] 测试限流配置 API...
curl -s -X GET http://127.0.0.1:5000/api/admin/rate-limits %AUTH_HDR% | findstr /i "success" > nul
if %ERRORLEVEL%==0 (echo ✓ 限流配置 API 正常) else (echo ✗ 限流配置 API 失败)

:: 测试敏感词
echo [10/20] 测试敏感词 API...
curl -s -X GET http://127.0.0.1:5000/api/admin/sensitive-words %AUTH_HDR% | findstr /i "success" > nul
if %ERRORLEVEL%==0 (echo ✓ 敏感词 API 正常) else (echo ✗ 敏感词 API 失败)

:: 测试Prompt模板
echo [11/20] 测试Prompt模板 API...
curl -s -X GET http://127.0.0.1:5000/api/admin/prompt-templates %AUTH_HDR% | findstr /i "success" > nul
if %ERRORLEVEL%==0 (echo ✓ Prompt模板 API 正常) else (echo ✗ Prompt模板 API 失败)

:: 测试日志
echo [12/20] 测试系统日志 API...
curl -s -X GET "http://127.0.0.1:5000/api/admin/logs?page=1&per_page=10" %AUTH_HDR% | findstr /i "success" > nul
if %ERRORLEVEL%==0 (echo ✓ 系统日志 API 正常) else (echo ✗ 系统日志 API 失败)

:: 测试实时监控
echo [13/20] 测试实时监控 API...
curl -s -X GET http://127.0.0.1:5000/api/admin/monitor/realtime %AUTH_HDR% | findstr /i "success" > nul
if %ERRORLEVEL%==0 (echo ✓ 实时监控 API 正常) else (echo ✗ 实时监控 API 失败)

:: 测试品种信息
echo [14/20] 测试品种信息 API...
curl -s -X GET http://127.0.0.1:5000/api/admin/breeds %AUTH_HDR% | findstr /i "success" > nul
if %ERRORLEVEL%==0 (echo ✓ 品种信息 API 正常) else (echo ✗ 品种信息 API 失败)

:: 测试限流日志
echo [15/20] 测试限流日志 API...
curl -s -X GET "http://127.0.0.1:5000/api/admin/rate-limits/logs?user_id=&endpoint=" %AUTH_HDR% | findstr /i "success" > nul
if %ERRORLEVEL%==0 (echo ✓ 限流日志 API 正常) else (echo ✗ 限流日志 API 失败)

:: 测试Prompt列表
echo [16/20] 测试Prompt列表 API...
curl -s -X GET "http://127.0.0.1:5000/api/admin/prompts?prompt_type=&search=" %AUTH_HDR% | findstr /i "success" > nul
if %ERRORLEVEL%==0 (echo ✓ Prompt列表 API 正常) else (echo ✗ Prompt列表 API 失败)

echo.
echo ========================================
echo 用户端API测试
echo ========================================
echo.

:: 测试公告列表（用户端）
echo [17/20] 测试用户端公告 API...
curl -s -X GET http://127.0.0.1:5000/api/announcements | findstr /i "success" > nul
if %ERRORLEVEL%==0 (echo ✓ 用户端公告 API 正常) else (echo ✗ 用户端公告 API 失败)

:: 测试识别历史
echo [18/20] 测试识别历史 API...
curl -s -X GET http://127.0.0.1:5000/api/recognize/history %AUTH_HDR% | findstr /i "success" > nul
if %ERRORLEVEL%==0 (echo ✓ 识别历史 API 正常) else (echo ✗ 识别历史 API 失败)

:: 测试我的反馈
echo [19/20] 测试我的反馈 API...
curl -s -X GET http://127.0.0.1:5000/api/feedback/my %AUTH_HDR% | findstr /i "success" > nul
if %ERRORLEVEL%==0 (echo ✓ 我的反馈 API 正常) else (echo ✗ 我的反馈 API 失败)

:: 测试收藏
echo [20/20] 测试收藏列表 API...
curl -s -X GET http://127.0.0.1:5000/api/favorites %AUTH_HDR% | findstr /i "success" > nul
if %ERRORLEVEL%==0 (echo ✓ 收藏列表 API 正常) else (echo ✗ 收藏列表 API 失败)

echo.
echo ========================================
echo 测试完成！
echo ========================================
