import customtkinter as ctk
import datetime
from database import db
import notifications

class TodoFrame(ctk.CTkFrame):
    def __init__(self, master, user_id):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.user_id = user_id
        
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # --- 1. PROGRESS HEADER TRACKER ---
        self.progress_frame = ctk.CTkFrame(self, fg_color="#181a26", corner_radius=16, border_color="#2b2e42", border_width=1)
        self.progress_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        # Grid inside progress frame
        self.progress_frame.grid_columnconfigure(0, weight=1)
        
        self.lbl_progress = ctk.CTkLabel(
            self.progress_frame, 
            text="0 of 0 tasks completed (0%)", 
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#ffffff"
        )
        self.lbl_progress.grid(row=0, column=0, padx=20, pady=(12, 6), sticky="w")
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, height=8, progress_color="#28a749", fg_color="#2b2e42")
        self.progress_bar.grid(row=1, column=0, padx=20, pady=(0, 15), sticky="ew")
        self.progress_bar.set(0)
        
        # --- 2. INPUT AREA CONTAINER ---
        self.input_frame = ctk.CTkFrame(self, fg_color="#181a26", corner_radius=16, border_color="#2b2e42", border_width=1)
        self.input_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        # Configure input columns
        self.input_frame.grid_columnconfigure(0, weight=1) # Task description entry
        
        # Task Description Entry
        self.task_entry = ctk.CTkEntry(
            self.input_frame, 
            placeholder_text="Write a new task description...", 
            height=38,
            corner_radius=8,
            border_color="#2b2e42",
            fg_color="#1e2132"
        )
        self.task_entry.grid(row=0, column=0, padx=(15, 8), pady=15, sticky="ew")
        self.task_entry.bind("<Return>", lambda e: self.add_task())
        
        # Due Date Entry
        self.due_entry = ctk.CTkEntry(
            self.input_frame, 
            placeholder_text="Due: YYYY-MM-DD", 
            height=38,
            width=130,
            corner_radius=8,
            border_color="#2b2e42",
            fg_color="#1e2132"
        )
        self.due_entry.grid(row=0, column=1, padx=4, pady=15)
        # Prepopulate with today's date format as helper
        today_str = datetime.datetime.now().strftime("%Y-%m-%d")
        self.due_entry.insert(0, today_str)
        
        # Priority drop down selection
        self.priorities = ["Low", "Medium", "High"]
        self.priority_dropdown = ctk.CTkOptionMenu(
            self.input_frame,
            values=self.priorities,
            height=38,
            width=90,
            fg_color="#7f00ff",
            button_color="#6200c8",
            button_hover_color="#5000a5"
        )
        self.priority_dropdown.grid(row=0, column=2, padx=4, pady=15)
        self.priority_dropdown.set("Medium")
        
        # Add Task Button
        self.add_btn = ctk.CTkButton(
            self.input_frame, 
            text="Add Task", 
            width=100, 
            height=38,
            corner_radius=8,
            fg_color="#7f00ff",
            hover_color="#6200c8",
            font=ctk.CTkFont(weight="bold"),
            command=self.add_task
        )
        self.add_btn.grid(row=0, column=3, padx=(4, 15), pady=15)
        
        # --- 3. SCROLLABLE TASKS LIST CONTAINER ---
        self.list_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.list_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="nsew")
        
        self.load_tasks()

    def load_tasks(self):
        # Clear frame children
        for widget in self.list_frame.winfo_children():
            widget.destroy()
            
        tasks = db.get_tasks(self.user_id)
        
        # Track counts for progress header
        total_count = len(tasks)
        completed_count = sum(1 for t in tasks if t[2] == 1)
        
        # Update progress header widgets
        if total_count > 0:
            pct = int((completed_count / total_count) * 100)
            self.lbl_progress.configure(text=f"{completed_count} of {total_count} tasks completed ({pct}%)")
            self.progress_bar.set(completed_count / total_count)
        else:
            self.lbl_progress.configure(text="0 of 0 tasks completed (0%)")
            self.progress_bar.set(0)
            
        if not tasks:
            empty_lbl = ctk.CTkLabel(self.list_frame, text="No tasks on your agenda. Enjoy your free time!", font=ctk.CTkFont(size=13, slant="italic"), text_color="#8b8c9d")
            empty_lbl.pack(pady=40)
            return
            
        # Draw categories separation
        active_tasks = [t for t in tasks if t[2] == 0]
        completed_tasks = [t for t in tasks if t[2] == 1]
        
        # 1. Active Section Header
        if active_tasks:
            lbl_active_hdr = ctk.CTkLabel(self.list_frame, text=f"Active Tasks ({len(active_tasks)})", font=ctk.CTkFont(size=14, weight="bold"), text_color="#ffffff", anchor="w")
            lbl_active_hdr.pack(fill="x", padx=10, pady=(10, 5))
            
            for task in active_tasks:
                task_id, task_text, is_completed, priority, due_date = task
                self.create_task_widget(task_id, task_text, is_completed, priority, due_date)
                
        # 2. Completed Section Header
        if completed_tasks:
            lbl_comp_hdr = ctk.CTkLabel(self.list_frame, text=f"Completed Tasks ({len(completed_tasks)})", font=ctk.CTkFont(size=14, weight="bold"), text_color="#8b8c9d", anchor="w")
            lbl_comp_hdr.pack(fill="x", padx=10, pady=(15, 5))
            
            for task in completed_tasks:
                task_id, task_text, is_completed, priority, due_date = task
                self.create_task_widget(task_id, task_text, is_completed, priority, due_date)

    def create_task_widget(self, task_id, task_text, is_completed, priority, due_date):
        task_frame = ctk.CTkFrame(
            self.list_frame, 
            fg_color="#181a26" if not is_completed else "#10121d",
            border_color="#2b2e42" if not is_completed else "#1e2132",
            border_width=1,
            corner_radius=10
        )
        task_frame.pack(fill="x", pady=4, padx=5)
        
        checkbox_var = ctk.IntVar(value=is_completed)
        
        def on_toggle():
            db.toggle_task(task_id, checkbox_var.get())
            self.load_tasks()
            
        checkbox = ctk.CTkCheckBox(
            task_frame, 
            text="", 
            variable=checkbox_var, 
            command=on_toggle,
            width=24,
            checkbox_width=20,
            checkbox_height=20
        )
        checkbox.pack(side="left", padx=(15, 0), pady=12)
        
        # Details container
        details = ctk.CTkFrame(task_frame, fg_color="transparent")
        details.pack(side="left", fill="both", expand=True, padx=10, pady=8)
        
        # Text alignment
        lbl_task = ctk.CTkLabel(
            details, 
            text=task_text, 
            font=ctk.CTkFont(size=13, weight="bold", overstrike=is_completed),
            text_color="#ffffff" if not is_completed else "#8b8c9d",
            anchor="w",
            justify="left",
            wraplength=350
        )
        lbl_task.pack(anchor="w")
        
        # Meta indicators row: Priority badge + due date
        meta_row = ctk.CTkFrame(details, fg_color="transparent")
        meta_row.pack(anchor="w", fill="x", pady=(2, 0))
        
        # Priority Badge Color
        badge_colors = {
            "High": ("#eb4034", "#ffebee"),
            "Medium": ("#ffb703", "#fff8e1"),
            "Low": ("#8b8c9d", "#f5f5f7")
        }
        color = badge_colors.get(priority, ("#ffb703", "#fff8e1"))
        
        priority_badge = ctk.CTkFrame(meta_row, fg_color="#1e2132" if not is_completed else "#141624", corner_radius=6, border_color=color[0], border_width=1)
        priority_badge.pack(side="left")
        
        priority_lbl = ctk.CTkLabel(priority_badge, text=priority, font=ctk.CTkFont(size=9, weight="bold"), text_color=color[0], padx=6, pady=1)
        priority_lbl.pack()
        
        # Due Date info
        if due_date:
            due_lbl = ctk.CTkLabel(meta_row, text=f"📅  Due: {due_date}", font=ctk.CTkFont(size=11), text_color="#8b8c9d" if not is_completed else "#555666", padx=10)
            due_lbl.pack(side="left")
            
        # Trash delete button
        del_btn = ctk.CTkButton(
            task_frame, 
            text="🗑️", 
            width=32, 
            height=32, 
            corner_radius=8,
            fg_color="transparent", 
            hover_color="#eb4034",
            text_color="#eb4034",
            command=lambda i=task_id: self.delete_task(i)
        )
        del_btn.pack(side="right", padx=15, pady=12)

    def add_task(self):
        task_text = self.task_entry.get().strip()
        due_date = self.due_entry.get().strip()
        priority = self.priority_dropdown.get()
        
        if not task_text:
            notifications.show_warning(self, "Please input a task description.")
            return
            
        # Basic due date format validator
        if due_date:
            if not re.match(r'^\d{4}-\d{2}-\d{2}$', due_date):
                notifications.show_error(self, "Invalid date format. Use YYYY-MM-DD.")
                return
                
        db.add_task(self.user_id, task_text, priority=priority, due_date=due_date)
        
        # Clear task entry but keep date helper for quick entries
        self.task_entry.delete(0, 'end')
        
        self.load_tasks()
        notifications.show_success(self, "Task added successfully!")

    def delete_task(self, task_id):
        db.delete_task(task_id)
        self.load_tasks()
        notifications.show_success(self, "Task deleted.")
