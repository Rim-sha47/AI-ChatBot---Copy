import customtkinter as ctk
from database import db
from tkinter import filedialog, messagebox
import notifications

class NotesFrame(ctk.CTkFrame):
    def __init__(self, master, user_id):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.user_id = user_id
        
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=3) # Left List Panel
        self.grid_columnconfigure(1, weight=5) # Right Editor Panel
        
        self.current_note_id = None
        self.auto_save_job = None
        
        # Header / Title
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=2, pady=(20, 10), sticky="ew", padx=20)
        
        title_lbl = ctk.CTkLabel(header_frame, text="Workspace Notes Manager", font=ctk.CTkFont(size=20, weight="bold"), text_color="#ffffff")
        title_lbl.pack(side="left")
        
        self.auto_save_status = ctk.CTkLabel(header_frame, text="All notes saved", font=ctk.CTkFont(size=12, slant="italic"), text_color="#8b8c9d")
        self.auto_save_status.pack(side="right", padx=10)
        
        # --- LEFT SIDE PANEL (List & Searches) ---
        self.left_panel = ctk.CTkFrame(self, fg_color="#181a26", corner_radius=16, border_color="#2b2e42", border_width=1)
        self.left_panel.grid(row=1, column=0, padx=(20, 10), pady=(0, 20), sticky="nsew")
        self.left_panel.grid_rowconfigure(2, weight=1)
        self.left_panel.grid_columnconfigure(0, weight=1)
        
        # Search Bar
        self.search_entry = ctk.CTkEntry(
            self.left_panel, 
            placeholder_text="🔍 Search notes...", 
            height=36,
            corner_radius=8,
            border_color="#2b2e42",
            fg_color="#1e2132"
        )
        self.search_entry.grid(row=0, column=0, padx=15, pady=(15, 8), sticky="ew")
        self.search_entry.bind("<KeyRelease>", lambda e: self.load_notes())
        
        # Category Filter Dropdown
        filter_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        filter_frame.grid(row=1, column=0, padx=15, pady=(0, 8), sticky="ew")
        
        ctk.CTkLabel(filter_frame, text="Filter:", font=ctk.CTkFont(size=11, weight="bold"), text_color="#8b8c9d").pack(side="left")
        
        self.categories_list = ["All", "General", "Work", "Personal", "Ideas", "Code", "Other"]
        self.filter_category = ctk.CTkOptionMenu(
            filter_frame,
            values=self.categories_list,
            height=28,
            width=180,
            fg_color="#1e2132",
            button_color="#2a2b3d",
            command=lambda c: self.load_notes()
        )
        self.filter_category.pack(side="right", fill="x", expand=True, padx=(5, 0))
        
        # Notes List Cards container
        self.list_frame = ctk.CTkScrollableFrame(self.left_panel, fg_color="transparent")
        self.list_frame.grid(row=2, column=0, padx=10, pady=(0, 15), sticky="nsew")
        
        # --- RIGHT SIDE PANEL (Editor) ---
        self.editor_panel = ctk.CTkFrame(self, fg_color="#181a26", corner_radius=16, border_color="#2b2e42", border_width=1)
        self.editor_panel.grid(row=1, column=1, padx=(10, 20), pady=(0, 20), sticky="nsew")
        self.editor_panel.grid_rowconfigure(2, weight=1)
        self.editor_panel.grid_columnconfigure(0, weight=1)
        
        # Title of note input
        meta_editor = ctk.CTkFrame(self.editor_panel, fg_color="transparent")
        meta_editor.grid(row=0, column=0, padx=15, pady=(15, 8), sticky="ew")
        
        self.title_entry = ctk.CTkEntry(
            meta_editor, 
            placeholder_text="Untitled Note Title", 
            font=ctk.CTkFont(size=16, weight="bold"),
            height=38,
            corner_radius=8,
            border_color="#2b2e42",
            fg_color="#1e2132"
        )
        self.title_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.title_entry.bind("<KeyRelease>", self.trigger_autosave)
        
        # Editor Category Select
        self.note_category = ctk.CTkOptionMenu(
            meta_editor,
            values=self.categories_list[1:], # remove "All"
            height=38,
            width=110,
            fg_color="#7f00ff",
            button_color="#6200c8",
            button_hover_color="#5000a5"
        )
        self.note_category.pack(side="right")
        
        # Textbox Editor
        self.content_textbox = ctk.CTkTextbox(
            self.editor_panel, 
            wrap="word", 
            fg_color="#10121d", 
            border_color="#1e2132",
            border_width=1,
            corner_radius=10,
            font=ctk.CTkFont(size=13)
        )
        self.content_textbox.grid(row=2, column=0, padx=15, pady=(0, 10), sticky="nsew")
        self.content_textbox.bind("<KeyRelease>", self.trigger_autosave)
        
        # Bottom controls row
        self.editor_controls = ctk.CTkFrame(self.editor_panel, fg_color="transparent")
        self.editor_controls.grid(row=3, column=0, padx=15, pady=(0, 15), sticky="ew")
        
        self.save_btn = ctk.CTkButton(
            self.editor_controls, text="Save Note", width=90, height=36, corner_radius=8,
            fg_color="#7f00ff", hover_color="#6200c8", font=ctk.CTkFont(weight="bold"),
            command=lambda: self.save_note(show_toast=True)
        )
        self.save_btn.pack(side="left", padx=3)
        
        self.clear_btn = ctk.CTkButton(
            self.editor_controls, text="Clear Editor", width=90, height=36, corner_radius=8,
            fg_color="#1e2132", hover_color="#2b2e42", text_color="#8b8c9d",
            command=self.clear_editor
        )
        self.clear_btn.pack(side="left", padx=3)
        
        self.export_btn = ctk.CTkButton(
            self.editor_controls, text="Export Note", width=90, height=36, corner_radius=8,
            fg_color="#1e2132", hover_color="#2b2e42", text_color="#ffffff",
            command=self.export_note
        )
        self.export_btn.pack(side="left", padx=3)
        
        self.delete_btn = ctk.CTkButton(
            self.editor_controls, text="Delete", width=90, height=36, corner_radius=8,
            fg_color="#eb4034", hover_color="#c8362b", font=ctk.CTkFont(weight="bold"),
            command=lambda: self.delete_note(self.current_note_id)
        )
        self.delete_btn.pack(side="right", padx=3)
        
        self.load_notes()
        self.clear_editor()

    def load_notes(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()
            
        search_query = self.search_entry.get().strip()
        category_filter = self.filter_category.get()
        
        notes = db.get_notes(self.user_id, search_query=search_query, category_filter=category_filter)
        
        for note in notes:
            note_id, title, content, category, created_at, updated_at = note
            
            # Note Card
            card = ctk.CTkFrame(
                self.list_frame, 
                fg_color="#10121d" if note_id != self.current_note_id else "#1e2132",
                border_color="#2b2e42" if note_id != self.current_note_id else "#7f00ff",
                border_width=1,
                corner_radius=10
            )
            card.pack(fill="x", pady=5, padx=5)
            
            # Bind click card to view note
            for w in (card,):
                w.bind("<Button-1>", lambda e, nid=note_id, t=title, c=content, cat=category: self.view_note(nid, t, c, cat))
                
            # Content inside card
            lbl_title = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=13, weight="bold"), text_color="#ffffff", anchor="w")
            lbl_title.pack(fill="x", padx=12, pady=(10, 2))
            lbl_title.bind("<Button-1>", lambda e, nid=note_id, t=title, c=content, cat=category: self.view_note(nid, t, c, cat))
            
            # Preview snippet
            snippet = (content[:32] + "...") if len(content) > 32 else content
            snippet = snippet.replace("\n", " ")
            lbl_snip = ctk.CTkLabel(card, text=snippet, font=ctk.CTkFont(size=11), text_color="#8b8c9d", anchor="w")
            lbl_snip.pack(fill="x", padx=12, pady=(0, 6))
            lbl_snip.bind("<Button-1>", lambda e, nid=note_id, t=title, c=content, cat=category: self.view_note(nid, t, c, cat))
            
            # Footer row (category badge)
            badge_frame = ctk.CTkFrame(card, fg_color="transparent")
            badge_frame.pack(fill="x", padx=12, pady=(0, 10))
            badge_frame.bind("<Button-1>", lambda e, nid=note_id, t=title, c=content, cat=category: self.view_note(nid, t, c, cat))
            
            cat_badge = ctk.CTkFrame(badge_frame, fg_color="#1e2132", corner_radius=6, border_color="#2b2e42", border_width=1)
            cat_badge.pack(side="left")
            
            badge_lbl = ctk.CTkLabel(cat_badge, text=category, font=ctk.CTkFont(size=9, weight="bold"), text_color="#00f2fe", padx=6, pady=2)
            badge_lbl.pack()
            badge_lbl.bind("<Button-1>", lambda e, nid=note_id, t=title, c=content, cat=category: self.view_note(nid, t, c, cat))

    def view_note(self, note_id, title, content, category):
        self.current_note_id = note_id
        
        # Load in editor
        self.title_entry.delete(0, 'end')
        self.title_entry.insert(0, title)
        
        self.content_textbox.delete("1.0", "end")
        self.content_textbox.insert("1.0", content)
        
        self.note_category.set(category)
        
        # Redraw notes to update active highlighting
        self.load_notes()

    def trigger_autosave(self, event=None):
        self.auto_save_status.configure(text="Typing...", text_color="#ffb703")
        if self.auto_save_job:
            self.after_cancel(self.auto_save_job)
        self.auto_save_job = self.after(1200, lambda: self.save_note(show_toast=False))

    def save_note(self, show_toast=True):
        title = self.title_entry.get().strip()
        content = self.content_textbox.get("1.0", "end-1c").strip()
        category = self.note_category.get()
        
        if not title:
            if show_toast:
                notifications.show_warning(self, "Please enter a note title first.")
            return
            
        if self.current_note_id:
            # Update existing
            db.update_note(self.current_note_id, title, content, category)
            if show_toast:
                notifications.show_success(self, "Note updated successfully!")
        else:
            # Insert new
            self.current_note_id = db.add_note(self.user_id, title, content, category)
            if show_toast:
                notifications.show_success(self, "New note saved successfully!")
                
        self.auto_save_status.configure(text="All notes saved", text_color="#8b8c9d")
        self.load_notes()

    def clear_editor(self):
        self.current_note_id = None
        self.title_entry.delete(0, 'end')
        self.title_entry.insert(0, "")
        self.content_textbox.delete("1.0", "end")
        self.note_category.set("General")
        self.load_notes()

    def delete_note(self, note_id):
        if not note_id:
            notifications.show_warning(self, "No note is currently loaded to delete.")
            return
            
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this note?"):
            db.delete_note(note_id)
            self.clear_editor()
            notifications.show_success(self, "Note deleted successfully.")

    def export_note(self):
        title = self.title_entry.get().strip()
        content = self.content_textbox.get("1.0", "end-1c").strip()
        
        if not title:
            notifications.show_error(self, "Cannot export empty note.")
            return
            
        filepath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if filepath:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"Title: {title}\nCategory: {self.note_category.get()}\n" + "="*30 + f"\n\n{content}")
            notifications.show_success(self, "Note exported successfully as TXT.")
