'''theme.py - Centralized theme definitions for HireBot AI Assistant'''

# Color palette (dark theme with blue-purple gradient)
GRADIENT_START = "#1e3c72"  # dark blue
GRADIENT_END = "#2a5298"    # lighter blue
ACCENT_PURPLE = "#6a1b9a"
BACKGROUND = "#121212"
SURFACE = "#1e1e1e"
TEXT_PRIMARY = "#e0e0e0"
TEXT_SECONDARY = "#b0b0b0"
BORDER_COLOR = "#333333"

# Utility function to apply theme to a CTk widget
def apply_theme(widget):
    """Apply dark theme colors to the given CTk widget and its children."""
    try:
        widget.configure(fg_color=SURFACE, text_color=TEXT_PRIMARY, border_color=BORDER_COLOR)
    except Exception:
        pass
    for child in widget.winfo_children():
        apply_theme(child)

# Gradient background for frames (requires custom drawing, simplified here)
def set_gradient_bg(frame, start=GRADIENT_START, end=GRADIENT_END):
    """Set a gradient background for a CTkFrame using a canvas overlay.
    Note: CustomTkinter does not support gradients natively; this function
    creates a canvas that draws a gradient image placeholder.
    """
    import customtkinter as ctk
    try:
        canvas = ctk.CTkCanvas(frame, highlightthickness=0)
        canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        # In a full implementation, generate a gradient image and set as background.
    except Exception:
        pass
