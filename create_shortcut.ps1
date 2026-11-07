# Hair Skin Plus — Desktop Shortcut Creator
# Works on ANY machine regardless of where the folder is placed.
# Run once from the project folder with:
#   powershell -ExecutionPolicy Bypass -File create_shortcut.ps1

$AppDir      = Split-Path -Parent $MyInvocation.MyCommand.Path
$LaunchPyw   = Join-Path $AppDir 'launch.pyw'
$IconPath    = Join-Path $AppDir 'static\app_icon.ico'

# Find pythonw.exe automatically
$PythonW = (Get-Command pythonw -ErrorAction SilentlyContinue).Source
if (-not $PythonW) {
    $Python = (Get-Command python -ErrorAction SilentlyContinue).Source
    if ($Python) {
        $PythonW = Join-Path (Split-Path $Python) 'pythonw.exe'
    }
}
if (-not $PythonW -or -not (Test-Path $PythonW)) {
    Write-Host "ERROR: pythonw.exe not found. Make sure Python is installed and on PATH." -ForegroundColor Red
    exit 1
}

$Desktop      = [System.Environment]::GetFolderPath('Desktop')
$ShortcutPath = Join-Path $Desktop 'Hair Skin Plus Rx.lnk'

$WScriptShell               = New-Object -ComObject WScript.Shell
$Shortcut                   = $WScriptShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath        = $PythonW
$Shortcut.Arguments         = "`"$LaunchPyw`""
$Shortcut.WorkingDirectory  = $AppDir
$Shortcut.IconLocation      = $IconPath
$Shortcut.Description       = 'Hair Skin Plus Prescription Desk'
$Shortcut.WindowStyle       = 1
$Shortcut.Save()

if (Test-Path $ShortcutPath) {
    Write-Host "SUCCESS: Shortcut created at: $ShortcutPath" -ForegroundColor Green
} else {
    Write-Host "ERROR: Shortcut was not created." -ForegroundColor Red
}
