# Installs the themes into your default Firefox profile (Windows).
# Run it in a normal PowerShell, with Firefox closed:
#     powershell -ExecutionPolicy Bypass -File install.ps1
#
# It backs up the profile's existing chrome folder, copies the themes in and adds
# one line to user.js. It never edits prefs.js and needs no admin rights.
# To install into a specific profile instead:  -ProfileDir "C:\path\to\profile"
param([string]$ProfileDir)
$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path

if (-not $ProfileDir) {
  if (Get-Process firefox -ErrorAction SilentlyContinue) {
    Write-Host "Please close Firefox completely, then run this again." -ForegroundColor Yellow
    exit 1
  }
  $ff = Join-Path $env:APPDATA "Mozilla\Firefox"
  $iniPath = Join-Path $ff "profiles.ini"
  if (-not (Test-Path $iniPath)) { throw "Firefox profile list not found. Start Firefox once, close it, and try again." }
  $ini = Get-Content $iniPath
  # the [Install...] section names the profile this Firefox really uses
  $rel = $ini | Where-Object { $_ -like "Default=Profiles/*" } | Select-Object -First 1
  if (-not $rel) {
    $inSection = $false
    foreach ($line in $ini) {
      if ($line -match '^\[') { $inSection = $false }
      if ($line -eq "Name=default-release") { $inSection = $true }
      if ($inSection -and $line -like "Path=*") { $rel = $line; break }
    }
  }
  if (-not $rel) { throw "Could not find your default profile. Use -ProfileDir with the folder shown in about:support." }
  $ProfileDir = Join-Path $ff ((($rel -split "=", 2)[1]) -replace "/", "\")
}
if (-not (Test-Path $ProfileDir)) { throw "Profile folder not found: $ProfileDir" }
Write-Host "Profile: $ProfileDir"

# back up what is there
$chrome = Join-Path $ProfileDir "chrome"
if (Test-Path $chrome) {
  $backup = "$chrome-backup-$(Get-Date -Format yyyyMMdd-HHmmss)"
  Copy-Item $chrome $backup -Recurse
  Write-Host "Backed up your existing chrome folder to $(Split-Path $backup -Leaf)"
} else {
  New-Item -ItemType Directory $chrome | Out-Null
}

# copy the themes
New-Item -ItemType Directory -Force (Join-Path $chrome "themes") | Out-Null
foreach ($t in Get-ChildItem (Join-Path $here "chrome\themes") -Directory) {
  $dest = Join-Path $chrome "themes\$($t.Name)"
  if (Test-Path $dest) { Remove-Item $dest -Recurse -Force }
  Copy-Item $t.FullName $dest -Recurse
  Write-Host "Installed: $($t.Name)"
}
Copy-Item (Join-Path $here "chrome\userChrome.css") (Join-Path $chrome "userChrome.css") -Force
Copy-Item (Join-Path $here "chrome\userContent.css") (Join-Path $chrome "userContent.css") -Force

# add the one required pref, keeping anything already in user.js
$userJs = Join-Path $ProfileDir "user.js"
$pref = 'user_pref("toolkit.legacyUserProfileCustomizations.stylesheets", true);'
$existing = if (Test-Path $userJs) { Get-Content $userJs } else { @() }
if ($existing -notcontains $pref) {
  Add-Content -Path $userJs -Encoding ascii -Value @("", "// Lets Firefox load chrome/userChrome.css and chrome/userContent.css.", $pref)
  Write-Host "Added the required line to user.js"
}

Write-Host ""
Write-Host "Done. Start Firefox: Nocturne is the default theme." -ForegroundColor Green
$loader = "C:\Program Files\Mozilla Firefox\theme-loader.cfg"
if (-not (Test-Path $loader)) {
  Write-Host "Optional: for the palette button, live switching, the Meridian clock and music, read" -ForegroundColor Yellow
  Write-Host "'Step 2' in README.md. It needs admin rights and has a security trade-off, so it's your call." -ForegroundColor Yellow
}
