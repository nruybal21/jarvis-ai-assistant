# PowerShell Profile - Microsoft.PowerShell_profile.ps1
# This file configures your beautiful AI assistant terminal

# Oh My Posh Theme (Paradox - Futuristic AI Look)
try {
    oh-my-posh init pwsh --config "$env:POSH_THEMES_PATH\paradox.omp.json" | Invoke-Expression
} catch {
    Write-Host "Oh My Posh theme not loaded - using default prompt" -ForegroundColor Yellow
}

# AI Assistant Project Path
$JarvisPath = "C:\Users\nicole.ruybal\Documents\jarvis-ai-assistant"

# AI Assistant Functions with Error Handling
function jarvis { 
    if (Test-Path $JarvisPath) {
        Push-Location $JarvisPath
        try {
            python src/basic_jarvis.py
        } catch {
            Write-Host "Error launching Jarvis: $($_.Exception.Message)" -ForegroundColor Red
        }
        Pop-Location
    } else {
        Write-Host "❌ Jarvis project not found at: $JarvisPath" -ForegroundColor Red
        Write-Host "💡 Navigate to your project folder and run: python src/basic_jarvis.py" -ForegroundColor Yellow
    }
}

function vjarvis { 
    if (Test-Path $JarvisPath) {
        Push-Location $JarvisPath
        try {
            python src/visual_jarvis.py
        } catch {
            Write-Host "Error launching Visual Jarvis: $($_.Exception.Message)" -ForegroundColor Red
        }
        Pop-Location
    } else {
        Write-Host "❌ Jarvis project not found at: $JarvisPath" -ForegroundColor Red
        Write-Host "💡 Navigate to your project folder and run: python src/visual_jarvis.py" -ForegroundColor Yellow
    }
}

function ejarvis { 
    if (Test-Path $JarvisPath) {
        Push-Location $JarvisPath
        try {
            python src/enhanced_jarvis.py
        } catch {
            Write-Host "Error launching Enhanced Jarvis: $($_.Exception.Message)" -ForegroundColor Red
        }
        Pop-Location
    } else {
        Write-Host "❌ Jarvis project not found at: $JarvisPath" -ForegroundColor Red
        Write-Host "💡 Navigate to your project folder and run: python src/enhanced_jarvis.py" -ForegroundColor Yellow
    }
}

# Quick navigation to Jarvis project
function cdjarvis {
    if (Test-Path $JarvisPath) {
        Set-Location $JarvisPath
        Write-Host "📂 Navigated to Jarvis AI Assistant project" -ForegroundColor Green
        ls
    } else {
        Write-Host "❌ Jarvis project not found at: $JarvisPath" -ForegroundColor Red
    }
}

# System status check
function jarvis-status {
    Write-Host ""
    Write-Host "🤖 JARVIS AI ASSISTANT STATUS CHECK" -ForegroundColor Cyan
    Write-Host "=" * 50 -ForegroundColor Cyan
    
    # Check Python
    try {
        $pythonVersion = python --version 2>&1
        Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
    } catch {
        Write-Host "❌ Python not found" -ForegroundColor Red
    }
    
    # Check project folder
    if (Test-Path $JarvisPath) {
        Write-Host "✅ Project folder: Found" -ForegroundColor Green
    } else {
        Write-Host "❌ Project folder: Not found" -ForegroundColor Red
    }
    
    # Check Git
    try {
        $gitVersion = git --version 2>&1
        Write-Host "✅ Git: $gitVersion" -ForegroundColor Green
    } catch {
        Write-Host "❌ Git not found" -ForegroundColor Red
    }
    
    # Check Oh My Posh
    try {
        $poshVersion = oh-my-posh --version 2>&1
        Write-Host "✅ Oh My Posh: $poshVersion" -ForegroundColor Green
    } catch {
        Write-Host "❌ Oh My Posh not found" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "💡 Commands available:" -ForegroundColor Yellow
    Write-Host "   jarvis      - Launch main AI assistant" -ForegroundColor White
    Write-Host "   vjarvis     - Launch visual AI assistant" -ForegroundColor White
    Write-Host "   ejarvis     - Launch enhanced AI assistant" -ForegroundColor White
    Write-Host "   cdjarvis    - Navigate to project folder" -ForegroundColor White
    Write-Host "   jarvis-status - Show this status check" -ForegroundColor White
    Write-Host ""
}

# Welcome Message
Write-Host ""
Write-Host "🤖 " -NoNewline -ForegroundColor Yellow
Write-Host "JARVIS AI ASSISTANT TERMINAL" -ForegroundColor Cyan
Write-Host "✨ Enhanced PowerShell Environment Ready" -ForegroundColor Green  
Write-Host ""
Write-Host "Quick Commands:" -ForegroundColor Yellow
Write-Host "  vjarvis  " -NoNewline -ForegroundColor White
Write-Host "→ Beautiful Visual Interface" -ForegroundColor Gray
Write-Host "  ejarvis  " -NoNewline -ForegroundColor White  
Write-Host "→ Enhanced AI with Memory" -ForegroundColor Gray
Write-Host "  jarvis   " -NoNewline -ForegroundColor White
Write-Host "→ Standard Interface" -ForegroundColor Gray
Write-Host ""
Write-Host "Type 'jarvis-status' for system check" -ForegroundColor Yellow
Write-Host "─" * 70 -ForegroundColor Cyan
Write-Host ""