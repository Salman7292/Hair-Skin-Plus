@echo off
title Hair Skin Plus — Build Installer
color 0A
echo.
echo  ╔══════════════════════════════════════════════════╗
echo  ║   Hair Skin Plus — Desktop Installer Builder    ║
echo  ║   Dr. Seyab Ur Rahman · Dermatology Clinic      ║
echo  ╚══════════════════════════════════════════════════╝
echo.

set PYTHON=C:\ProgramData\anaconda3\python.exe
set PYI=C:\Users\%USERNAME%\AppData\Roaming\Python\Python312\Scripts\pyinstaller.exe
set ISCC="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
set ISCC64="C:\Program Files\Inno Setup 6\ISCC.exe"

REM ── 1. Check Python ─────────────────────────────────────────────────────────
echo [1/4] Checking Python...
"%PYTHON%" --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found at %PYTHON%
    echo Please install Anaconda or update PYTHON path in this script.
    pause & exit /b 1
)
echo       OK — Python found.
echo.

REM ── 2. Install / upgrade dependencies ───────────────────────────────────────
echo [2/4] Installing dependencies...
"%PYTHON%" -m pip install -r requirements.txt --quiet
"%PYTHON%" -m pip install pyinstaller --quiet
echo       OK — Dependencies ready.
echo.

REM ── 3. Run PyInstaller ──────────────────────────────────────────────────────
echo [3/4] Building executable with PyInstaller...
echo       This takes 2-5 minutes. Please wait...
echo.
if exist "%PYI%" (
    "%PYI%" HairSkinPlus.spec --noconfirm
) else (
    "%PYTHON%" -m PyInstaller HairSkinPlus.spec --noconfirm
)
if errorlevel 1 (
    echo ERROR: PyInstaller build failed. See output above.
    pause & exit /b 1
)
echo.
echo       OK — dist\HairSkinPlus\ created.
echo.

REM ── 4. Run Inno Setup Compiler ──────────────────────────────────────────────
echo [4/4] Building Windows installer with Inno Setup...
set ISCC_FOUND=0

if exist %ISCC% (
    %ISCC% installer.iss
    set ISCC_FOUND=1
)
if exist %ISCC64% (
    %ISCC64% installer.iss
    set ISCC_FOUND=1
)

if "%ISCC_FOUND%"=="0" (
    echo.
    echo  ┌─────────────────────────────────────────────────────────┐
    echo  │  Inno Setup not found — skipping .exe installer build.  │
    echo  │                                                         │
    echo  │  To create the installer:                               │
    echo  │   1. Download Inno Setup 6 (free):                      │
    echo  │      https://jrsoftware.org/isdl.php                    │
    echo  │   2. Install it, then re-run this script.               │
    echo  │                                                         │
    echo  │  Alternatively, you can distribute the folder:          │
    echo  │      dist\HairSkinPlus\                                 │
    echo  │  (zip it up and share — users double-click              │
    echo  │   HairSkinPlus.exe inside to run the app)               │
    echo  └─────────────────────────────────────────────────────────┘
    echo.
    goto :done
)

if errorlevel 1 (
    echo ERROR: Inno Setup compilation failed. See output above.
    pause & exit /b 1
)

echo.
echo  ╔══════════════════════════════════════════════════╗
echo  ║   BUILD COMPLETE!                               ║
echo  ║   Installer: Output\HairSkinPlus-Setup.exe      ║
echo  ║                                                 ║
echo  ║   Share HairSkinPlus-Setup.exe with users.     ║
echo  ║   They just double-click it — no Python needed! ║
echo  ╚══════════════════════════════════════════════════╝

:done
echo.
pause

