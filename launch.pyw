"""
Hair Skin Plus — Prescription Desk Launcher
Runs silently (no console window) via pythonw.
Starts Flask server in background, waits for it to be ready,
then opens the app in Chrome/Edge --app mode (desktop app, no browser UI).
"""

import subprocess
import sys
import os
import time
import webbrowser
import urllib.request

APP_DIR  = os.path.dirname(os.path.abspath(__file__))
APP_PY   = os.path.join(APP_DIR, "app.py")
APP_URL  = "http://127.0.0.1:5050"
TIMEOUT  = 15   # seconds to wait for server startup

# ── Browser candidates (Chrome / Edge in app mode) ──────────────────────────
BROWSER_CANDIDATES = [
    # Google Chrome
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    # Microsoft Edge
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\Application\msedge.exe"),
]

def find_browser():
    """Return path to Chrome or Edge, or None if neither found."""
    for path in BROWSER_CANDIDATES:
        if os.path.isfile(path):
            return path
    return None

def open_app_window(url):
    """
    Open in Chrome/Edge --app mode: frameless window, no tabs, no address bar.
    Falls back to default browser if neither is available.
    """
    browser = find_browser()
    if browser:
        subprocess.Popen([
            browser,
            f"--app={url}",
            "--start-maximized",
            "--disable-extensions",
            "--no-default-browser-check",
        ])
    else:
        # Fallback: regular browser
        webbrowser.open_new(url)

def server_ready():
    """Poll until Flask responds or timeout."""
    deadline = time.time() + TIMEOUT
    while time.time() < deadline:
        try:
            urllib.request.urlopen(APP_URL, timeout=1)
            return True
        except Exception:
            time.sleep(0.4)
    return False

def start_flask():
    """Launch Flask as a hidden subprocess (no console window)."""
    python_exe = sys.executable.replace("pythonw.exe", "python.exe")
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = subprocess.SW_HIDE
    subprocess.Popen(
        [python_exe, APP_PY],
        cwd=APP_DIR,
        startupinfo=startupinfo,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )

def main():
    # If our server is already running on 5050, just open the window
    try:
        urllib.request.urlopen(APP_URL, timeout=1)
        open_app_window(APP_URL)
        return
    except Exception:
        pass

    # Start Flask server
    start_flask()

    # Wait for it to be ready, then open app window
    server_ready()
    open_app_window(APP_URL)

if __name__ == "__main__":
    main()
