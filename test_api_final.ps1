# PetWise API Full Test

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PetWise API Full Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get admin token
Write-Host "Getting admin token..." -ForegroundColor Yellow
$loginResp = Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/auth/login" -Method POST -Body '{"username":"admin","password":"admin123"}' -ContentType "application/json" -UseBasicParsing
$loginData = $loginResp.Content | ConvertFrom-Json

if ($loginData.success) {
    Write-Host "SUCCESS: Login" -ForegroundColor Green
    $adminToken = $loginData.token
} else {
    Write-Host "FAIL: Login" -ForegroundColor Red
    exit 1
}

$headers = @{
    "Authorization" = "Bearer $adminToken"
}

Write-Host ""
Write-Host "Admin API Tests:" -ForegroundColor Cyan
Write-Host ""

$tests = @(
    @{Name="Stats"; Uri="http://127.0.0.1:5000/api/admin/stats"},
    @{Name="Users"; Uri="http://127.0.0.1:5000/api/admin/users"},
    @{Name="Announcements"; Uri="http://127.0.0.1:5000/api/admin/announcements"},
    @{Name="Feedback"; Uri="http://127.0.0.1:5000/api/admin/feedback"},
    @{Name="Corrections"; Uri="http://127.0.0.1:5000/api/admin/corrections"},
    @{Name="Knowledge"; Uri="http://127.0.0.1:5000/api/admin/knowledge"},
    @{Name="HardSamples"; Uri="http://127.0.0.1:5000/api/admin/samples/hard"},
    @{Name="RateLimits"; Uri="http://127.0.0.1:5000/api/admin/rate-limits"},
    @{Name="SensitiveWords"; Uri="http://127.0.0.1:5000/api/admin/sensitive-words"},
    @{Name="PromptTemplates"; Uri="http://127.0.0.1:5000/api/admin/prompt-templates"},
    @{Name="Logs"; Uri="http://127.0.0.1:5000/api/admin/logs"},
    @{Name="RealtimeMonitor"; Uri="http://127.0.0.1:5000/api/admin/monitor/realtime"},
    @{Name="Breeds"; Uri="http://127.0.0.1:5000/api/admin/breeds"},
    @{Name="RateLimitsLogs"; Uri="http://127.0.0.1:5000/api/admin/rate-limits/logs"},
    @{Name="Prompts"; Uri="http://127.0.0.1:5000/api/admin/prompts"},
    @{Name="UserAnnouncements"; Uri="http://127.0.0.1:5000/api/announcements"},
    @{Name="RecognitionHistory"; Uri="http://127.0.0.1:5000/api/recognize/history"},
    @{Name="MyFeedback"; Uri="http://127.0.0.1:5000/api/feedback/my"},
    @{Name="Favorites"; Uri="http://127.0.0.1:5000/api/favorites"}
)

$successCount = 0
$failCount = 0

foreach ($test in $tests) {
    $needAuth = $test.Uri -notmatch "/api/announcements"
    
    try {
        if ($needAuth) {
            $resp = Invoke-WebRequest -Uri $test.Uri -Headers $headers -UseBasicParsing
        } else {
            $resp = Invoke-WebRequest -Uri $test.Uri -UseBasicParsing
        }
        
        $data = $resp.Content | ConvertFrom-Json
        
        if ($data.success) {
            Write-Host "[OK] $($test.Name)" -ForegroundColor Green
            $successCount++
        } else {
            Write-Host "[FAIL] $($test.Name)" -ForegroundColor Red
            $failCount++
        }
    } catch {
        Write-Host "[ERROR] $($test.Name): $($_.Exception.Message)" -ForegroundColor Red
        $failCount++
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Test Summary" -ForegroundColor Cyan
Write-Host "Success: $successCount" -ForegroundColor Green
Write-Host "Failed: $failCount" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Cyan
