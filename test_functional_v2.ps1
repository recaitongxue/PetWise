# PetWise Frontend Functional Test

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PetWise Frontend Functional Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$issues = @()
$fixed = 0

# Helper function
function Test-ComponentFunctions {
    param(
        [string]$name,
        [string]$path,
        [string[]]$requiredPatterns,
        [string[]]$buttonPatterns
    )
    
    Write-Host "`nTesting $name..." -ForegroundColor Yellow
    
    if (-not (Test-Path $path)) {
        Write-Host "  [FAIL] File not found: $path" -ForegroundColor Red
        $issues += "$name`: File not found"
        return
    }
    
    $content = Get-Content $path -Raw
    $missingPatterns = @()
    $missingButtons = @()
    
    # Check function patterns
    foreach ($pattern in $requiredPatterns) {
        if ($content -notmatch $pattern) {
            $missingPatterns += $pattern
        }
    }
    
    # Check button bindings
    foreach ($btn in $buttonPatterns) {
        if ($content -notmatch $btn) {
            $missingButtons += $btn
        }
    }
    
    if ($missingPatterns.Count -eq 0 -and $missingButtons.Count -eq 0) {
        Write-Host "  [OK] All functions and buttons found" -ForegroundColor Green
        $script:fixed++
    } else {
        if ($missingPatterns.Count -gt 0) {
            Write-Host "  [WARN] Missing function patterns: $($missingPatterns -join ', ')" -ForegroundColor Yellow
        }
        if ($missingButtons.Count -gt 0) {
            Write-Host "  [WARN] Missing button handlers: $($missingButtons -join ', ')" -ForegroundColor Yellow
        }
        $issues += "$name`: Missing patterns"
    }
}

# User Components
Test-ComponentFunctions "BreedDetail.vue" "e:\PetWise\Frontend\src\views\BreedDetail.vue" `
    @("loadBreedInfo", "loadComments", "submitComment", "likeComment", "toggleFavorite") `
    @("submitComment", "likeComment", "toggleFavorite")

Test-ComponentFunctions "Favorites.vue" "e:\PetWise\Frontend\src\views\Favorites.vue" `
    @("loadFavorites", "removeFavorite") `
    @("removeFavorite", "goToDetail")

Test-ComponentFunctions "Pets.vue" "e:\PetWise\Frontend\src\views\Pets.vue" `
    @("loadPets", "addPet", "deletePet") `
    @("addPet", "deletePet")

Test-ComponentFunctions "Recognize.vue" "e:\PetWise\Frontend\src\views\Recognize.vue" `
    @("handleRecognize", "submitCorrection", "loadHistory", "loadAllBreeds") `
    @("handleRecognize", "submitCorrection", "loadHistory")

Test-ComponentFunctions "BatchRecognize.vue" "e:\PetWise\Frontend\src\views\BatchRecognize.vue" `
    @("handleBatchRecognize", "clearResults") `
    @("handleBatchRecognize", "clearResults")

Test-ComponentFunctions "Feedback.vue" "e:\PetWise\Frontend\src\views\Feedback.vue" `
    @("submitFeedback", "loadFeedbackHistory") `
    @("submitFeedback")

Test-ComponentFunctions "Schedule.vue" "e:\PetWise\Frontend\src\views\Schedule.vue" `
    @("loadReminders", "addReminder", "completeReminder", "deleteReminder") `
    @("submitReminder", "completeReminder", "deleteReminder")

Test-ComponentFunctions "Profile.vue" "e:\PetWise\Frontend\src\views\Profile.vue" `
    @("loadProfile", "updateProfile") `
    @("updateProfile")

# Admin Components
Test-ComponentFunctions "Admin Dashboard" "e:\PetWise\Frontend\src\views\Admin.vue" `
    @("loadStats") `
    @()

Test-ComponentFunctions "Admin Samples" "e:\PetWise\Frontend\src\views\admin\Samples.vue" `
    @("getSamples", "handleReview", "handleExport", "handleRelabel") `
    @("handleReview", "handleExport", "handleRelabel")

Test-ComponentFunctions "Admin Corrections" "e:\PetWise\Frontend\src\views\admin\Corrections.vue" `
    @("loadCorrections", "approveCorrection", "rejectCorrection") `
    @("approveCorrection", "rejectCorrection")

Test-ComponentFunctions "Admin Feedback" "e:\PetWise\Frontend\src\views\admin\Feedback.vue" `
    @("loadFeedback", "replyFeedback") `
    @("replyFeedback")

Test-ComponentFunctions "Admin Announcements" "e:\PetWise\Frontend\src\views\admin\Announcements.vue" `
    @("loadAnnouncements", "createAnnouncement") `
    @("createAnnouncement")

Test-ComponentFunctions "Admin Users" "e:\PetWise\Frontend\src\views\admin\Users.vue" `
    @("loadUsers", "addUser", "saveUser", "deleteUser") `
    @("addUser", "saveUser", "deleteUser")

Test-ComponentFunctions "Admin Knowledge" "e:\PetWise\Frontend\src\views\admin\Knowledge.vue" `
    @("loadKnowledge", "addKnowledge", "saveKnowledge") `
    @("addKnowledge", "saveKnowledge")

Test-ComponentFunctions "Admin Logs" "e:\PetWise\Frontend\src\views\admin\Logs.vue" `
    @("loadLogs") `
    @()

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Test Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
$total = $fixed + $issues.Count
Write-Host "Components Tested: $total" -ForegroundColor Cyan
Write-Host "Passed: $fixed" -ForegroundColor Green
Write-Host "Issues: $($issues.Count)" -ForegroundColor $(if ($issues.Count -eq 0) { "Green" } else { "Yellow" })
Write-Host ""

if ($issues.Count -gt 0) {
    Write-Host "Components with issues:" -ForegroundColor Yellow
    foreach ($issue in $issues) {
        Write-Host "  - $issue" -ForegroundColor Red
    }
}
