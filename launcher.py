"""
Hair Skin Plus — Desktop Launcher
Bundles Flask app into a click-to-run Windows executable.
PyInstaller entry point: launcher.py
"""
import os
import sys
import time
import socket
import threading
import subprocess
import webbrowser
import tkinter as tk
from tkinter import messagebox

# ── Resolve base directory (works both from source and PyInstaller bundle) ──
if getattr(sys, 'frozen', False):
    # Running as PyInstaller .exe — _MEIPASS holds extracted bundle
    BASE_DIR = sys._MEIPASS
    # Data files (db, templates, static) live next to the .exe
    APP_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    APP_DIR = BASE_DIR

PORT = 5050
URL  = f"http://127.0.0.1:{PORT}"

# ── Patch sys.path so app.py finds its modules ──────────────────────────────
sys.path.insert(0, BASE_DIR)
os.chdir(APP_DIR)   # CWD = folder with medicines.db / templates / static


def is_port_free(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) != 0


def wait_for_server(port, timeout=20):
    """Poll until Flask is accepting connections."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection(('127.0.0.1', port), timeout=1):
                return True
        except OSError:
            time.sleep(0.3)
    return False


def run_flask():
    """Start Flask in a background thread (no console window)."""
    # Import and run app.py inside this process
    import importlib.util
    spec = importlib.util.spec_from_file_location("app", os.path.join(BASE_DIR, "app.py"))
    app_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(app_module)
    # app.run() is called at module level if __name__ == '__main__',
    # but since we're importing, we call it explicitly:
    app_module.app.run(host='127.0.0.1', port=PORT, debug=False, use_reloader=False)


def show_splash():
    """Show a small splash window while Flask starts."""
    splash = tk.Tk()
    splash.title("Hair Skin Plus")
    splash.geometry("400x180")
    splash.resizable(False, False)
    splash.configure(bg="#0b5650")
    # Center on screen
    splash.update_idletasks()
    w = splash.winfo_screenwidth()
    h = splash.winfo_screenheight()
    x = (w - 400) // 2
    y = (h - 180) // 2
    splash.geometry(f"400x180+{x}+{y}")
    splash.overrideredirect(True)   # borderless

    tk.Label(splash, text="Hair Skin Plus", font=("Segoe UI", 22, "bold"),
             bg="#0b5650", fg="#e0a030").pack(pady=(30, 4))
    tk.Label(splash, text="Dermatology Clinic — Starting…", font=("Segoe UI", 11),
             bg="#0b5650", fg="#d7ebe8").pack()
    tk.Label(splash, text="Dr. Seyab Ur Rahman · Peshawar", font=("Segoe UI", 9),
             bg="#0b5650", fg="#8eccc6").pack(pady=(4, 0))

    progress_var = tk.StringVar(value="Initializing…")
    tk.Label(splash, textvariable=progress_var, font=("Segoe UI", 9),
             bg="#0b5650", fg="#aad8d3").pack(pady=(10, 0))

    def launch():
        progress_var.set("Starting Flask server…")
        splash.update()
        t = threading.Thread(target=run_flask, daemon=True)
        t.start()
        progress_var.set("Waiting for server…")
        splash.update()
        if wait_for_server(PORT, timeout=25):
            progress_var.set("Opening browser…")
            splash.update()
            time.sleep(0.3)
            webbrowser.open(URL)
            splash.destroy()
        else:
            splash.destroy()
            messagebox.showerror(
                "Hair Skin Plus",
                f"Could not start the server on port {PORT}.\n"
                "Please check that no other app is using that port."
            )

    splash.after(200, launch)
    splash.mainloop()


def main():
    if not is_port_free(PORT):
        # Already running — just open the browser
        webbrowser.open(URL)
        return
    show_splash()


if __name__ == "__main__":
    main()

