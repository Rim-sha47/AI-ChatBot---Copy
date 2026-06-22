'''about.py - About page for HireBot AI Assistant'''
import customtkinter as ctk
import notifications

class AboutFrame(ctk.CTkFrame):
    """Simple About page showing application details and version info."""
    def __init__(self, master):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Container for content
        container = ctk.CTkFrame(self, fg_color="#181a26", corner_radius=16, border_color="#2b2e42", border_width=1)
        container.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Title
        title = ctk.CTkLabel(container, text="About HireBot AI Assistant",
                            font=ctk.CTkFont(size=22, weight="bold"),
                            text_color="#ffffff")
        title.pack(pady=(30, 10))

        # Description
        desc_text = (
            "HireBot is a premium, portfolio‑quality AI chatbot assistant built with "
            "CustomTkinter. It includes a modular workspace featuring a chatbot, notes, "
            "to‑do list, QR code generator, password generator, and a secure login/register system. "
            "The UI follows a dark glassmorphism theme with smooth animations and dynamic accent colors."
        )
        desc = ctk.CTkLabel(container, text=desc_text, wraplength=500,
                            font=ctk.CTkFont(size=13), text_color="#e0e0e0")
        desc.pack(padx=30, pady=10)

        # Version and credits
        version = ctk.CTkLabel(container, text="Version: 2.0‑Portfolio",
                              font=ctk.CTkFont(size=12, weight="bold"),
                              text_color="#7f00ff")
        version.pack(pady=(20, 5))

        credits = ctk.CTkLabel(container, text="Developed by: Your Name (2026)",
                               font=ctk.CTkFont(size=11), text_color="#8b8c9d")
        credits.pack(pady=(0, 30))

        # Close button (optional)
        close_btn = ctk.CTkButton(container, text="Close", width=100, height=32,
                                 corner_radius=8, fg_color="#eb4034", hover_color="#c8362b",
                                 font=ctk.CTkFont(size=12, weight="bold"),
                                 command=self.destroy)
        close_btn.pack(pady=10)

        # Show a toast when the page is opened
        notifications.toast("Opened About page")
