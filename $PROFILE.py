# Oh My Posh Paradox Theme
oh-my-posh init pwsh --config "$env:POSH_THEMES_PATH\paradox.omp.json" | Invoke-Expression

# AI Assistant Functions
function jarvis { 
    if (Test-Path "C:\Users\nicole.ruybal\Documents\jarvis-ai-assistant") {
        Set-Location "C:\Users\nicole.ruybal\Documents\jarvis-ai-assistant"
        python src/basic_jarvis.py 
    } else {
        Write-Host "Jarvis project not found! Navigate to your project folder first." -ForegroundColor Red
    }
}

function vjarvis { 
    if (Test-Path "C:\Users\nicole.ruybal\Documents\jarvis-ai-assistant") {
        Set-Location "C:\Users\nicole.ruybal\Documents\jarvis-ai-assistant"
        python src/visual_jarvis.py 
    } else {
        Write-Host "Jarvis project not found! Navigate to your project folder first." -ForegroundColor Red
    }
}

function ejarvis { 
    if (Test-Path "C:\Users\nicole.ruybal\Documents\jarvis-ai-assistant") {
        Set-Location "C:\Users\nicole.ruybal\Documents\jarvis-ai-assistant"
        python src/enhanced_jarvis.py 
    } else {
        Write-Host "Jarvis project not found! Navigate to your project folder first." -ForegroundColor Red
    }
}

# Welcome Message
Write-Host ""
Write-Host "🤖 JARVIS AI ASSISTANT TERMINAL" -ForegroundColor Cyan
Write-Host "✨ Oh My Posh Paradox theme active" -ForegroundColor Green  
Write-Host "Type 'vjarvis' for Visual Interface | 'jarvis' for Standard | 'ejarvis' for Enhanced" -ForegroundColor Yellow
Write-Host "─" * 80 -ForegroundColor Cyan
Write-Host ""