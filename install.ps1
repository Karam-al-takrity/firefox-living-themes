# Installs the themes into your default Firefox profile (Windows).
# Run it in a normal PowerShell, with Firefox closed:
#     powershell -ExecutionPolicy Bypass -File install.ps1
#
# It backs up the profile's existing chrome folder, copies the themes in and adds
# one line to user.js. It needs no admin rights.
#
#   -CssOnly     install the CSS-only edition (no JavaScript, no theme loader).
#                It also creates the theme switches in about:config, by adding
#                them to prefs.js while Firefox is closed.
#   -ProfileDir  install into a specific profile instead of the default one.
param([string]$ProfileDir, [switch]$CssOnly)
$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$source = if ($CssOnly) { Join-Path $here "css-only\chrome" } else { Join-Path $here "chrome" }
if (-not (Test-Path $source)) { throw "Theme files not found: $source" }

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

# copy the themes. The old themes folder is replaced as a whole (it's in the backup),
# so switching editions never leaves an old script behind.
$themes = Join-Path $chrome "themes"
if (Test-Path $themes) { Remove-Item $themes -Recurse -Force }
New-Item -ItemType Directory $themes | Out-Null
foreach ($t in Get-ChildItem (Join-Path $source "themes") -Directory) {
  Copy-Item $t.FullName (Join-Path $themes $t.Name) -Recurse
  Write-Host "Installed: $($t.Name)"
}
Copy-Item (Join-Path $source "userChrome.css") (Join-Path $chrome "userChrome.css") -Force
Copy-Item (Join-Path $source "userContent.css") (Join-Path $chrome "userContent.css") -Force

# add the one required pref, keeping anything already in user.js
$userJs = Join-Path $ProfileDir "user.js"
$pref = 'user_pref("toolkit.legacyUserProfileCustomizations.stylesheets", true);'
$existing = if (Test-Path $userJs) { Get-Content $userJs } else { @() }
if ($existing -notcontains $pref) {
  Add-Content -Path $userJs -Encoding ascii -Value @("", "// Lets Firefox load chrome/userChrome.css and chrome/userContent.css.", $pref)
  Write-Host "Added the required line to user.js"
}

# CSS-only: create the theme switches so they show up in about:config ready to toggle.
# Firefox rewrites prefs.js when it closes, so this only works while it's closed.
if ($CssOnly) {
  $prefsJs = Join-Path $ProfileDir "prefs.js"
  if (Get-Process firefox -ErrorAction SilentlyContinue) {
    Write-Host "Firefox is running, so the theme switches weren't created. Close it and run this again, or create them in about:config yourself." -ForegroundColor Yellow
  } else {
    $have = if (Test-Path $prefsJs) { Get-Content $prefsJs } else { @() }
    $add = @()
    foreach ($name in "relics.active", "ame.active", "manga.active", "meridian.active",
                      "nocturne.freeze", "relics.freeze", "ame.freeze", "manga.freeze", "meridian.freeze") {
      if (-not ($have | Where-Object { $_ -like "user_pref(`"$name`",*" })) { $add += "user_pref(`"$name`", false);" }
    }
    if ($add.Count) {
      Add-Content -Path $prefsJs -Encoding ascii -Value $add
      Write-Host "Created $($add.Count) theme switch(es) in about:config"
    }
  }
}

Write-Host ""
Write-Host "Done. Start Firefox: Nocturne is the default theme." -ForegroundColor Green
if ($CssOnly) {
  Write-Host "To switch themes: open about:config, search for ame.active, relics.active, manga.active or meridian.active," -ForegroundColor Green
  Write-Host "and keep ONE of them true (all false = Nocturne). README.md has the full steps." -ForegroundColor Green
}
$loader = "C:\Program Files\Mozilla Firefox\theme-loader.cfg"
if (-not $CssOnly -and -not (Test-Path $loader)) {
  Write-Host "Optional: for the palette button, live switching, the Meridian clock and music, read" -ForegroundColor Yellow
  Write-Host "'Step 2' in README.md. It needs admin rights and has a security trade-off, so it's your call." -ForegroundColor Yellow
}
