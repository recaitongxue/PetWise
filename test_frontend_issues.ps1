# PetWise Frontend Actual Functions Test

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PetWise Frontend Actual Functions Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$issues = @()

Write-Host "=== User Frontend Issues ===" -ForegroundColor Yellow

# Favorites.vue
$path = "e:\PetWise\Frontend\src\views\Favorites.vue"
if (Test-Path $path) {
    $content = Get-Content $path -Raw
    if ($content -notmatch "addFavorite") {
        Write-Host "  [!] Favorites.vue - addFavorite function missing" -ForegroundColor Yellow
        $issues += "Favorites.vue: addFavorite function missing"
    }
}

# BatchRecognize.vue
$path = "e:\PetWise\Frontend\src\views\BatchRecognize.vue"
if (Test-Path $path) {
    $content = Get-Content $path -Raw
    if ($content -notmatch "clearResults") {
        Write-Host "  [!] BatchRecognize.vue - clearResults function missing" -ForegroundColor Yellow
        $issues += "BatchRecognize.vue: clearResults function missing"
    }
}

# Feedback.vue
$path = "e:\PetWise\Frontend\src\views\Feedback.vue"
if (Test-Path $path) {
    $content = Get-Content $path -Raw
    if ($content -notmatch "loadHistory") {
        Write-Host "  [!] Feedback.vue - loadHistory function missing" -ForegroundColor Yellow
        $issues += "Feedback.vue: loadHistory function missing"
    }
}

# Schedule.vue
$path = "e:\PetWise\Frontend\src\views\Schedule.vue"
if (Test-Path $path) {
    $content = Get-Content $path -Raw
    if ($content -notmatch "updateReminder") {
        Write-Host "  [!] Schedule.vue - updateReminder function missing" -ForegroundColor Yellow
        $issues += "Schedule.vue: updateReminder function missing"
    }
}

# Profile.vue
$path = "e:\PetWise\Frontend\src\views\Profile.vue"
if (Test-Path $path) {
    $content = Get-Content $path -Raw
    if ($content -notmatch "updatePassword") {
        Write-Host "  [!] Profile.vue - updatePassword function missing" -ForegroundColor Yellow
        $issues += "Profile.vue: updatePassword function missing"
    }
}

# Agent.vue
$path = "e:\PetWise\Frontend\src\views\Agent.vue"
if (Test-Path $path) {
    $content = Get-Content $path -Raw
    if ($content -notmatch "clearChat") {
        Write-Host "  [!] Agent.vue - clearChat function missing" -ForegroundColor Yellow
        $issues += "Agent.vue: clearChat function missing"
    }
}

Write-Host ""
Write-Host "=== Admin Frontend Issues ===" -ForegroundColor Yellow

# Samples.vue
$path = "e:\PetWise\Frontend\src\views\admin\Samples.vue"
if (Test-Path $path) {
    $content = Get-Content $path -Raw
    if ($content -notmatch "loadSamples") {
        Write-Host "  [!] admin/Samples.vue - loadSamples function missing (found: getSamples)" -ForegroundColor Yellow
        $issues += "admin/Samples.vue: loadSamples function missing (found: getSamples)"
    }
}

# Corrections.vue
$path = "e:\PetWise\Frontend\src\views\admin\Corrections.vue"
if (Test-Path $path) {
    $content = Get-Content $path -Raw
    if ($content -notmatch "handleCorrection") {
        Write-Host "  [!] admin/Corrections.vue - handleCorrection function missing" -ForegroundColor Yellow
        $issues += "admin/Corrections.vue: handleCorrection function missing"
    }
}

# Announcements.vue
$path = "e:\PetWise\Frontend\src\views\admin\Announcements.vue"
if (Test-Path $path) {
    $content = Get-Content $path -Raw
    $missing = @()
    if ($content -notmatch "addAnnouncement") { $missing += "addAnnouncement" }
    if ($content -notmatch "updateAnnouncement") { $missing += "updateAnnouncement" }
    if ($content -notmatch "deleteAnnouncement") { $missing += "deleteAnnouncement" }
    
    if ($missing.Count -gt 0) {
        Write-Host "  [!] admin/Announcements.vue - Missing: $($missing -join ', ')" -ForegroundColor Yellow
        $issues += "admin/Announcements.vue: Missing functions: $($missing -join ', ')"
    }
}

# Users.vue
$path = "e:\PetWise\Frontend\src\views\admin\Users.vue"
if (Test-Path $path) {
    $content = Get-Content $path -Raw
    if ($content -notmatch "handleUser") {
        Write-Host "  [!] admin/Users.vue - handleUser function missing" -ForegroundColor Yellow
        $issues += "admin/Users.vue: handleUser function missing"
    }
}

# Models.vue
$path = "e:\PetWise\Frontend\src\views\admin\Models.vue"
if (Test-Path $path) {
    $content = Get-Content $path -Raw
    $missing = @()
    if ($content -notmatch "loadModels") { $missing += "loadModels" }
    if ($content -notmatch "handleModel") { $missing += "handleModel" }
    
    if ($missing.Count -gt 0) {
        Write-Host "  [!] admin/Models.vue - Missing: $($missing -join ', ')" -ForegroundColor Yellow
        $issues += "admin/Models.vue: Missing functions: $($missing -join ', ')"
    }
}

# Knowledge.vue
$path = "e:\PetWise\Frontend\src\views\admin\Knowledge.vue"
if (Test-Path $path) {
    $content = Get-Content $path -Raw
    $missing = @()
    if ($content -notmatch "loadKnowledge") { $missing += "loadKnowledge" }
    if ($content -notmatch "addKnowledge") { $missing += "addKnowledge" }
    
    if ($missing.Count -gt 0) {
        Write-Host "  [!] admin/Knowledge.vue - Missing: $($missing -join ', ')" -ForegroundColor Yellow
        $issues += "admin/Knowledge.vue: Missing functions: $($missing -join ', ')"
    }
}

# RateLimits.vue
$path = "e:\PetWise\Frontend\src\views\admin\RateLimits.vue"
if (Test-Path $path) {
    $content = Get-Content $path -Raw
    $missing = @()
    if ($content -notmatch "loadRateLimits") { $missing += "loadRateLimits" }
    if ($content -notmatch "addRateLimit") { $missing += "addRateLimit" }
    if ($content -notmatch "updateRateLimit") { $missing += "updateRateLimit" }
    if ($content -notmatch "deleteRateLimit") { $missing += "deleteRateLimit" }
    
    if ($missing.Count -gt 0) {
        Write-Host "  [!] admin/RateLimits.vue - Missing: $($missing -join ', ')" -ForegroundColor Yellow
        $issues += "admin/RateLimits.vue: Missing functions: $($missing -join ', ')"
    }
}

# SensitiveWords.vue
$path = "e:\PetWise\Frontend\src\views\admin\SensitiveWords.vue"
if (Test-Path $path) {
    $content = Get-Content $path -Raw
    $missing = @()
    if ($content -notmatch "loadSensitiveWords") { $missing += "loadSensitiveWords" }
    if ($content -notmatch "addSensitiveWord") { $missing += "addSensitiveWord" }
    if ($content -notmatch "updateSensitiveWord") { $missing += "updateSensitiveWord" }
    if ($content -notmatch "deleteSensitiveWord") { $missing += "deleteSensitiveWord" }
    
    if ($missing.Count -gt 0) {
        Write-Host "  [!] admin/SensitiveWords.vue - Missing: $($missing -join ', ')" -ForegroundColor Yellow
        $issues += "admin/SensitiveWords.vue: Missing functions: $($missing -join ', ')"
    }
}

# Prompts.vue
$path = "e:\PetWise\Frontend\src\views\admin\Prompts.vue"
if (Test-Path $path) {
    $content = Get-Content $path -Raw
    $missing = @()
    if ($content -notmatch "addPrompt") { $missing += "addPrompt" }
    if ($content -notmatch "updatePrompt") { $missing += "updatePrompt" }
    
    if ($missing.Count -gt 0) {
        Write-Host "  [!] admin/Prompts.vue - Missing: $($missing -join ', ')" -ForegroundColor Yellow
        $issues += "admin/Prompts.vue: Missing functions: $($missing -join ', ')"
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Issues Found: $($issues.Count)" -ForegroundColor $(if ($issues.Count -eq 0) { "Green" } else { "Yellow" })
Write-Host "========================================" -ForegroundColor Cyan

if ($issues.Count -gt 0) {
    Write-Host ""
    Write-Host "Details:" -ForegroundColor Yellow
    foreach ($issue in $issues) {
        Write-Host "  - $issue" -ForegroundColor Red
    }
}
