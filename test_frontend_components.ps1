# PetWise Frontend Interaction Test

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PetWise Frontend Interaction Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Test frontend pages and components

Write-Host "Testing Frontend Components:" -ForegroundColor Yellow
Write-Host ""

$tests = @()

# BreedDetail component check
$breedDetailPath = "e:\PetWise\Frontend\src\views\BreedDetail.vue"
if (Test-Path $breedDetailPath) {
    $content = Get-Content $breedDetailPath -Raw
    if ($content -match "submitComment" -and $content -match "loadComments" -and $content -match "likeComment") {
        Write-Host "[OK] BreedDetail.vue - Comment functions found" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] BreedDetail.vue - Missing comment functions" -ForegroundColor Red
    }
}

# Favorites component check
$favoritesPath = "e:\PetWise\Frontend\src\views\Favorites.vue"
if (Test-Path $favoritesPath) {
    $content = Get-Content $favoritesPath -Raw
    if ($content -match "loadFavorites" -and $content -match "removeFavorite") {
        Write-Host "[OK] Favorites.vue - Favorites functions found" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] Favorites.vue - Missing functions" -ForegroundColor Red
    }
}

# Pets component check
$petsPath = "e:\PetWise\Frontend\src\views\Pets.vue"
if (Test-Path $petsPath) {
    $content = Get-Content $petsPath -Raw
    if ($content -match "loadPets" -and $content -match "addPet") {
        Write-Host "[OK] Pets.vue - Pet functions found" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] Pets.vue - Missing functions" -ForegroundColor Red
    }
}

# Recognize component check
$recognizePath = "e:\PetWise\Frontend\src\views\Recognize.vue"
if (Test-Path $recognizePath) {
    $content = Get-Content $recognizePath -Raw
    if ($content -match "handleFileChange" -and $content -match "uploadImage" -and $content -match "submitCorrection") {
        Write-Host "[OK] Recognize.vue - Recognition functions found" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] Recognize.vue - Missing functions" -ForegroundColor Red
    }
}

# BatchRecognize component check
$batchPath = "e:\PetWise\Frontend\src\views\BatchRecognize.vue"
if (Test-Path $batchPath) {
    $content = Get-Content $batchPath -Raw
    if ($content -match "handleFiles" -and $content -match "batchRecognize") {
        Write-Host "[OK] BatchRecognize.vue - Batch functions found" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] BatchRecognize.vue - Missing functions" -ForegroundColor Red
    }
}

# Feedback component check
$feedbackPath = "e:\PetWise\Frontend\src\views\Feedback.vue"
if (Test-Path $feedbackPath) {
    $content = Get-Content $feedbackPath -Raw
    if ($content -match "loadFeedback" -and $content -match "submitFeedback") {
        Write-Host "[OK] Feedback.vue - Feedback functions found" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] Feedback.vue - Missing functions" -ForegroundColor Red
    }
}

# Schedule component check
$schedulePath = "e:\PetWise\Frontend\src\views\Schedule.vue"
if (Test-Path $schedulePath) {
    $content = Get-Content $schedulePath -Raw
    if ($content -match "loadReminders" -and $content -match "addReminder") {
        Write-Host "[OK] Schedule.vue - Schedule functions found" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] Schedule.vue - Missing functions" -ForegroundColor Red
    }
}

# HealthRecords component check
$healthPath = "e:\PetWise\Frontend\src\views\HealthRecords.vue"
if (Test-Path $healthPath) {
    $content = Get-Content $healthPath -Raw
    if ($content -match "loadHealthRecords" -and $content -match "addHealthRecord") {
        Write-Host "[OK] HealthRecords.vue - Health functions found" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] HealthRecords.vue - Missing functions" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Testing Admin Components:" -ForegroundColor Yellow
Write-Host ""

# Admin Samples component check
$samplesPath = "e:\PetWise\Frontend\src\views\admin\Samples.vue"
if (Test-Path $samplesPath) {
    $content = Get-Content $samplesPath -Raw
    if ($content -match "loadSamples" -and $content -match "reviewSample" -and $content -match "deleteSample") {
        Write-Host "[OK] admin/Samples.vue - Sample functions found" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] admin/Samples.vue - Missing functions" -ForegroundColor Red
    }
}

# Admin Corrections component check
$corrPath = "e:\PetWise\Frontend\src\views\admin\Corrections.vue"
if (Test-Path $corrPath) {
    $content = Get-Content $corrPath -Raw
    if ($content -match "loadCorrections" -and $content -match "handleCorrection") {
        Write-Host "[OK] admin/Corrections.vue - Correction functions found" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] admin/Corrections.vue - Missing functions" -ForegroundColor Red
    }
}

# Admin Feedback component check
$adminFeedbackPath = "e:\PetWise\Frontend\src\views\admin\Feedback.vue"
if (Test-Path $adminFeedbackPath) {
    $content = Get-Content $adminFeedbackPath -Raw
    if ($content -match "loadFeedback" -and $content -match "replyFeedback") {
        Write-Host "[OK] admin/Feedback.vue - Admin feedback functions found" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] admin/Feedback.vue - Missing functions" -ForegroundColor Red
    }
}

# Admin Announcements component check
$annPath = "e:\PetWise\Frontend\src\views\admin\Announcements.vue"
if (Test-Path $annPath) {
    $content = Get-Content $annPath -Raw
    if ($content -match "loadAnnouncements" -and $content -match "addAnnouncement") {
        Write-Host "[OK] admin/Announcements.vue - Announcement functions found" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] admin/Announcements.vue - Missing functions" -ForegroundColor Red
    }
}

# Admin Users component check
$usersPath = "e:\PetWise\Frontend\src\views\admin\Users.vue"
if (Test-Path $usersPath) {
    $content = Get-Content $usersPath -Raw
    if ($content -match "loadUsers" -and $content -match "handleUser") {
        Write-Host "[OK] admin/Users.vue - User management functions found" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] admin/Users.vue - Missing functions" -ForegroundColor Red
    }
}

# Admin Models component check
$modelsPath = "e:\PetWise\Frontend\src\views\admin\Models.vue"
if (Test-Path $modelsPath) {
    $content = Get-Content $modelsPath -Raw
    if ($content -match "loadModels" -and $content -match "handleModel") {
        Write-Host "[OK] admin/Models.vue - Model management functions found" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] admin/Models.vue - Missing functions" -ForegroundColor Red
    }
}

# Admin Knowledge component check
$knowledgePath = "e:\PetWise\Frontend\src\views\admin\Knowledge.vue"
if (Test-Path $knowledgePath) {
    $content = Get-Content $knowledgePath -Raw
    if ($content -match "loadKnowledge" -and $content -match "addKnowledge") {
        Write-Host "[OK] admin/Knowledge.vue - Knowledge functions found" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] admin/Knowledge.vue - Missing functions" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Frontend Component Test Complete" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
