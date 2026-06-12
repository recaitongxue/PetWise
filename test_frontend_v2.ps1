# PetWise Frontend Comprehensive Test

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PetWise Frontend Comprehensive Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$totalChecks = 0
$passedChecks = 0

# Helper function
function Test-Component($name, $path, $functions) {
    Write-Host "Checking $name..." -ForegroundColor Yellow
    $totalChecks++
    
    if (-not (Test-Path $path)) {
        Write-Host "  [FAIL] File not found: $path" -ForegroundColor Red
        return $false
    }
    
    $content = Get-Content $path -Raw
    $missing = @()
    
    foreach ($func in $functions) {
        if ($content -notmatch $func) {
            $missing += $func
        }
    }
    
    if ($missing.Count -eq 0) {
        Write-Host "  [OK] All required functions found" -ForegroundColor Green
        $script:passedChecks++
        return $true
    } else {
        Write-Host "  [FAIL] Missing functions: $($missing -join ', ')" -ForegroundColor Red
        return $false
    }
}

Write-Host "=== User Frontend ===" -ForegroundColor Cyan

# User Components
Test-Component "BreedDetail.vue" "e:\PetWise\Frontend\src\views\BreedDetail.vue" @("loadBreedInfo", "loadComments", "submitComment", "likeComment", "toggleFavorite")
Test-Component "Favorites.vue" "e:\PetWise\Frontend\src\views\Favorites.vue" @("loadFavorites", "removeFavorite", "addFavorite")
Test-Component "Pets.vue" "e:\PetWise\Frontend\src\views\Pets.vue" @("loadPets", "addPet", "deletePet", "updatePet")
Test-Component "Recognize.vue" "e:\PetWise\Frontend\src\views\Recognize.vue" @("handleRecognize", "submitCorrection", "loadHistory", "loadAllBreeds")
Test-Component "BatchRecognize.vue" "e:\PetWise\Frontend\src\views\BatchRecognize.vue" @("handleFiles", "batchRecognize", "clearResults")
Test-Component "Feedback.vue" "e:\PetWise\Frontend\src\views\Feedback.vue" @("loadFeedback", "submitFeedback", "loadHistory")
Test-Component "Schedule.vue" "e:\PetWise\Frontend\src\views\Schedule.vue" @("loadReminders", "addReminder", "updateReminder", "deleteReminder")
Test-Component "HealthRecords.vue" "e:\PetWise\Frontend\src\views\HealthRecords.vue" @("loadHealthRecords", "addHealthRecord", "deleteHealthRecord")
Test-Component "Profile.vue" "e:\PetWise\Frontend\src\views\Profile.vue" @("loadProfile", "updateProfile", "updatePassword")
Test-Component "Agent.vue" "e:\PetWise\Frontend\src\views\Agent.vue" @("sendMessage", "loadHistory", "clearChat")

Write-Host ""
Write-Host "=== Admin Frontend ===" -ForegroundColor Cyan

# Admin Components
Test-Component "Admin Dashboard" "e:\PetWise\Frontend\src\views\Admin.vue" @("loadStats")
Test-Component "Admin Samples" "e:\PetWise\Frontend\src\views\admin\Samples.vue" @("loadSamples", "reviewSample", "deleteSample", "exportSamples")
Test-Component "Admin Corrections" "e:\PetWise\Frontend\src\views\admin\Corrections.vue" @("loadCorrections", "handleCorrection")
Test-Component "Admin Feedback" "e:\PetWise\Frontend\src\views\admin\Feedback.vue" @("loadFeedback", "replyFeedback")
Test-Component "Admin Announcements" "e:\PetWise\Frontend\src\views\admin\Announcements.vue" @("loadAnnouncements", "addAnnouncement", "updateAnnouncement", "deleteAnnouncement")
Test-Component "Admin Users" "e:\PetWise\Frontend\src\views\admin\Users.vue" @("loadUsers", "handleUser", "exportUsers", "importUsers")
Test-Component "Admin Models" "e:\PetWise\Frontend\src\views\admin\Models.vue" @("loadModels", "handleModel", "setDefaultModel")
Test-Component "Admin Knowledge" "e:\PetWise\Frontend\src\views\admin\Knowledge.vue" @("loadKnowledge", "addKnowledge", "updateKnowledge", "deleteKnowledge")
Test-Component "Admin Logs" "e:\PetWise\Frontend\src\views\admin\Logs.vue" @("loadLogs")
Test-Component "Admin RateLimits" "e:\PetWise\Frontend\src\views\admin\RateLimits.vue" @("loadRateLimits", "addRateLimit", "updateRateLimit", "deleteRateLimit")
Test-Component "Admin SensitiveWords" "e:\PetWise\Frontend\src\views\admin\SensitiveWords.vue" @("loadSensitiveWords", "addSensitiveWord", "updateSensitiveWord", "deleteSensitiveWord")
Test-Component "Admin Prompts" "e:\PetWise\Frontend\src\views\admin\Prompts.vue" @("loadPrompts", "addPrompt", "updatePrompt", "deletePrompt")
Test-Component "Admin Stats" "e:\PetWise\Frontend\src\views\admin\Stats.vue" @("loadStats")

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Test Summary: $passedChecks/$totalChecks passed" -ForegroundColor $(if ($passedChecks -eq $totalChecks) { "Green" } else { "Yellow" })
Write-Host "========================================" -ForegroundColor Cyan
