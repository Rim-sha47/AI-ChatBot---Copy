import customtkinter as ctk
import bcrypt
import notifications
from database import db

class AuthFrame(ctk.CTkFrame):
    def __init__(self, master, switch_to_main_callback):
        super().__init__(master, corner_radius=0, fg_color="#0d0e15")
        self.master = master
        self.switch_to_main = switch_to_main_callback
        
        # Configure layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.show_login()

    def show_login(self):
        # Clear current frame
        for widget in self.winfo_children():
            widget.destroy()
            
        login_card = ctk.CTkFrame(
            self,
            width=380,
            height=460,
            corner_radius=16,
            fg_color="#181a26",
            border_color="#7f00ff",
            border_width=1
        )
        login_card.grid(row=0, column=0, padx=20, pady=20)
        login_card.grid_propagate(False)
        
        # Title
        title_lbl = ctk.CTkLabel(
            login_card,
            text="Welcome to HireBot",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color="#ffffff"
        )
        title_lbl.pack(pady=(45, 5))
        
        sub_lbl = ctk.CTkLabel(
            login_card,
            text="Sign in to your AI Assistant Workspace",
            font=ctk.CTkFont(size=12),
            text_color="#8b8c9d"
        )
        sub_lbl.pack(pady=(0, 30))
        
        # Username
        self.login_user_entry = ctk.CTkEntry(
            login_card,
            placeholder_text="Username",
            width=280,
            height=42,
            corner_radius=10,
            border_color="#2b2e42",
            fg_color="#1e2132",
            text_color="#ffffff",
            placeholder_text_color="#8b8c9d"
        )
        self.login_user_entry.pack(pady=10)
        self.login_user_entry.bind("<Return>", lambda e: self.handle_login())
        
        # Password
        self.login_pass_entry = ctk.CTkEntry(
            login_card,
            placeholder_text="Password",
            show="*",
            width=280,
            height=42,
            corner_radius=10,
            border_color="#2b2e42",
            fg_color="#1e2132",
            text_color="#ffffff",
            placeholder_text_color="#8b8c9d"
        )
        self.login_pass_entry.pack(pady=10)
        self.login_pass_entry.bind("<Return>", lambda e: self.handle_login())
        
        # Login Button
        login_btn = ctk.CTkButton(
            login_card,
            text="Sign In",
            width=280,
            height=42,
            corner_radius=10,
            fg_color="#7f00ff",
            hover_color="#6200c8",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.handle_login
        )
        login_btn.pack(pady=(20, 10))
        
        # Switch to Register
        switch_btn = ctk.CTkButton(
            login_card,
            text="Don't have an account? Sign Up",
            fg_color="transparent", 
            hover_color="#1e2132",
            text_color="#8b8c9d",
            font=ctk.CTkFont(size=12, underline=False),
            command=self.show_register
        )
        switch_btn.pack(pady=5)

    def show_register(self):
        # Clear current frame
        for widget in self.winfo_children():
            widget.destroy()
            
        reg_card = ctk.CTkFrame(
            self,
            width=380,
            height=460,
            corner_radius=16,
            fg_color="#181a26",
            border_color="#00f2fe",
            border_width=1
        )
        reg_card.grid(row=0, column=0, padx=20, pady=20)
        reg_card.grid_propagate(False)
        
        # Title
        title_lbl = ctk.CTkLabel(
            reg_card,
            text="Create Account",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color="#ffffff"
        )
        title_lbl.pack(pady=(45, 5))
        
        sub_lbl = ctk.CTkLabel(
            reg_card,
            text="Register a new local workspace profile",
            font=ctk.CTkFont(size=12),
            text_color="#8b8c9d"
        )
        sub_lbl.pack(pady=(0, 30))
        
        # Username
        self.reg_user_entry = ctk.CTkEntry(
            reg_card,
            placeholder_text="Username",
            width=280,
            height=42,
            corner_radius=10,
            border_color="#2b2e42",
            fg_color="#1e2132",
            text_color="#ffffff",
            placeholder_text_color="#8b8c9d"
        )
        self.reg_user_entry.pack(pady=10)
        self.reg_user_entry.bind("<Return>", lambda e: self.handle_register())
        
        # Password
        self.reg_pass_entry = ctk.CTkEntry(
            reg_card,
            placeholder_text="Password (min. 6 characters)",
            show="*",
            width=280,
            height=42,
            corner_radius=10,
            border_color="#2b2e42",
            fg_color="#1e2132",
            text_color="#ffffff",
            placeholder_text_color="#8b8c9d"
        )
        self.reg_pass_entry.pack(pady=10)
        self.reg_pass_entry.bind("<Return>", lambda e: self.handle_register())
        
        # Register Button
        reg_btn = ctk.CTkButton(
            reg_card,
            text="Sign Up",
            width=280,
            height=42,
            corner_radius=10,
            fg_color="#00f2fe",
            hover_color="#00c0cb",
            text_color="#0d0e15",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.handle_register
        )
        reg_btn.pack(pady=(20, 10))
        
        # Switch to Login
        switch_btn = ctk.CTkButton(
            reg_card,
            text="Already have an account? Sign In",
            fg_color="transparent", 
            hover_color="#1e2132",
            text_color="#8b8c9d",
            font=ctk.CTkFont(size=12, underline=False),
            command=self.show_login
        )
        switch_btn.pack(pady=5)

    def handle_login(self):
        username = self.login_user_entry.get().strip()
        password = self.login_pass_entry.get().strip()
        
        if not username or not password:
            notifications.show_error(self, "Please enter both credentials.")
            return
            
        user = db.get_user(username)
        if user:
            user_id, db_username, db_password_hash = user
            if bcrypt.checkpw(password.encode('utf-8'), db_password_hash.encode('utf-8')):
                # Success
                self.switch_to_main(user_id, db_username)
            else:
                notifications.show_error(self, "Invalid username or password.")
        else:
            notifications.show_error(self, "Profile not found.")

    def handle_register(self):
        username = self.reg_user_entry.get().strip()
        password = self.reg_pass_entry.get().strip()
        
        if not username or not password:
            notifications.show_error(self, "Please fill in all input fields.")
            return
            
        if len(password) < 6:
            notifications.show_error(self, "Password must be at least 6 characters.")
            return
            
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        if db.add_user(username, hashed_pw):
            notifications.show_success(self, "Account created successfully! Please Sign In.")
            self.show_login()
        else:
            notifications.show_error(self, "Username already exists.")

