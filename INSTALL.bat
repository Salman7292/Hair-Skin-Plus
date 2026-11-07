@echo off
title Hair Skin Plus — Installer
color 0A
echo.
echo  ============================================
echo    Hair Skin Plus - Prescription System
echo    Installer for Dr. Seyab Ur Rahman
echo  ============================================
echo.

:: ── Step 1: Check Python is installed ────────────────────────────────────────
echo [1/4] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo  ERROR: Python is not installed!
    echo.
    echo  Please install Python 3.10 or newer from:
    echo  https://www.python.org/downloads/
    echo.
    echo  IMPORTANT: During install, tick "Add Python to PATH"
    echo.
    pause
    exit /b 1
)
echo        Python found. OK.

:: ── Step 2: Install Flask ─────────────────────────────────────────────────────
echo.
echo [2/4] Installing Flask (this may take a moment)...
pip install -r "%~dp0requirements.txt" --quiet
if errorlevel 1 (
    echo  ERROR: Failed to install Flask. Check your internet connection.
    pause
    exit /b 1
)
echo        Flask installed. OK.

:: ── Step 3: Create desktop shortcut ──────────────────────────────────────────
echo.
echo [3/4] Creating desktop shortcut...

:: Find pythonw.exe automatically
for /f "delims=" %%i in ('where pythonw 2^>nul') do set PYTHONW=%%i
if "%PYTHONW%"=="" (
    :: fallback: look next to python.exe
    for /f "delims=" %%i in ('where python 2^>nul') do set PYTHONW=%%~dpi\pythonw.exe
)

:: App directory = folder this install.bat is in
set APP_DIR=%~dp0
:: Remove trailing backslash
if "%APP_DIR:~-1%"=="\" set APP_DIR=%APP_DIR:~0,-1%

set LAUNCH_PY=%APP_DIR%\launch.pyw
set ICON=%APP_DIR%\static\app_icon.ico
set DESKTOP=%USERPROFILE%\Desktop
set SHORTCUT=%DESKTOP%\Hair Skin Plus Rx.lnk

:: Write a small VBScript to create the shortcut
set VBS=%TEMP%\make_shortcut.vbs
(
echo Set oWS = WScript.CreateObject("WScript.Shell"^)
echo sLinkFile = "%SHORTCUT%"
echo Set oLink = oWS.CreateShortcut(sLinkFile^)
echo oLink.TargetPath = "%PYTHONW%"
echo oLink.Arguments = """%LAUNCH_PY%"""
echo oLink.WorkingDirectory = "%APP_DIR%"
echo oLink.IconLocation = "%ICON%"
echo oLink.Description = "Hair Skin Plus Prescription Desk"
echo oLink.WindowStyle = 1
echo oLink.Save
) > "%VBS%"
cscript //nologo "%VBS%"
del "%VBS%"

if exist "%SHORTCUT%" (
    echo        Desktop shortcut created. OK.
) else (
    echo  WARNING: Shortcut could not be created. You can still run launch.pyw manually.
)

:: ── Step 4: First launch ──────────────────────────────────────────────────────
echo.
echo [4/4] Launching Hair Skin Plus...
echo.
echo  ============================================
echo    Installation complete!
echo    The app will open as a desktop window.
echo.
echo    Next time: just double-click the
echo    "Hair Skin Plus Rx" icon on your Desktop.
echo  ============================================
echo.
start "" "%PYTHONW%" "%LAUNCH_PY%"

timeout /t 3 >nul
exit
