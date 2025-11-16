# Waterworks - One-Line Installer for Windows PowerShell
# Usage: irm https://raw.githubusercontent.com/amanzav/waterworks/main/install.ps1 | iex

Write-Host "💧 Waterworks - Easy Installer" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python (\d+)\.(\d+)") {
        $major = [int]$Matches[1]
        $minor = [int]$Matches[2]
    } else {
        throw "Could not parse Python version"
    }
    
    if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 9)) {
        Write-Host "❌ Python $major.$minor found, but Python 3.9+ is required" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✅ Found $pythonVersion" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "❌ Python is not installed." -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Python 3.9 or higher from:"
    Write-Host "  https://www.python.org/downloads/"
    exit 1
}

# Set installation directory
$defaultInstallDir = "$env:USERPROFILE\waterworks"
$installDir = Read-Host "Install to [$defaultInstallDir]"
if ([string]::IsNullOrWhiteSpace($installDir)) {
    $installDir = $defaultInstallDir
}

Write-Host ""
Write-Host "📦 Installing to: $installDir" -ForegroundColor Yellow
Write-Host ""

# Create directory
New-Item -ItemType Directory -Force -Path $installDir | Out-Null
Set-Location $installDir

# Download files
Write-Host "⬇️  Downloading Waterworks files..." -ForegroundColor Yellow

$baseUrl = "https://raw.githubusercontent.com/amanzav/waterworks/main"

# Download main files
$files = @{
    "requirements.txt" = "requirements.txt"
    "main.py" = "main.py"
    "setup.py" = "setup.py"
}

foreach ($file in $files.GetEnumerator()) {
    Invoke-WebRequest -Uri "$baseUrl/$($file.Key)" -OutFile $file.Value -UseBasicParsing
}

# Download modules
New-Item -ItemType Directory -Force -Path "modules" | Out-Null

$modules = @(
    "__init__.py",
    "auth.py",
    "config_manager.py",
    "cover_letter_generator.py",
    "folder_navigator.py",
    "job_extractor.py",
    "pdf_builder.py",
    "utils.py"
)

foreach ($module in $modules) {
    Invoke-WebRequest -Uri "$baseUrl/modules/$module" -OutFile "modules\$module" -UseBasicParsing
}

Write-Host "✅ Files downloaded" -ForegroundColor Green
Write-Host ""

# Create virtual environment
Write-Host "🔧 Setting up virtual environment..." -ForegroundColor Yellow
python -m venv venv

# Activate virtual environment
& ".\venv\Scripts\Activate.ps1"

# Upgrade pip
python -m pip install --upgrade pip --quiet

# Install dependencies
Write-Host "📥 Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet

Write-Host "✅ Dependencies installed" -ForegroundColor Green
Write-Host ""

# Check for Microsoft Word
$wordInstalled = Test-Path "HKLM:\SOFTWARE\Classes\Word.Application"
if (-not $wordInstalled) {
    Write-Host "⚠️  Microsoft Word not found" -ForegroundColor Yellow
    Write-Host "   PDF conversion will create DOCX files that you can manually convert"
    Write-Host ""
}

# Create launcher script
$launcherContent = @"
@echo off
call "%~dp0venv\Scripts\activate.bat"
python "%~dp0main.py" %*
"@

Set-Content -Path "waterworks.bat" -Value $launcherContent

# Add to PATH
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($userPath -notlike "*$installDir*") {
    [Environment]::SetEnvironmentVariable(
        "Path",
        "$userPath;$installDir",
        "User"
    )
    Write-Host "✅ Added to PATH" -ForegroundColor Green
}

Write-Host ""
Write-Host "==============================" -ForegroundColor Cyan
Write-Host "✅ Installation Complete!" -ForegroundColor Green
Write-Host "==============================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Restart your terminal"
Write-Host "  2. Run: waterworks config --show"
Write-Host ""
Write-Host "If config not found:"
Write-Host "  1. Run setup: cd $installDir; .\venv\Scripts\Activate.ps1; python setup.py"
Write-Host "  2. Then: waterworks generate --folder <folder_name>"
Write-Host ""
Write-Host "Documentation: https://github.com/amanzav/waterworks"
Write-Host ""
