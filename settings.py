import customtkinter as ctk
import bcrypt
from tkinter import messagebox
from database import db
import notifications

class SettingsFrame(ctk.CTkFrame):
    def __init__(self, master, user_id, current_username, refresh_user_callback, change_accent_callback):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.user_id = user_id
        self.username = current_username
        self.refresh_user = refresh_user_callback
        self.change_accent = change_accent_callback
        
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure((0, 1), weight=1, uniform="equal")
        
        # Title
        title_lbl = ctk.CTkLabel(self, text="User & Visual Settings", font=ctk.CTkFont(size=24, weight="bold"), text_color="#ffffff")
        title_lbl.grid(row=0, column=0, columnspan=2, pady=(20, 15), sticky="w", padx=20)
        
        # Left Panel (Theme Customizer & App Info)
        self.left_panel = ctk.CTkFrame(self, fg_color="#181a26", corner_radius=16, border_color="#2b2e42", border_width=1)
        self.left_panel.grid(row=1, column=0, padx=(20, 10), pady=10, sticky="nsew")
        self.left_panel.grid_columnconfigure(0, weight=1)
        
        theme_title = ctk.CTkLabel(self.left_panel, text="Visual Customizer", font=ctk.CTkFont(size=18, weight="bold"), text_color="#ffffff")
        theme_title.pack(anchor="w", padx=20, pady=(20, 10))
        
        theme_desc = ctk.CTkLabel(
            self.left_panel, 
            text="Change the application interface highlight color. This will regenerate visual assets dynamically.",
            font=ctk.CTkFont(size=12),
            text_color="#8b8c9d",
            wraplength=350,
            justify="left"
        )
        theme_desc.pack(anchor="w", padx=20, pady=(0, 15))
        
        # Color dropdown selection
        self.accents = {
            "Royal Purple (Default)": "#7f00ff",
            "Electric Blue": "#00f2fe",
            "Emerald Green": "#28a749",
            "Neon Teal": "#00f5d4",
            "Vibrant Pink": "#f15bb5",
            "Bright Amber": "#ffb703"
        }
        
        self.accent_selector = ctk.CTkOptionMenu(
            self.left_panel,
            values=list(self.accents.keys()),
            command=self.handle_accent_change,
            fg_color="#7f00ff",
            button_color="#6200c8",
            button_hover_color="#5000a5"
        )
        self.accent_selector.pack(anchor="w", padx=20, pady=(0, 30))
        
        # App Info Section
        cls_info_lbl = ctk.CTkLabel(self.left_panel, text="App Specifications", font=ctk.CTkFont(size=16, weight="bold"), text_color="#ffffff")
        cls_info_lbl.pack(anchor="w", padx=20, pady=(10, 10))
        
        self.spec_card = ctk.CTkFrame(self.left_panel, fg_color="#1e2132", corner_radius=10)
        self.spec_card.pack(fill="x", padx=20, pady=(0, 20))
        
        specs = [
            ("Core Version", "HireBot v2.0-Portfolio"),
            ("UI Design Theme", "Dark Glassmorphism"),
            ("Engine Stack", "Python + CustomTkinter"),
            ("Local Memory", "SQLite3 Caching DB")
        ]
        
        for idx, (k, v) in enumerate(specs):
            f = ctk.CTkFrame(self.spec_card, fg_color="transparent")
            f.pack(fill="x", padx=15, pady=6)
            ctk.CTkLabel(f, text=k, font=ctk.CTkFont(size=12, weight="bold"), text_color="#8b8c9d").pack(side="left")
            ctk.CTkLabel(f, text=v, font=ctk.CTkFont(size=12), text_color="#ffffff").pack(side="right")

        # Right Panel (Security Settings)
        self.right_panel = ctk.CTkFrame(self, fg_color="#181a26", corner_radius=16, border_color="#2b2e42", border_width=1)
        self.right_panel.grid(row=1, column=1, padx=(10, 20), pady=10, sticky="nsew")
        self.right_panel.grid_columnconfigure(0, weight=1)
        
        security_title = ctk.CTkLabel(self.right_panel, text="Security & Profile", font=ctk.CTkFont(size=18, weight="bold"), text_color="#ffffff")
        security_title.pack(anchor="w", padx=20, pady=(20, 10))
        
        security_desc = ctk.CTkLabel(
            self.right_panel, 
            text="Update your login password securely using advanced Bcrypt hashing algorithm.",
            font=ctk.CTkFont(size=12),
            text_color="#8b8c9d",
            wraplength=350,
            justify="left"
        )
        security_desc.pack(anchor="w", padx=20, pady=(0, 20))
        
        # User details inputs
        ctk.CTkLabel(self.right_panel, text="Username", font=ctk.CTkFont(size=12, weight="bold"), text_color="#e0e0e6").pack(anchor="w", padx=20, pady=(5, 2))
        self.entry_username = ctk.CTkEntry(self.right_panel, height=36, placeholder_text=self.username, state="disabled")
        self.entry_username.pack(fill="x", padx=20, pady=(0, 15))
        
        ctk.CTkLabel(self.right_panel, text="New Password", font=ctk.CTkFont(size=12, weight="bold"), text_color="#e0e0e6").pack(anchor="w", padx=20, pady=(5, 2))
        self.entry_pwd = ctk.CTkEntry(self.right_panel, show="*", height=36, placeholder_text="Enter new password...")
        self.entry_pwd.pack(fill="x", padx=20, pady=(0, 10))
        
        ctk.CTkLabel(self.right_panel, text="Confirm New Password", font=ctk.CTkFont(size=12, weight="bold"), text_color="#e0e0e6").pack(anchor="w", padx=20, pady=(5, 2))
        self.entry_pwd_conf = ctk.CTkEntry(self.right_panel, show="*", height=36, placeholder_text="Confirm new password...")
        self.entry_pwd_conf.pack(fill="x", padx=20, pady=(0, 20))
        
        self.btn_update_pwd = ctk.CTkButton(
            self.right_panel, 
            text="Save Profile Password", 
            command=self.update_pwd,
            font=ctk.CTkFont(weight="bold")
        )
        self.btn_update_pwd.pack(anchor="w", padx=20, pady=(0, 20))

    def handle_accent_change(self, option_name):
        color_hex = self.accents.get(option_name, "#7f00ff")
        
        # Dynamically change OptionMenu background colors to match accent selection
        hover_color = self.get_lighter_color(color_hex)
        self.accent_selector.configure(fg_color=color_hex, button_color=color_hex, button_hover_color=hover_color)
        
        # Run callback in main.py to regenerate assets and refresh views
        self.change_accent(color_hex)
        notifications.show_success(self, f"Accent color updated to {option_name}!")

    def get_lighter_color(self, hex_code):
        # Quick helper to lighten color for hovers
        hex_code = hex_code.lstrip('#')
        r, g, b = tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))
        r = min(255, int(r * 1.25))
        g = min(255, int(g * 1.25))
        b = min(255, int(b * 1.25))
        return f"#{r:02x}{g:02x}{b:02x}"

    def update_pwd(self):
        new_pwd = self.entry_pwd.get().strip()
        conf_pwd = self.entry_pwd_conf.get().strip()
        
        if not new_pwd:
            notifications.show_error(self, "Password field cannot be empty.")
            return
            
        if len(new_pwd) < 6:
            notifications.show_error(self, "Password must be at least 6 characters.")
            return
            
        if new_pwd != conf_pwd:
            notifications.show_error(self, "Passwords do not match.")
            return
            
        # Perform hash and update
        hashed_pw = bcrypt.hashpw(new_pwd.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        if db.update_user_password(self.user_id, hashed_pw):
            notifications.show_success(self, "Password updated successfully!")
            self.entry_pwd.delete(0, 'end')
            self.entry_pwd_conf.delete(0, 'end')
        else:
            notifications.show_error(self, "Failed to update profile password.")
