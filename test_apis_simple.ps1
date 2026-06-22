# PetWise API 全功能测试（简化版）

Write-Host "========================================"
Write-Host "PetWise API 全功能测试"
Write-Host "========================================"
Write-Host ""

# 获取管理员token
Write-Host "[1] Testing login..."
try {
    $loginResp = Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/auth/login" -Method POST -Body '{"username":"admin","password":"admin123"}' -ContentType "application/json" -UseBasicParsing
    $loginData = $loginResp.Content | ConvertFrom-Json
    
    if ($loginData.success) {
        Write-Host "SUCCESS: Login OK"
        $adminToken = $loginData.token
    } else {
        Write-Host "FAIL: Login failed"
        exit 1
    }
} catch {
    Write-Host "FAIL: Login - $($_.Exception.Message)"
    exit 1
}

# 设置token header
$headers = @{
    "Authorization" = "Bearer $adminToken"
}

Write-Host ""
Write-Host "========================================"
Write-Host "Admin API Tests"
Write-Host "========================================"
Write-Host ""

# 测试统计数据
Write-Host "[2] Testing /admin/stats..."
try {
    $resp = Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/admin/stats" -Headers $headers -UseBasicParsing
    $data = $resp.Content | ConvertFrom-Json
    if ($data.success) { Write-Host "OK: Stats API" } else { Write-Host "FAIL: Stats API" }
} catch { Write-Host "FAIL: Stats - $($_.Exception.Message)" }

# 测试用户列表
Write-Host "[3] Testing /admin/users..."
try {
    $resp = Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/admin/users" -Headers $headers -UseBasicParsing
    $data = $resp.Content | ConvertFrom-Json
    if ($data.success) { Write-Host "OK: Users API" } else { Write-Host "FAIL: Users API" }
} catch { Write-Host "FAIL: Users - $($_.Exception.Message)" }

# 测试公告列表
Write-Host "[4] Testing /admin/announcements..."
try {
    $resp = Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/admin/announcements" -Headers $headers -UseBasicParsing
    $data = $resp.Content | ConvertFrom-Json
    if ($data.success) { Write-Host "OK: Announcements API" } else { Write-Host "FAIL: Announcements API" }
} catch { Write-Host "FAIL: Announcements - $($_.Exception.Message)" }

# 测试反馈列表
Write-Host "[5] Testing /admin/feedback..."
try {
    $resp = Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/admin/feedback" -Headers $headers -UseBasicParsing
    $data = $resp.Content | ConvertFrom-Json
    if ($data.success) { Write-Host "OK: Feedback API" } else { Write-Host "FAIL: Feedback API" }
} catch { Write-Host "FAIL: Feedback - $($_.Exception.Message)" }

# 测试纠错列表
Write-Host "[6] Testing /admin/corrections..."
try {
    $resp = Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/admin/corrections" -Headers $headers -UseBasicParsing
    $data = $resp.Content | ConvertFrom-Json
    if ($data.success) { Write-Host "OK: Corrections API" } else { Write-Host "FAIL: Corrections API" }
} catch { Write-Host "FAIL: Corrections - $($_.Exception.Message)" }

# 测试知识库
Write-Host "[7] Testing /admin/knowledge..."
try {
    $resp = Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/admin/knowledge" -Headers $headers -UseBasicParsing
    $data = $resp.Content | ConvertFrom-Json
    if ($data.success) { Write-Host "OK: Knowledge API" } else { Write-Host "FAIL: Knowledge API" }
} catch { Write-Host "FAIL: Knowledge - $($_.Exception.Message)" }

# 测试难样本列表
Write-Host "[8] Testing /admin/samples/hard..."
try {
    $resp = Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/admin/samples/hard" -Headers $headers -UseBasicParsing
    $data = $resp.Content | ConvertFrom-Json
    if ($data.success) { Write-Host "OK: Hard Samples API" } else { Write-Host "FAIL: Hard Samples API" }
} catch { Write-Host "FAIL: Hard Samples - $($_.Exception.Message)" }

# 测试限流配置
Write-Host "[9] Testing /admin/rate-limits..."
try {
    $resp = Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/admin/rate-limits" -Headers $headers -UseBasicParsing
    $data = $resp.Content | ConvertFrom-Json
    if ($data.success) { Write-Host "OK: Rate Limits API" } else { Write-Host "FAIL: Rate Limits API" }
} catch { Write-Host "FAIL: Rate Limits - $($_.Exception.Message)" }

# 测试敏感词
Write-Host "[10] Testing /admin/sensitive-words..."
try {
    $resp = Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/admin/sensitive-words" -Headers $headers -UseBasicParsing
    $data = $resp.Content | ConvertFrom-Json
    if ($data.success) { Write-Host "OK: Sensitive Words API" } else { Write-Host "FAIL: Sensitive Words API" }
} catch { Write-Host "FAIL: Sensitive Words - $($_.Exception.Message)" }

# 测试Prompt模板
Write-Host "[11] Testing /admin/prompt-templates..."
try {
    $resp = Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/admin/prompt-templates" -Headers $headers -UseBasicParsing
    $data = $resp.Content | ConvertFrom-Json
    if ($data.success) { Write-Host "OK: Prompt Templates API" } else { Write-Host "FAIL: Prompt Templates API" }
} catch { Write-Host "FAIL: Prompt Templates - $($_.Exception.Message)" }

# 测试日志
Write-Host "[12] Testing /admin/logs..."
try {
    $resp = Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/admin/logs" -Headers $headers -UseBasicParsing
    $data = $resp.Content | ConvertFrom-Json
    if ($data.success) { Write-Host "OK: Logs API" } else { Write-Host "FAIL: Logs API" }
} catch { Write-Host "FAIL: Logs - $($_.Exception.Message)" }

# 测试实时监控
Write-Host "[13] Testing /admin/monitor/realtime..."
try {
    $resp = Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/admin/monitor/realtime" -Headers $headers -UseBasicParsing
    $data = $resp.Content | ConvertFrom-Json
    if ($data.success) { Write-Host "OK: Realtime Monitor API" } else { Write-Host "FAIL: Realtime Monitor API" }
} catch { Write-Host "FAIL: Realtime Monitor - $($_.Exception.Message)" }

# 测试品种信息
Write-Host "[14] Testing /admin/breeds..."
try {
    $resp = Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/admin/breeds" -Headers $headers -UseBasicParsing
    $data = $resp.Content | ConvertFrom-Json
    if ($data.success) { Write-Host "OK: Breeds API" } else { Write-Host "FAIL: Breeds API" }
} catch { Write-Host "FAIL: Breeds - $($_.Exception.Message)" }

# 测试限流日志
Write-Host "[15] Testing /admin/rate-limits/logs..."
try {
    $resp = Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/admin/rate-limits/logs" -Headers $headers -UseBasicParsing
    $data = $resp.Content | ConvertFrom-Json
    if ($data.success) { Write-Host "OK: Rate Limits Logs API" } else { Write-Host "FAIL: Rate Limits Logs API" }
} catch { Write-Host "FAIL: Rate Limits Logs - $($_.Exception.Message)" }

# 测试Prompt列表
Write-Host "[16] Testing /admin/prompts..."
try {
    $resp = Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/admin/prompts" -Headers $headers -UseBasicParsing
    $data = $resp.Content | ConvertFrom-Json
    if ($data.success) { Write-Host "OK: Prompts API" } else { Write-Host "FAIL: Prompts API" }
} catch { Write-Host "FAIL: Prompts - $($_.Exception.Message)" }

Write-Host ""
Write-Host "========================================"
Write-Host "User API Tests"
Write-Host "========================================"
Write-Host ""

# 测试公告列表（用户端）
Write-Host "[17] Testing /api/announcements (user)..."
try {
    $resp = Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/announcements" -UseBasicParsing
    $data = $resp.Content | ConvertFrom-Json
    if ($data.success) { Write-Host "OK: User Announcements API" } else { Write-Host "FAIL: User Announcements API" }
} catch { Write-Host "FAIL: User Announcements - $($_.Exception.Message)" }

# 测试识别历史
Write-Host "[18] Testing /api/recognize/history..."
try {
    $resp = Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/recognize/history" -Headers $headers -UseBasicParsing
    $data = $resp.Content | ConvertFrom-Json
    if ($data.success) { Write-Host "OK: Recognition History API" } else { Write-Host "FAIL: Recognition History API" }
} catch { Write-Host "FAIL: Recognition History - $($_.Exception.Message)" }

# 测试我的反馈
Write-Host "[19] Testing /api/feedback/my..."
try {
    $resp = Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/feedback/my" -Headers $headers -UseBasicParsing
    $data = $resp.Content | ConvertFrom-Json
    if ($data.success) { Write-Host "OK: My Feedback API" } else { Write-Host "FAIL: My Feedback API" }
} catch { Write-Host "FAIL: My Feedback - $($_.Exception.Message)" }

# 测试收藏
Write-Host "[20] Testing /api/favorites..."
try {
    $resp = Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/favorites" -Headers $headers -UseBasicParsing
    $data = $resp.Content | ConvertFrom-Json
    if ($data.success) { Write-Host "OK: Favorites API" } else { Write-Host "FAIL: Favorites API" }
} catch { Write-Host "FAIL: Favorites - $($_.Exception.Message)" }

Write-Host ""
Write-Host "========================================"
Write-Host "Testing Complete!"
Write-Host "========================================"
