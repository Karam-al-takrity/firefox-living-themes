# Adds the theme loader (Firefox autoconfig) to the Firefox install folder.
# Run from an ADMIN PowerShell. It copies exactly two files and changes nothing else:
#   <Firefox>\theme-loader.cfg
#   <Firefox>\defaults\pref\autoconfig.js
# To remove the loader later, delete those two files.
param([string]$FirefoxDir = "C:\Program Files\Mozilla Firefox")
$ErrorActionPreference = "Stop"
if (-not (Test-Path (Join-Path $FirefoxDir "firefox.exe"))) { throw "firefox.exe not found in $FirefoxDir" }
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Copy-Item (Join-Path $here "theme-loader.cfg") (Join-Path $FirefoxDir "theme-loader.cfg") -Force
Copy-Item (Join-Path $here "defaults\pref\autoconfig.js") (Join-Path $FirefoxDir "defaults\pref\autoconfig.js") -Force
Write-Host "Theme loader installed in $FirefoxDir. Restart Firefox."
