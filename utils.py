'''utils.py - common helper functions for HireBot AI Assistant'''
import os
import json
import datetime
import tkinter as tk
from tkinter import messagebox
import pyperclip

def load_json(path: str, default=None):
    """Load JSON from *path* safely, returning *default* on failure."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def save_json(path: str, data) -> bool:
    """Write *data* as JSON to *path* (creates directories if needed)."""
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        messagebox.showerror("File Save Error", str(e))
        return False

def format_timestamp(dt: datetime.datetime = None) -> str:
    """Return a human‑readable timestamp like '14:35 • Sep 21'."""
    if dt is None:
        dt = datetime.datetime.now()
    return dt.strftime("%H:%M • %b %d")

def copy_to_clipboard(text: str):
    """Copy *text* to the system clipboard using pyperclip (fallback to tkinter)."""
    try:
        pyperclip.copy(text)
    except Exception:
        # fallback for environments without pyperclip
        root = tk.Tk()
        root.withdraw()
        root.clipboard_clear()
        root.clipboard_append(text)
        root.update()
        root.destroy()

def resource_path(relative_path: str) -> str:
    """Return absolute path for bundled resources (works for PyInstaller)."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
