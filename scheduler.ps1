# CaciqueAnalytics Scheduler Wrapper
# This script is invoked by Windows Task Scheduler to run the automation pipeline.
#
# Setup:
#   1. Open Task Scheduler
#   2. Create Basic Task -> Name: "CaciqueAnalytics Automation"
#   3. Trigger: Daily, repeat every 15 minutes
#   4. Action: Start a program
#   5. Program: powershell.exe
#   6. Arguments: -ExecutionPolicy Bypass -File "C:\Users\PC\Projects\CaciqueAnalytics\scheduler.ps1"
#
# For match days (more frequent checks):
#   Create a second task that runs every 15 minutes during match hours (e.g., 12:00-23:00)

$ProjectPath = "C:\Users\PC\Projects\CaciqueAnalytics"
$PythonExe = "py"
$PythonArgs = "-3.12", "$ProjectPath\src\automation\scheduler.py"

# Optional: Add --dry-run for testing
# $PythonArgs += "--dry-run"

# Optional: Filter by specific competition/season
# $PythonArgs += "--competition", "1"
# $PythonArgs += "--season", "1"

Set-Location -LiteralPath $ProjectPath

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Write-Output "[$timestamp] Starting CaciqueAnalytics automation cycle"

# Ensure PostgreSQL is running
$pgService = Get-Service -Name "postgresql-x64-18" -ErrorAction SilentlyContinue
if ($pgService -and $pgService.Status -ne "Running") {
    Write-Output "Starting PostgreSQL service..."
    try {
        Start-Service -Name "postgresql-x64-18"
        Start-Sleep -Seconds 3
    } catch {
        Write-Output "Could not start PostgreSQL service. Trying pg_ctl..."
        & "C:\Program Files\PostgreSQL\18\bin\pg_ctl.exe" start -D "C:\Program Files\PostgreSQL\18\data" -l "C:\Program Files\PostgreSQL\18\log\postgresql.log"
        Start-Sleep -Seconds 5
    }
}

# Run the automation cycle
& $PythonExe @PythonArgs

$exitCode = $LASTEXITCODE
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

if ($exitCode -eq 0) {
    Write-Output "[$timestamp] Automation cycle completed successfully"
} else {
    Write-Output "[$timestamp] Automation cycle failed with exit code $exitCode"
}

exit $exitCode
