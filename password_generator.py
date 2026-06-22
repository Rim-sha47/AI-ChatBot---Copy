import customtkinter as ctk
import random
import string
import notifications

class PasswordGeneratorFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure((0, 1), weight=1, uniform="equal")
        
        # Title
        title_lbl = ctk.CTkLabel(self, text="Security Keys Workspace", font=ctk.CTkFont(size=20, weight="bold"), text_color="#ffffff")
        title_lbl.grid(row=0, column=0, columnspan=2, pady=(20, 15), sticky="w", padx=20)
        
        # --- LEFT SIDE PANEL (Generator options) ---
        self.left_panel = ctk.CTkFrame(self, fg_color="#181a26", corner_radius=16, border_color="#2b2e42", border_width=1)
        self.left_panel.grid(row=1, column=0, padx=(20, 10), pady=(0, 20), sticky="nsew")
        self.left_panel.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(self.left_panel, text="Character Settings", font=ctk.CTkFont(size=16, weight="bold"), text_color="#ffffff").pack(anchor="w", padx=20, pady=(20, 10))
        
        # Length Slider
        self.len_lbl = ctk.CTkLabel(self.left_panel, text="Password Length: 16", font=ctk.CTkFont(size=12, weight="bold"), text_color="#8b8c9d")
        self.len_lbl.pack(anchor="w", padx=20, pady=(10, 2))
        
        self.len_slider = ctk.CTkSlider(
            self.left_panel, 
            from_=8, 
            to=64, 
            number_of_steps=56, 
            progress_color="#7f00ff",
            command=self.update_len_lbl
        )
        self.len_slider.set(16)
        self.len_slider.pack(fill="x", padx=20, pady=(0, 15))
        
        # Options checkboxes
        self.var_upper = ctk.BooleanVar(value=True)
        self.var_lower = ctk.BooleanVar(value=True)
        self.var_nums = ctk.BooleanVar(value=True)
        self.var_syms = ctk.BooleanVar(value=True)
        
        cb_opts = [
            ("Include Uppercase (A-Z)", self.var_upper),
            ("Include Lowercase (a-z)", self.var_lower),
            ("Include Numbers (0-9)", self.var_nums),
            ("Include Symbols (!@#$*)", self.var_syms)
        ]
        
        for text, var in cb_opts:
            cb = ctk.CTkCheckBox(self.left_panel, text=text, variable=var, font=ctk.CTkFont(size=12), border_color="#2b2e42", fg_color="#7f00ff")
            cb.pack(anchor="w", padx=20, pady=6)
            
        self.gen_btn = ctk.CTkButton(
            self.left_panel, 
            text="Generate Secure Password", 
            height=40,
            corner_radius=8,
            fg_color="#7f00ff", 
            hover_color="#6200c8",
            font=ctk.CTkFont(weight="bold"),
            command=self.generate
        )
        self.gen_btn.pack(fill="x", padx=20, pady=(25, 20))
        
        # --- RIGHT SIDE PANEL (Output card) ---
        self.right_panel = ctk.CTkFrame(self, fg_color="#181a26", corner_radius=16, border_color="#2b2e42", border_width=1)
        self.right_panel.grid(row=1, column=1, padx=(10, 20), pady=(0, 20), sticky="nsew")
        self.right_panel.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(self.right_panel, text="Output Display", font=ctk.CTkFont(size=16, weight="bold"), text_color="#ffffff").pack(anchor="w", padx=20, pady=(20, 10))
        
        # Output field
        self.output_entry = ctk.CTkEntry(
            self.right_panel, 
            font=ctk.CTkFont(family="Consolas", size=18), 
            justify="center", 
            height=46,
            corner_radius=10,
            border_color="#2b2e42",
            fg_color="#10121d",
            text_color="#ffffff"
        )
        self.output_entry.pack(fill="x", padx=20, pady=(15, 20))
        
        # Strength Meter Container
        self.strength_container = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        self.strength_container.pack(fill="x", padx=20, pady=(0, 25))
        
        self.strength_lbl = ctk.CTkLabel(
            self.strength_container, 
            text="Strength: Not Evaluated", 
            font=ctk.CTkFont(size=12, weight="bold"), 
            text_color="#8b8c9d"
        )
        self.strength_lbl.pack(anchor="w", pady=(0, 5))
        
        self.strength_bar = ctk.CTkProgressBar(self.strength_container, height=6, fg_color="#2b2e42")
        self.strength_bar.pack(fill="x")
        self.strength_bar.set(0)
        
        # Copy to clipboard button
        self.copy_btn = ctk.CTkButton(
            self.right_panel, 
            text="Copy to Clipboard", 
            height=38,
            corner_radius=8,
            fg_color="#1e2132", 
            hover_color="#2b2e42",
            text_color="#ffffff",
            font=ctk.CTkFont(weight="bold"),
            state="disabled",
            command=self.copy_to_clip
        )
        self.copy_btn.pack(fill="x", padx=20, pady=(0, 20))

    def update_len_lbl(self, val):
        self.len_lbl.configure(text=f"Password Length: {int(val)}")

    def generate(self):
        length = int(self.len_slider.get())
        
        chars = ""
        types_count = 0
        if self.var_upper.get(): 
            chars += string.ascii_uppercase
            types_count += 1
        if self.var_lower.get(): 
            chars += string.ascii_lowercase
            types_count += 1
        if self.var_nums.get(): 
            chars += string.digits
            types_count += 1
        if self.var_syms.get(): 
            chars += string.punctuation
            types_count += 1
        
        if not chars:
            self.output_entry.delete(0, 'end')
            self.output_entry.insert(0, "Select options!")
            self.evaluate_strength("", 0)
            self.copy_btn.configure(state="disabled")
            return
            
        pwd = "".join(random.choice(chars) for _ in range(length))
        self.output_entry.delete(0, 'end')
        self.output_entry.insert(0, pwd)
        
        # Evaluate strength
        self.evaluate_strength(pwd, types_count)
        
        self.copy_btn.configure(state="normal", fg_color="#00f2fe", text_color="#0d0e15", hover_color="#00c0cb")
        notifications.show_success(self, "Password generated successfully!")

    def evaluate_strength(self, pwd, types_count):
        if not pwd:
            self.strength_lbl.configure(text="Strength: Not Evaluated", text_color="#8b8c9d")
            self.strength_bar.set(0)
            return
            
        length = len(pwd)
        
        # Strength calculation heuristic
        # Base factor from types used
        score = types_count * 20
        # Add factor for length
        score += min(40, (length - 8) * 1.5)
        
        # Clamp score between 0 and 100
        score = max(0, min(100, score))
        
        # Map score to labels & colors
        if score < 40:
            rating = "Weak (Insecure)"
            color = "#eb4034"
        elif score < 70:
            rating = "Medium (Good)"
            color = "#ffb703"
        elif score < 88:
            rating = "High (Strong)"
            color = "#28a749"
        else:
            rating = "Military-Grade (Extreme)"
            color = "#00f5d4"
            
        self.strength_lbl.configure(text=f"Strength: {rating}", text_color=color)
        self.strength_bar.configure(progress_color=color)
        self.strength_bar.set(score / 100)

    def copy_to_clip(self):
        pwd = self.output_entry.get()
        if pwd and pwd != "Select options!":
            self.clipboard_clear()
            self.clipboard_append(pwd)
            notifications.show_success(self, "Password copied to clipboard!")
