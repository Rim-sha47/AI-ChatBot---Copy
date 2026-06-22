import customtkinter as ctk
import datetime
from PIL import Image
from database import db

class DashboardFrame(ctk.CTkFrame):
    def __init__(self, master, user_id, username, select_frame_callback):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.user_id = user_id
        self.username = username
        self.select_frame = select_frame_callback
        
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # We'll load the icons
        self.load_icons()
        
        # 1. Greeting Banner
        self.greeting_frame = ctk.CTkFrame(self, fg_color="#181a26", corner_radius=16, border_color="#2b2e42", border_width=1)
        self.greeting_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10), ipady=15)
        self.greeting_frame.grid_columnconfigure(0, weight=1)
        
        self.lbl_greeting = ctk.CTkLabel(
            self.greeting_frame,
            text="",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#ffffff",
            anchor="w"
        )
        self.lbl_greeting.grid(row=0, column=0, padx=25, pady=(15, 5), sticky="w")
        
        self.lbl_sub = ctk.CTkLabel(
            self.greeting_frame,
            text="Welcome back to your premium workspace. Here's your status at a glance.",
            font=ctk.CTkFont(size=13),
            text_color="#8b8c9d",
            anchor="w"
        )
        self.lbl_sub.grid(row=1, column=0, padx=25, pady=(0, 15), sticky="w")
        
        # 2. Stats Grid
        self.stats_container = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_container.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        self.stats_container.grid_columnconfigure((0, 1, 2), weight=1, uniform="equal")
        
        # Card 1: Chat count
        self.card_chats = ctk.CTkFrame(self.stats_container, fg_color="#181a26", corner_radius=16, border_color="#2b2e42", border_width=1)
        self.card_chats.grid(row=0, column=0, padx=(0, 10), sticky="nsew", ipady=10)
        self.card_chats.grid_columnconfigure(1, weight=1)
        
        self.icon_chats = ctk.CTkLabel(self.card_chats, text="", image=self.icon_chat_img)
        self.icon_chats.grid(row=0, column=0, rowspan=2, padx=20, pady=20)
        self.val_chats = ctk.CTkLabel(self.card_chats, text="0", font=ctk.CTkFont(size=26, weight="bold"), text_color="#00f2fe")
        self.val_chats.grid(row=0, column=1, padx=(0, 20), pady=(15, 0), sticky="w")
        lbl_chats_title = ctk.CTkLabel(self.card_chats, text="Total AI Chats", font=ctk.CTkFont(size=13), text_color="#8b8c9d")
        lbl_chats_title.grid(row=1, column=1, padx=(0, 20), pady=(0, 15), sticky="nw")
        
        # Card 2: Notes Count
        self.card_notes = ctk.CTkFrame(self.stats_container, fg_color="#181a26", corner_radius=16, border_color="#2b2e42", border_width=1)
        self.card_notes.grid(row=0, column=1, padx=5, sticky="nsew", ipady=10)
        self.card_notes.grid_columnconfigure(1, weight=1)
        
        self.icon_notes = ctk.CTkLabel(self.card_notes, text="", image=self.icon_notes_img)
        self.icon_notes.grid(row=0, column=0, rowspan=2, padx=20, pady=20)
        self.val_notes = ctk.CTkLabel(self.card_notes, text="0", font=ctk.CTkFont(size=26, weight="bold"), text_color="#7f00ff")
        self.val_notes.grid(row=0, column=1, padx=(0, 20), pady=(15, 0), sticky="w")
        lbl_notes_title = ctk.CTkLabel(self.card_notes, text="Rich Notes Saved", font=ctk.CTkFont(size=13), text_color="#8b8c9d")
        lbl_notes_title.grid(row=1, column=1, padx=(0, 20), pady=(0, 15), sticky="nw")
        
        # Card 3: Tasks completion
        self.card_todo = ctk.CTkFrame(self.stats_container, fg_color="#181a26", corner_radius=16, border_color="#2b2e42", border_width=1)
        self.card_todo.grid(row=0, column=2, padx=(10, 0), sticky="nsew", ipady=10)
        self.card_todo.grid_columnconfigure(0, weight=1)
        
        todo_title_frame = ctk.CTkFrame(self.card_todo, fg_color="transparent")
        todo_title_frame.pack(fill="x", padx=20, pady=(15, 5))
        
        self.val_todo = ctk.CTkLabel(todo_title_frame, text="0/0 Completed", font=ctk.CTkFont(size=15, weight="bold"), text_color="#e0e0e6")
        self.val_todo.pack(side="left")
        
        self.pct_todo = ctk.CTkLabel(todo_title_frame, text="0%", font=ctk.CTkFont(size=15, weight="bold"), text_color="#28a749")
        self.pct_todo.pack(side="right")
        
        self.todo_progress = ctk.CTkProgressBar(self.card_todo, height=8, progress_color="#28a749", fg_color="#2b2e42")
        self.todo_progress.pack(fill="x", padx=20, pady=(10, 15))
        self.todo_progress.set(0)
        
        # 3. Quick Actions Header
        self.lbl_actions_title = ctk.CTkLabel(self, text="Quick Shortcuts", font=ctk.CTkFont(size=18, weight="bold"), text_color="#ffffff")
        self.lbl_actions_title.grid(row=2, column=0, sticky="w", padx=20, pady=(20, 10))
        
        # 4. Quick Actions Grid
        self.actions_grid = ctk.CTkFrame(self, fg_color="transparent")
        self.actions_grid.grid(row=3, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.actions_grid.grid_rowconfigure((0, 1), weight=1)
        self.actions_grid.grid_columnconfigure((0, 1), weight=1, uniform="equal")
        
        # Shortcut 1: Chatbot
        self.btn_chat = self.create_shortcut_card(
            self.actions_grid, "AI Chat Assistant", "Launch HireBot assistant to ask questions, code, and search Wikipedia.", 
            self.icon_chat_img, lambda: self.select_frame("chat")
        )
        self.btn_chat.grid(row=0, column=0, padx=(0, 10), pady=(0, 10), sticky="nsew")
        
        # Shortcut 2: Notes
        self.btn_notes = self.create_shortcut_card(
            self.actions_grid, "Notes Workspace", "Write and categorize your rich text documents with auto-save.", 
            self.icon_notes_img, lambda: self.select_frame("notes")
        )
        self.btn_notes.grid(row=0, column=1, padx=(10, 0), pady=(0, 10), sticky="nsew")
        
        # Shortcut 3: Todo
        self.btn_todo = self.create_shortcut_card(
            self.actions_grid, "Tasks & Priorities", "Organize tasks by low/medium/high priority and due dates.", 
            self.icon_todo_img, lambda: self.select_frame("todo")
        )
        self.btn_todo.grid(row=1, column=0, padx=(0, 10), pady=(10, 0), sticky="nsew")
        
        # Shortcut 4: Password
        self.btn_pwd = self.create_shortcut_card(
            self.actions_grid, "Security Generator", "Generate complex military-grade passwords with visual strength meter.", 
            self.icon_pwd_img, lambda: self.select_frame("pwd")
        )
        self.btn_pwd.grid(row=1, column=1, padx=(10, 0), pady=(10, 0), sticky="nsew")

        # Initial refresh
        self.refresh_stats()

    def load_icons(self):
        self.icon_chat_img = ctk.CTkImage(
            light_image=Image.open("assets/chat_active.png"),
            dark_image=Image.open("assets/chat_active.png"),
            size=(32, 32)
        )
        self.icon_notes_img = ctk.CTkImage(
            light_image=Image.open("assets/notes_active.png"),
            dark_image=Image.open("assets/notes_active.png"),
            size=(32, 32)
        )
        self.icon_todo_img = ctk.CTkImage(
            light_image=Image.open("assets/todo_active.png"),
            dark_image=Image.open("assets/todo_active.png"),
            size=(32, 32)
        )
        self.icon_pwd_img = ctk.CTkImage(
            light_image=Image.open("assets/pwd_active.png"),
            dark_image=Image.open("assets/pwd_active.png"),
            size=(32, 32)
        )

    def create_shortcut_card(self, parent, title, desc, icon_img, command):
        # We can implement a clean button design by embedding layout inside a frame and binding clicks
        card = ctk.CTkFrame(parent, fg_color="#181a26", corner_radius=16, border_color="#2b2e42", border_width=1)
        
        # Grid layout for content
        card.grid_columnconfigure(1, weight=1)
        card.grid_rowconfigure(1, weight=1)
        
        lbl_icon = ctk.CTkLabel(card, text="", image=icon_img)
        lbl_icon.grid(row=0, column=0, rowspan=2, padx=(20, 15), pady=20, sticky="n")
        
        lbl_title = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=16, weight="bold"), text_color="#ffffff")
        lbl_title.grid(row=0, column=1, padx=(0, 20), pady=(15, 2), sticky="w")
        
        lbl_desc = ctk.CTkLabel(card, text=desc, font=ctk.CTkFont(size=12), text_color="#8b8c9d", wraplength=260, justify="left")
        lbl_desc.grid(row=1, column=1, padx=(0, 20), pady=(0, 15), sticky="nw")
        
        # Bind click triggers to run command
        for widget in (card, lbl_title, lbl_desc, lbl_icon):
            widget.bind("<Button-1>", lambda e: command())
            widget.bind("<Enter>", lambda e, c=card: c.configure(border_color="#7f00ff"))
            widget.bind("<Leave>", lambda e, c=card: c.configure(border_color="#2b2e42"))
            
        return card

    def refresh_stats(self):
        # 1. Update Greeting
        hour = datetime.datetime.now().hour
        if hour < 12:
            greet = "Good Morning"
        elif hour < 18:
            greet = "Good Afternoon"
        else:
            greet = "Good Evening"
            
        self.lbl_greeting.configure(text=f"{greet}, {self.username}!")
        
        # 2. Fetch SQLite DB Counts
        stats = db.get_user_stats(self.user_id)
        
        self.val_chats.configure(text=str(stats["chats_count"]))
        self.val_notes.configure(text=str(stats["notes_count"]))
        
        total = stats["total_tasks"]
        comp = stats["completed_tasks"]
        self.val_todo.configure(text=f"{comp}/{total} Tasks")
        
        if total > 0:
            pct = int((comp / total) * 100)
            self.pct_todo.configure(text=f"{pct}%")
            self.todo_progress.set(comp / total)
        else:
            self.pct_todo.configure(text="0%")
            self.todo_progress.set(0)
