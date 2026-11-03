$ErrorActionPreference = 'Stop'
$repo = 'pm5120-alt/campus-lost-and-found'
$remote = "https://github.com/$repo.git"

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw 'Git is required. Install Git for Windows, then run this script again.'
}
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    throw 'GitHub CLI is required. Install it from https://cli.github.com/ and run this script again.'
}

# Authenticate in the browser when GitHub CLI is not already signed in.
gh auth status --hostname github.com 2>$null
if ($LASTEXITCODE -ne 0) {
    gh auth login --hostname github.com --git-protocol https --web
    if ($LASTEXITCODE -ne 0) { throw 'GitHub authentication did not complete.' }
}
gh auth setup-git
if ($LASTEXITCODE -ne 0) { throw 'Could not configure Git to use GitHub CLI authentication.' }

if (-not (Test-Path '.git')) {
    git init --initial-branch=main
    if ($LASTEXITCODE -ne 0) { throw 'Could not initialize the local Git repository.' }
}

git add --all
if ($LASTEXITCODE -ne 0) { throw 'Could not stage project files.' }

git diff --cached --quiet
if ($LASTEXITCODE -ne 0) {
    git commit -m 'Update Campus Lost and Found application'
    if ($LASTEXITCODE -ne 0) { throw 'Git commit failed. Check your Git name and email settings.' }
}

$origin = git remote get-url origin 2>$null
if ($LASTEXITCODE -eq 0 -and $origin) {
    if ($origin -notmatch 'github\.com[:/]pm5120-alt/campus-lost-and-found(?:\.git)?$') {
        throw "An unrelated 'origin' remote already exists ($origin). Remove or rename it before publishing."
    }
} else {
    git remote add origin $remote
    if ($LASTEXITCODE -ne 0) { throw 'Could not add the GitHub remote.' }
}

git push -u origin main
if ($LASTEXITCODE -ne 0) { throw 'Push failed. Check GitHub authentication and branch history.' }

Write-Host "Published: https://github.com/$repo" -ForegroundColor Green
