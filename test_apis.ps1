# PetWise API 全功能测试

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PetWise API 全功能测试" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 获取管理员token
Write-Host "[1/20] 测试登录..." -ForegroundColor Yellow
$loginResp = Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/auth/login" -Method POST -Body '{"username":"admin","password":"admin123"}' -ContentType "application/json" -UseBasicParsing
$loginData = $loginResp.Content | ConvertFrom-Json

if ($loginData.success) {
    Write-Host "✓ 登录成功" -ForegroundColor Green
    $adminToken = $loginData.token
} else {
    Write-Host "✗ 登录失败" -ForegroundColor Red
    exit 1
}

# 设置token header
$headers = @{
    "Authorization" = "Bearer $adminToken"
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "管理员端API测试" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 测试统计数据
Write-Host "[2/20] 测试统计数据 API..." -ForegroundColor Yellow
try {
    $resp = Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/admin/stats" -Headers $headers -UseBasicParsing
    $data = $resp.Content | ConvertFrom-Json
    if ($data.success) {
        Write-Host "✓ 统计数据 API 正常 (total_users: $($data.total_users))" -ForegroundColor Green
    } else {
        Write-Host "✗ 统计数据 API 返回失败" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ 统计数据 API 失败: $($_.Exception.Message)" -ForegroundColor Red
}

# 测试用户列表
Write-Host "[3/20] 测试用户列表 API..." -ForegroundColor Yellow
try {
    $resp = Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/admin/users?page=1%26per_page=10" -Headers $headers -UseBasicParsing
    $data = $resp.Content | ConvertFrom-Json
    if ($data.success) {
        Write-Host "✓ 用户列表 API 正常 (count: $($data.data.Count))" -ForegroundColor Green
    } else {
        Write-Host "✗ 用户列表 API 返回失败" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ 用户列表 API 失败: $($_.Exception.Message)" -ForegroundColor Red
}

# 测试公告列表
Write-Host "[4/20] 测试公告列表 API..." -ForegroundColor Yellow
try {
    $resp = Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/admin/announcements" -Headers $headers -UseBasicParsing
    $data = $resp.Content | ConvertFrom-Json
    if ($data.success) {
        Write-Host "✓ 公告列表 API 正常" -ForegroundColor Green
    } else {
        Write-Host "✗ 公告列表 API 返回失败" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ 公告列表 API 失败: $($_.Exception.Message)" -ForegroundColor Red
}

# 测试反馈列表
Write-Host "[5/20] 测试反馈列表 API..." -ForegroundColor Yellow
try {
    $resp = Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/admin/feedback" -Headers $headers -UseBasicParsing
    $data = $resp.Content | ConvertFrom-Json
    if ($data.success) {
        Write-Host "✓ 反馈列表 API 正常" -ForegroundColor Green
    } else {
        Write-Host "✗ 反馈列表 API 返回失败" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ 反馈列表 API 失败: $($_.Exception.Message)" -ForegroundColor Red
}

# 测试纠错列表
Write-Host "[6/20] 测试纠错列表 API..." -ForegroundColor Yellow
try {
    $resp = Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/admin/corrections" -Headers $headers -UseBasicParsing
    $data = $resp.Content | ConvertFrom-Json
    if ($data.success) {
        Write-Host "✓ 纠错列表 API 正常" -ForegroundColor Green
    } else {
        Write-Host "✗ 纠错列表 API 返回失败" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ 纠错列表 API 失败: $($_.Exception.Message)" -ForegroundColor Red
}

# 测试知识库
Write-Host "[7/20] 测试知识库 API..." -ForegroundColor Yellow
try {
    $resp = Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/admin/knowledge" -Headers $headers -UseBasicParsing
    $data = $resp.Content | ConvertFrom-Json
    if ($data.success) {
        Write-Host "✓ 知识库 API 正常" -ForegroundColor Green
    } else {
        Write-Host "✗ 知识库 API 返回失败" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ 知识库 API 失败: $($_.Exception.Message)" -ForegroundColor Red
}

# 测试难样本列表
Write-Host "[8/20] 测试难样本列表 API..." -ForegroundColor Yellow
try {
    $resp = Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/admin/samples/hard" -Headers $headers -UseBasicParsing
    $data = $resp.Content | ConvertFrom-Json
    if ($data.success) {
        Write-Host "✓ 难样本列表 API 正常" -ForegroundColor Green
    } else {
        Write-Host "✗ 难样本列表 API 返回失败" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ 难样本列表 API 失败: $($_.Exception.Message)" -ForegroundColor Red
}

# 测试限流配置
Write-Host "[9/20] 测试限流配置 API..." -ForegroundColor Yellow
try {
    $resp = Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/admin/rate-limits" -Headers $headers -UseBasicParsing
    $data = $resp.Content | ConvertFrom-Json
    if ($data.success) {
        Write-Host "✓ 限流配置 API 正常" -ForegroundColor Green
    } else {
        Write-Host "✗ 限流配置 API 返回失败" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ 限流配置 API 失败: $($_.Exception.Message)" -ForegroundColor Red
}

# 测试敏感词
Write-Host "[10/20] 测试敏感词 API..." -ForegroundColor Yellow
try {
    $resp = Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/admin/sensitive-words" -Headers $headers -UseBasicParsing
    $data = $resp.Content | ConvertFrom-Json
    if ($data.success) {
        Write-Host "✓ 敏感词 API 正常" -ForegroundColor Green
    } else {
        Write-Host "✗ 敏感词 API 返回失败" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ 敏感词 API 失败: $($_.Exception.Message)" -ForegroundColor Red
}

# 测试Prompt模板
Write-Host "[11/20] 测试Prompt模板 API..." -ForegroundColor Yellow
try {
    $resp = Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/admin/prompt-templates" -Headers $headers -UseBasicParsing
    $data = $resp.Content | ConvertFrom-Json
    if ($data.success) {
        Write-Host "✓ Prompt模板 API 正常" -ForegroundColor Green
    } else {
        Write-Host "✗ Prompt模板 API 返回失败" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ Prompt模板 API 失败: $($_.Exception.Message)" -ForegroundColor Red
}

# 测试日志
Write-Host "[12/20] 测试系统日志 API..." -ForegroundColor Yellow
try {
    $resp = Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/admin/logs?page=1%26per_page=10" -Headers $headers -UseBasicParsing
    $data = $resp.Content | ConvertFrom-Json
    if ($data.success) {
        Write-Host "✓ 系统日志 API 正常" -ForegroundColor Green
    } else {
        Write-Host "✗ 系统日志 API 返回失败" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ 系统日志 API 失败: $($_.Exception.Message)" -ForegroundColor Red
}

# 测试实时监控
Write-Host "[13/20] 测试实时监控 API..." -ForegroundColor Yellow
try {
    $resp = Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/admin/monitor/realtime" -Headers $headers -UseBasicParsing
    $data = $resp.Content | ConvertFrom-Json
    if ($data.success) {
        Write-Host "✓ 实时监控 API 正常" -ForegroundColor Green
    } else {
        Write-Host "✗ 实时监控 API 返回失败" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ 实时监控 API 失败: $($_.Exception.Message)" -ForegroundColor Red
}

# 测试品种信息
Write-Host "[14/20] 测试品种信息 API..." -ForegroundColor Yellow
try {
    $resp = Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/admin/breeds" -Headers $headers -UseBasicParsing
    $data = $resp.Content | ConvertFrom-Json
    if ($data.success) {
        Write-Host "✓ 品种信息 API 正常" -ForegroundColor Green
    } else {
        Write-Host "✗ 品种信息 API 返回失败" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ 品种信息 API 失败: $($_.Exception.Message)" -ForegroundColor Red
}

# 测试限流日志
Write-Host "[15/20] 测试限流日志 API..." -ForegroundColor Yellow
try {
    $resp = Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/admin/rate-limits/logs" -Headers $headers -UseBasicParsing
    $data = $resp.Content | ConvertFrom-Json
    if ($data.success) {
        Write-Host "✓ 限流日志 API 正常" -ForegroundColor Green
    } else {
        Write-Host "✗ 限流日志 API 返回失败" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ 限流日志 API 失败: $($_.Exception.Message)" -ForegroundColor Red
}

# 测试Prompt列表
Write-Host "[16/20] 测试Prompt列表 API..." -ForegroundColor Yellow
try {
    $resp = Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/admin/prompts" -Headers $headers -UseBasicParsing
    $data = $resp.Content | ConvertFrom-Json
    if ($data.success) {
        Write-Host "✓ Prompt列表 API 正常" -ForegroundColor Green
    } else {
        Write-Host "✗ Prompt列表 API 返回失败" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ Prompt列表 API 失败: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "用户端API测试" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 测试公告列表（用户端）
Write-Host "[17/20] 测试用户端公告 API..." -ForegroundColor Yellow
try {
    $resp = Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/announcements" -UseBasicParsing
    $data = $resp.Content | ConvertFrom-Json
    if ($data.success) {
        Write-Host "✓ 用户端公告 API 正常" -ForegroundColor Green
    } else {
        Write-Host "✗ 用户端公告 API 返回失败" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ 用户端公告 API 失败: $($_.Exception.Message)" -ForegroundColor Red
}

# 测试识别历史
Write-Host "[18/20] 测试识别历史 API..." -ForegroundColor Yellow
try {
    $resp = Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/recognize/history" -Headers $headers -UseBasicParsing
    $data = $resp.Content | ConvertFrom-Json
    if ($data.success) {
        Write-Host "✓ 识别历史 API 正常" -ForegroundColor Green
    } else {
        Write-Host "✗ 识别历史 API 返回失败" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ 识别历史 API 失败: $($_.Exception.Message)" -ForegroundColor Red
}

# 测试我的反馈
Write-Host "[19/20] 测试我的反馈 API..." -ForegroundColor Yellow
try {
    $resp = Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/feedback/my" -Headers $headers -UseBasicParsing
    $data = $resp.Content | ConvertFrom-Json
    if ($data.success) {
        Write-Host "✓ 我的反馈 API 正常" -ForegroundColor Green
    } else {
        Write-Host "✗ 我的反馈 API 返回失败" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ 我的反馈 API 失败: $($_.Exception.Message)" -ForegroundColor Red
}

# 测试收藏
Write-Host "[20/20] 测试收藏列表 API..." -ForegroundColor Yellow
try {
    $resp = Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/favorites" -Headers $headers -UseBasicParsing
    $data = $resp.Content | ConvertFrom-Json
    if ($data.success) {
        Write-Host "✓ 收藏列表 API 正常" -ForegroundColor Green
    } else {
        Write-Host "✗ 收藏列表 API 返回失败" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ 收藏列表 API 失败: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "测试完成！" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
