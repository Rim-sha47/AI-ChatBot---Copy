'''assets.py - Helper for loading image assets and managing generated icons'''
import os
from pathlib import Path
import customtkinter as ctk
from PIL import Image, ImageDraw, ImageTk

# Base assets directory (relative to this file)
ASSETS_DIR = Path(__file__).parent / "assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

def load_image(name, size=None):
    """Load an image from the assets folder.
    Args:
        name (str): Filename of the image (e.g., 'logo.png').
        size (int | tuple[int, int] | None): Desired size. If None, original size is used.
    Returns:
        ctk.CTkImage: Image usable in CustomTkinter widgets.
    """
    path = ASSETS_DIR / name
    if not path.is_file():
        raise FileNotFoundError(f"Asset not found: {path}")
    img = Image.open(path)
    if size:
        if isinstance(size, (int, float)):
            size = (int(size), int(size))
        img = img.resize(size, Image.Resampling.LANCZOS)
        return ctk.CTkImage(light_image=img, dark_image=img, size=size)
    return ctk.CTkImage(light_image=img, dark_image=img)

class AssetsManager:
    """Generate simple placeholder icons based on accent color.
    In a production app you would replace these with proper SVG/icon assets.
    """
    ICON_NAMES = [
        "dashboard",
        "chat",
        "notes",
        "todo",
        "qr",
        "pwd",
        "settings",
        "about",
        "profile",
    ]

    @staticmethod
    def _icon_path(name, color_hex):
        """Return the file path for a generated icon.
        The filename incorporates the color to allow regeneration when accent changes.
        """
        sanitized = color_hex.lstrip("#")
        return ASSETS_DIR / f"{name}_{sanitized}.png"

    @staticmethod
    def generate_icon(name: str, color_hex: str, size: int = 40):
        """Create a circular icon of *size* px with the given *color_hex*.
        Overwrites any existing file with the same name.
        """
        path = AssetsManager._icon_path(name, color_hex)
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        # Draw a filled circle with the accent color
        draw.ellipse([0, 0, size - 1, size - 1], fill=color_hex)
        img.save(path)
        return path

    @staticmethod
    def generate_all_assets(accent_color: str):
        """Generate icons for all UI elements using the current accent color.
        This is called at startup and whenever the user changes the theme accent.
        """
        for name in AssetsManager.ICON_NAMES:
            AssetsManager.generate_icon(name, accent_color)

    @staticmethod
    def get_icon(name: str, size=None):
        """Convenient wrapper to load a generated icon.
        *size* can be an int for square dimensions.
        """
        # Determine the most recent file for the given name (ignore color in filename)
        matching = list(ASSETS_DIR.glob(f"{name}_*.png"))
        if not matching:
            raise FileNotFoundError(f"No generated icon found for {name}")
        # Use the latest file (by modification time)
        latest = max(matching, key=lambda p: p.stat().st_mtime)
        return load_image(latest.name, size)
