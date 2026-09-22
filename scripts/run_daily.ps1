# Runs the daily Telegram -> RSS digest locally and pushes the result to
# GitHub, so LinkedIn's RSS source can pick it up. Schedule this with
# Windows Task Scheduler.
$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

Get-Content .env | ForEach-Object {
    if ($_ -match '^\s*#' -or $_ -match '^\s*$') { return }
    $parts = $_ -split '=', 2
    if ($parts.Length -eq 2) {
        [System.Environment]::SetEnvironmentVariable($parts[0].Trim(), $parts[1].Trim())
    }
}

git pull --ff-only

Set-Location src
python main.py
Set-Location ..

git add docs/feed.xml docs/history.json state/last_post.json
git diff --cached --quiet
if ($LASTEXITCODE -ne 0) {
    git commit -m "chore: publish daily digest entry"
    git push
} else {
    Write-Host "Nothing new to publish."
}
