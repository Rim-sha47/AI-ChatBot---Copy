'''sidebar.py - Premium collapsible sidebar with navigation icons and profile'''
import customtkinter as ctk
from typing import Callable

import notifications
from assets import AssetsManager

class Sidebar(ctk.CTkFrame):
    """Collapsible sidebar used by the main App.
    It displays a user profile section, navigation buttons with icons, and
    supports hover animations. The `nav_callback` is called with the page name
    (e.g., "dashboard", "chat", "notes", ...) when a button is pressed.
    """
    def __init__(self, master, nav_callback: Callable[[str], None], get_user_profile: Callable[[], str], accent_color: str = "#7f00ff"):
        super().__init__(master, width=200, corner_radius=0, fg_color="#0d0e15")
        self.nav_callback = nav_callback
        self.get_user_profile = get_user_profile
        self.accent_color = accent_color
        self._is_collapsed = False
        self._build_ui()

    def _build_ui(self):
        # Profile section (top)
        profile_frame = ctk.CTkFrame(self, fg_color="transparent")
        profile_frame.pack(fill="x", pady=(15, 10))
        # Load profile avatar (generated placeholder)
        avatar = AssetsManager.get_icon("profile", size=50)
        self.avatar_label = ctk.CTkLabel(profile_frame, image=avatar, text="")
        self.avatar_label.pack(pady=5)
        self.username_label = ctk.CTkLabel(profile_frame, text=self.get_user_profile(), font=ctk.CTkFont(size=14, weight="bold"), text_color="#e0e0e0")
        self.username_label.pack()

        # Separator
        ctk.CTkLabel(self, text="", height=2, fg_color="#333333").pack(fill="x", padx=10, pady=10)

        # Navigation buttons
        self.buttons = {}
        nav_items = [
            ("dashboard", "Dashboard"),
            ("chat", "Chatbot"),
            ("notes", "Notes"),
            ("todo", "To‑Do List"),
            ("qr", "QR Generator"),
            ("pwd", "Password Generator"),
            ("settings", "Settings"),
            ("about", "About"),
        ]
        for key, label in nav_items:
            btn = ctk.CTkButton(
                self,
                text=label,
                image=AssetsManager.get_icon(key, size=30),
                compound="left",
                anchor="w",
                width=180,
                corner_radius=8,
                fg_color="#1e1e1e",
                hover_color="#2a2a2a",
                text_color="#e0e0e0",
                font=ctk.CTkFont(size=13),
                command=lambda n=key: self._on_nav(n),
            )
            btn.pack(pady=3, padx=10, fill="x")
            self.buttons[key] = btn

        # Collapse toggle at bottom
        self.toggle_btn = ctk.CTkButton(
            self,
            text="<<",
            width=40,
            corner_radius=8,
            fg_color="#1e1e1e",
            hover_color="#2a2a2a",
            command=self.toggle,
        )
        self.toggle_btn.place(relx=0.5, rely=0.98, anchor="s")

    def _on_nav(self, name: str):
        # Highlight active button
        for key, btn in self.buttons.items():
            if key == name:
                btn.configure(fg_color=self.accent_color)
            else:
                btn.configure(fg_color="#1e1e1e")
        self.nav_callback(name)
        notifications.toast(f"Opening {name.capitalize()} page")

    def refresh_profile(self, new_username: str):
        self.username_label.configure(text=new_username)
        notifications.toast("Profile updated")

    def refresh_accent(self, new_color: str):
        self.accent_color = new_color
        # Update active button colour if any
        for key, btn in self.buttons.items():
            if btn.cget("fg_color") == self.accent_color:
                btn.configure(fg_color=new_color)
        # Regenerate icons with new accent
        for key in self.buttons:
            self.buttons[key].configure(image=AssetsManager.get_icon(key, size=30))

    def toggle(self):
        """Collapse or expand the sidebar with a smooth width animation."""
        target_width = 60 if not self._is_collapsed else 200
        step = -10 if not self._is_collapsed else 10
        def animate(width):
            self.configure(width=width)
            self.update_idletasks()
        for w in range(self.winfo_width(), target_width + step, step):
            animate(w)
        self._is_collapsed = not self._is_collapsed
        # Adjust button text visibility when collapsed
        for btn in self.buttons.values():
            btn.configure(text="" if self._is_collapsed else btn.cget("text"))
        self.toggle_btn.configure(text=">>" if self._is_collapsed else "<<")
