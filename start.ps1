# start.ps1
try {
    Write-Host "Activating virtual environment..." -ForegroundColor Cyan
    .\venv\Scripts\Activate.ps1
    
    Write-Host "`nCentaurus-See-Music Launcher" -ForegroundColor Cyan
    Write-Host "1. Single Piano Visualizer" -ForegroundColor Yellow
    Write-Host "2. Single Guitar Fretboard Visualizer" -ForegroundColor Yellow
    Write-Host "3. Two Piano Visualizers (Local + Remote)" -ForegroundColor Yellow
    Write-Host "4. Two Guitar Visualizers (Local + Remote)" -ForegroundColor Yellow
    Write-Host "5. Piano + Guitar Combo (Guitar Remote)" -ForegroundColor Green
    Write-Host "Choose option (1-5) or wait 5 seconds for auto-start:" -ForegroundColor Green

    # Start timeout counter
    $timeoutSeconds = 5
    $choice = $null
    $startTime = Get-Date

    while (((Get-Date) - $startTime).TotalSeconds -lt $timeoutSeconds) {
        if ([Console]::KeyAvailable) {
            $key = [Console]::ReadKey($true)
            if ($key.KeyChar -match '[1-5]') {
                $choice = $key.KeyChar
                break
            }
        }
        Start-Sleep -Milliseconds 100
        
        # Show countdown
        $remainingTime = [Math]::Ceiling($timeoutSeconds - ((Get-Date) - $startTime).TotalSeconds)
        Write-Host "`rAuto-starting in $remainingTime seconds... " -NoNewline -ForegroundColor Yellow
    }
    Write-Host "" # New line after countdown

    # If no choice made, default to option 5
    if (-not $choice) {
        $choice = "5"
        Write-Host "No selection made, starting Piano + Guitar Combo..." -ForegroundColor Green
    }

    switch ($choice) {
        "1" { 
            Write-Host "`nStarting Piano Visualizer..." -ForegroundColor Green
            python -m src.visualizers.test_visualizer 
        }
        "2" { 
            Write-Host "`nStarting Guitar Fretboard Visualizer..." -ForegroundColor Green
            python -m src.visualizers.guitar_visualizer
        }
        "3" { 
            Write-Host "`nStarting Two Piano Visualizers..." -ForegroundColor Green
            Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\venv\Scripts\Activate.ps1; python -m src.visualizers.test_visualizer"
            Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\venv\Scripts\Activate.ps1; python -m src.visualizers.test_visualizer"
            Write-Host "Press 't' in the second window to switch to REMOTE mode" -ForegroundColor Yellow
        }
        "4" { 
            Write-Host "`nStarting Two Guitar Visualizers..." -ForegroundColor Green
            Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\venv\Scripts\Activate.ps1; python -m src.visualizers.guitar_visualizer"
            Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\venv\Scripts\Activate.ps1; python -m src.visualizers.guitar_visualizer"
            Write-Host "Press 't' in the second window to switch to REMOTE mode" -ForegroundColor Yellow
        }
        "5" { 
            Write-Host "`nStarting Piano + Guitar Combo..." -ForegroundColor Green
            Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\venv\Scripts\Activate.ps1; python -m src.visualizers.test_visualizer"
            Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\venv\Scripts\Activate.ps1; python -m src.visualizers.guitar_visualizer"
            Write-Host "Press 't' in the Guitar window to switch to REMOTE mode" -ForegroundColor Yellow
        }
        default { Write-Host "`nInvalid choice" -ForegroundColor Red }
    }
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host "You may need to run: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Yellow
}