'''main.py - Entry point for HireBot AI Assistant with dynamic frame switching'''
import customtkinter as ctk
import datetime
import time
from PIL import Image
import os
import sys
import traceback
from tkinter import messagebox

# Import UI components
from auth import AuthFrame
from dashboard import DashboardFrame
from chatbot import ChatbotFrame
from notes import NotesFrame
from todo import TodoFrame
from qr_generator import QRGeneratorFrame
from password_generator import PasswordGeneratorFrame
from settings import SettingsFrame
from about import AboutFrame

# Core utilities
from assets import AssetsManager
import notifications

# Sidebar component (moved to separate module)
from sidebar import Sidebar

# Global theme initialization (dark mode, accent handled elsewhere)
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        notifications.set_root(self)
        self.title("HireBot AI Assistant Workspace")
        self.geometry("1100x700")
        self.minsize(950, 600)

        # User/session state
        self.current_user_id = None
        self.current_username = None
        self.current_accent_color = "#7f00ff"  # default purple accent
        self.active_frame = None  # reference to currently visible page

        # Ensure icons are generated before UI builds
        AssetsManager.generate_all_assets(self.current_accent_color)

        # Show splash screen then auth screen
        self.show_splash_screen()

    # ---------------------------------------------------------------------
    # Splash & Auth handling
    # ---------------------------------------------------------------------
    def show_splash_screen(self):
        splash = ctk.CTkFrame(self, fg_color="#0d0e15")
        splash.grid(row=0, column=0, columnspan=2, sticky="nsew")
        logo_img = ctk.CTkImage(
            light_image=Image.open("assets/logo.png"),
            dark_image=Image.open("assets/logo.png"),
            size=(100, 100)
        )
        ctk.CTkLabel(splash, image=logo_img, text="").place(relx=0.5, rely=0.35, anchor="center")
        ctk.CTkLabel(
            splash,
            text="HireBot Assistant",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="#ffffff",
        ).place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(
            splash,
            text="Loading premium AI workspace...",
            font=ctk.CTkFont(size=14),
            text_color="#8b8c9d",
        ).place(relx=0.5, rely=0.56, anchor="center")
        prog = ctk.CTkProgressBar(
            splash, width=280, height=8, progress_color="#7f00ff", fg_color="#1e2132"
        )
        prog.place(relx=0.5, rely=0.64, anchor="center")
        prog.set(0)
        self.update()
        for i in range(1, 101):
            prog.set(i / 100)
            self.update()
            time.sleep(0.008)
        splash.destroy()
        self.show_auth_screen()

    def show_auth_screen(self):
        self.auth_frame = AuthFrame(self, self.login_success)
        self.auth_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")

    def login_success(self, user_id, username):
        self.current_user_id = user_id
        self.current_username = username
        self.auth_frame.destroy()
        self.setup_main_interface()
        notifications.toast(f"Welcome back, {username}!")

    # ---------------------------------------------------------------------
    # Main UI (sidebar + content area)
    # ---------------------------------------------------------------------
    def setup_main_interface(self):
        # Root container split into sidebar and right side
        self.container = ctk.CTkFrame(self, fg_color="#0d0e15", corner_radius=0)
        self.container.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(1, weight=1)

        # Sidebar (custom component)
        def nav_callback(page_name: str):
            self.show_frame(page_name)

        def get_profile_name():
            return self.current_username

        self.sidebar = Sidebar(
            master=self.container,
            nav_callback=nav_callback,
            get_user_profile=get_profile_name,
            accent_color=self.current_accent_color,
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # Right column (header + page container)
        self.right_col = ctk.CTkFrame(self.container, fg_color="transparent", corner_radius=0)
        self.right_col.grid(row=0, column=1, sticky="nsew")
        self.right_col.grid_rowconfigure(1, weight=1)
        self.right_col.grid_columnconfigure(0, weight=1)

        # Header bar
        self.header = ctk.CTkFrame(self.right_col, height=65, fg_color="#10121d", corner_radius=0, border_color="#1e2132", border_width=1)
        self.header.grid(row=0, column=0, sticky="ew")
        self.header.grid_propagate(False)
        self.header_page_title = ctk.CTkLabel(
            self.header,
            text="Dashboard",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#ffffff",
        )
        self.header_page_title.grid(row=0, column=0, padx=25, pady=18, sticky="w")
        # Online status dot & text
        status_container = ctk.CTkFrame(self.header, fg_color="transparent")
        status_container.grid(row=0, column=1, pady=18, sticky="w")
        dot = ctk.CTkCanvas(status_container, width=12, height=12, bg="#10121d", highlightthickness=0)
        dot.pack(side="left", padx=(0, 6))
        dot.create_oval(2, 2, 10, 10, fill="#28a749", outline="")
        ctk.CTkLabel(status_container, text="System Online", font=ctk.CTkFont(size=11), text_color="#8b8c9d").pack(side="left")
        # Clock label
        self.clock_lbl = ctk.CTkLabel(
            self.header,
            text="",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#8b8c9d",
        )
        self.clock_lbl.grid(row=0, column=3, padx=25, pady=18, sticky="e")
        self.update_clock()

        # Content container where pages will be swapped
        self.page_container = ctk.CTkFrame(self.right_col, fg_color="transparent")
        self.page_container.grid(row=1, column=0, sticky="nsew")
        self.page_container.grid_rowconfigure(0, weight=1)
        self.page_container.grid_columnconfigure(0, weight=1)

        # Pre‑create frames (lazy loading also works, but pre‑creation simplifies first load)
        self.frames = {
            "dashboard": DashboardFrame(self.page_container, self.current_user_id, self.current_username, self.show_frame),
            "chat": ChatbotFrame(self.page_container, self.current_user_id),
            "notes": NotesFrame(self.page_container, self.current_user_id),
            "todo": TodoFrame(self.page_container, self.current_user_id),
            "qr": QRGeneratorFrame(self.page_container),
            "pwd": PasswordGeneratorFrame(self.page_container),
            "settings": SettingsFrame(self.page_container, self.current_user_id, self.current_username, self.refresh_user_profile, self.change_accent_theme),
            "about": AboutFrame(self.page_container),
        }

        # Show default dashboard
        self.show_frame("dashboard")

    # ---------------------------------------------------------------------
    # Frame switching logic
    # ---------------------------------------------------------------------
    def show_frame(self, name: str):
        """Hide current page and display the requested one.
        Handles errors gracefully and logs activity.
        """
        print(f"[INFO] Opening {name.capitalize()} Page")
        # Hide previous frame
        if self.active_frame is not None:
            self.active_frame.grid_forget()
        # Retrieve target frame
        frame = self.frames.get(name)
        if not frame:
            messagebox.showerror("Navigation Error", f"Page '{name}' not found.")
            return
        try:
            frame.grid(row=0, column=0, sticky="nsew")
            self.active_frame = frame
            # Update header title
            title_map = {
                "dashboard": "Dashboard Workspace",
                "chat": "AI Chat Assistant",
                "notes": "Workspace Notes",
                "todo": "Priority Tasks Tracker",
                "qr": "QR Code Generator",
                "pwd": "Password Generator",
                "settings": "Settings Panel",
                "about": "About HireBot",
            }
            self.header_page_title.configure(text=title_map.get(name, "HireBot Assistant"))
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Page Load Error", f"Failed to load {name}: {e}")

    # ---------------------------------------------------------------------
    # Helper callbacks used by Sidebar & Settings
    # ---------------------------------------------------------------------
    def refresh_user_profile(self, new_username: str):
        self.current_username = new_username
        self.sidebar.refresh_profile(new_username)
        # propagate to dashboard if needed
        if hasattr(self.frames.get("dashboard"), "username"):
            self.frames["dashboard"].username = new_username

    def change_accent_theme(self, color_hex: str):
        self.current_accent_color = color_hex
        AssetsManager.generate_all_assets(color_hex)
        # Update sidebar icons & other UI components
        self.sidebar.refresh_accent(color_hex)
        # Force reload of active frame if it uses accent‑dependent assets
        if self.active_frame:
            self.active_frame.update_idletasks()

    # ---------------------------------------------------------------------
    # Clock & logout
    # ---------------------------------------------------------------------
    def update_clock(self):
        now = datetime.datetime.now()
        self.clock_lbl.configure(text=now.strftime("%A, %b %d  |  %I:%M:%S %p"))
        self.after(1000, self.update_clock)

    def logout(self):
        # Reset session state and show auth again
        self.current_user_id = None
        self.current_username = None
        # Destroy main UI components
        for widget in self.container.winfo_children():
            widget.destroy()
        self.show_auth_screen()

if __name__ == "__main__":
    app = App()
    app.mainloop()
