# GitHub Upload Script for Windows PowerShell
# Usage: Run this script in PowerShell

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  GitHub Project Upload Script" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Set working directory
$PROJECT_DIR = "e:\Code\value of LLM\LLM's values"
Set-Location $PROJECT_DIR

# Step 1: Configure Git user
Write-Host "Step 1: Configure Git User" -ForegroundColor Yellow
Write-Host ""
Write-Host "Enter your GitHub username:"
$GIT_USERNAME = Read-Host
Write-Host "Enter your GitHub email:"
$GIT_EMAIL = Read-Host

git config --global user.name "$GIT_USERNAME"
git config --global user.email "$GIT_EMAIL"
Write-Host "[OK] Git user configured" -ForegroundColor Green
Write-Host ""

# Step 2: Initialize Git repository
Write-Host "Step 2: Initialize Git Repository" -ForegroundColor Yellow
if (Test-Path ".git") {
    Write-Host "[WARNING] Git repository already exists" -ForegroundColor Yellow
} else {
    git init
    Write-Host "[OK] Git repository initialized" -ForegroundColor Green
}
Write-Host ""

# Step 3: Add remote repository
Write-Host "Step 3: Configure Remote Repository" -ForegroundColor Yellow
Write-Host ""
Write-Host "Enter your GitHub repository URL (e.g., https://github.com/username/repo.git):"
$REPO_URL = Read-Host

$remotes = git remote
if ($remotes -contains "origin") {
    Write-Host "[WARNING] Remote 'origin' exists, updating URL" -ForegroundColor Yellow
    git remote set-url origin $REPO_URL
} else {
    git remote add origin $REPO_URL
}
Write-Host "[OK] Remote repository configured" -ForegroundColor Green
Write-Host ""

# Step 4: Fetch and create branch
Write-Host "Step 4: Create Branch update-1119" -ForegroundColor Yellow
$BRANCH_NAME = "update-1119"
Write-Host "Branch name: $BRANCH_NAME"

Write-Host "Fetching remote branches..."
git fetch origin 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Remote branches fetched" -ForegroundColor Green
    
    $remoteBranches = git branch -r
    if ($remoteBranches -match "origin/$BRANCH_NAME") {
        Write-Host "Remote branch exists, checking out..." -ForegroundColor Cyan
        git checkout -b $BRANCH_NAME origin/$BRANCH_NAME 2>$null
        if ($LASTEXITCODE -ne 0) {
            git checkout $BRANCH_NAME
        }
    } else {
        Write-Host "Creating new branch..." -ForegroundColor Cyan
        git checkout -b $BRANCH_NAME 2>$null
        if ($LASTEXITCODE -ne 0) {
            git checkout $BRANCH_NAME
        }
    }
} else {
    Write-Host "[WARNING] Cannot fetch remote (new repo?), creating local branch" -ForegroundColor Yellow
    git checkout -b $BRANCH_NAME 2>$null
    if ($LASTEXITCODE -ne 0) {
        git checkout $BRANCH_NAME
    }
}
Write-Host "[OK] Branch ready" -ForegroundColor Green
Write-Host ""

# Step 5: Clean Git cache
Write-Host "Step 5: Clean Git Cache" -ForegroundColor Yellow
git rm -r --cached . 2>$null
Write-Host "[OK] Cache cleaned" -ForegroundColor Green
Write-Host ""

# Step 6: Add files
Write-Host "Step 6: Add Files (applying .gitignore rules)" -ForegroundColor Yellow
git add .
Write-Host "[OK] Files added" -ForegroundColor Green
Write-Host ""

# Step 7: Check status
Write-Host "Step 7: Check Files to Commit" -ForegroundColor Yellow
Write-Host ""
$statusOutput = git status --short
$fileCount = ($statusOutput | Measure-Object).Count
Write-Host "Files to commit: $fileCount" -ForegroundColor Cyan
Write-Host ""
Write-Host "Main changes (first 30 files):"
$statusOutput | Select-Object -First 30 | ForEach-Object { Write-Host $_ }
if ($fileCount -gt 30) {
    Write-Host "... and $($fileCount - 30) more files" -ForegroundColor Gray
}
Write-Host ""

# Step 8: Check large files
Write-Host "Step 8: Check Large Files (>10MB)" -ForegroundColor Yellow
$largeFiles = @()
git diff --cached --name-only | ForEach-Object {
    if (Test-Path $_) {
        $size = (Get-Item $_).Length / 1MB
        if ($size -gt 10) {
            $largeFiles += "$_ - $([math]::Round($size, 2))MB"
            Write-Host "[WARNING] $_ - $([math]::Round($size, 2))MB" -ForegroundColor Red
        }
    }
}
if ($largeFiles.Count -eq 0) {
    Write-Host "[OK] No large files found" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "[WARNING] Found $($largeFiles.Count) large files" -ForegroundColor Red
    Write-Host "Continue? (y/n)"
    $continue = Read-Host
    if ($continue -ne "y") {
        Write-Host "Operation cancelled" -ForegroundColor Yellow
        exit
    }
}
Write-Host ""

# Step 9: Commit
Write-Host "Step 9: Commit Changes" -ForegroundColor Yellow
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$COMMIT_MSG = @"
Update: First commit after migrating to new computer

- Update project files to latest state
- Add .gitignore to exclude large files and model_cultural_comp-main
- Include latest analysis results and documentation
- Exclude large data files (can be regenerated via scripts)

Commit time: $timestamp
"@

git commit -m $COMMIT_MSG
Write-Host "[OK] Committed" -ForegroundColor Green
Write-Host ""

# Step 10: Push
Write-Host "Step 10: Push to GitHub" -ForegroundColor Yellow
Write-Host "Executing: git push -u origin $BRANCH_NAME"
Write-Host ""

$pushSuccess = $false
try {
    git push -u origin $BRANCH_NAME
    $pushSuccess = $true
} catch {
    Write-Host "Push failed, authentication may be required" -ForegroundColor Red
}

if ($pushSuccess -or $LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=====================================" -ForegroundColor Green
    Write-Host "  Successfully pushed to GitHub!" -ForegroundColor Green
    Write-Host "=====================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Visit your GitHub repository webpage"
    Write-Host "2. You will see a prompt to create Pull Request"
    Write-Host "3. Click Compare and pull request button"
    Write-Host "4. Fill in PR description and submit"
    Write-Host "5. Merge to main branch"
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "=====================================" -ForegroundColor Red
    Write-Host "  Push Failed" -ForegroundColor Red
    Write-Host "=====================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Possible reasons:" -ForegroundColor Yellow
    Write-Host "1. GitHub authentication required"
    Write-Host "   Solution: Configure GitHub Personal Access Token or SSH key"
    Write-Host ""
    Write-Host "2. Need to pull remote changes first"
    Write-Host "   Solution: git pull origin $BRANCH_NAME --rebase"
    Write-Host "   Then: git push -u origin $BRANCH_NAME"
    Write-Host ""
    Write-Host "3. Large files rejected"
    Write-Host "   Solution: Check large files list above, update .gitignore"
    Write-Host ""
}
