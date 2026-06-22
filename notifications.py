'''notifications.py - Simple toast notification system'''
import customtkinter as ctk

# Global reference to the root window (set from main.py)
_ROOT = None

def set_root(root):
    """Initialize the root window reference for notifications."""
    global _ROOT
    _ROOT = root
_ROOT = None

def show_success(*_, msg: str):
    """Compatibility wrapper for legacy calls. Shows a toast with a success style (same as toast)."""
    toast(msg)

def show_error(*_, msg: str):
    """Compatibility wrapper for legacy calls. Shows a toast with an error style (same as toast)."""
    toast(msg)

def show_warning(*_, msg: str):
    """Compatibility wrapper for legacy calls. Shows a toast with a warning style (same as toast)."""
    toast(msg)


def toast(message: str, duration: int = 3000):
    """Display a temporary toast message.
    Args:
        message: Text to display.
        duration: Milliseconds the toast stays visible.
    """
    if _ROOT is None:
        raise RuntimeError("Root window not set for notifications. Call set_root(root) first.")
    # Create toast window
    toast_win = ctk.CTkToplevel(_ROOT)
    toast_win.overrideredirect(True)
    toast_win.configure(fg_color="#333333")
    label = ctk.CTkLabel(toast_win, text=message, text_color="#f0f0f0", font=("Segoe UI", 12))
    label.pack(padx=10, pady=5)
    # Position at bottom-right of the root window
    _ROOT.update_idletasks()
    x = _ROOT.winfo_x() + _ROOT.winfo_width() - toast_win.winfo_reqwidth() - 20
    y = _ROOT.winfo_y() + _ROOT.winfo_height() - toast_win.winfo_reqheight() - 20
    toast_win.geometry(f"+{x}+{y}")
    # Auto-destroy after duration
    toast_win.after(duration, toast_win.destroy)
