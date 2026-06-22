import customtkinter as ctk
import qrcode
from PIL import Image
import os
from tkinter import filedialog
import notifications

class QRGeneratorFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure((0, 1), weight=1, uniform="equal")
        
        self.temp_qr_path = "assets/temp_qr.png"
        
        # Ensure assets dir exists
        os.makedirs("assets", exist_ok=True)
        
        # Title
        title_lbl = ctk.CTkLabel(self, text="QR Code Workspace", font=ctk.CTkFont(size=20, weight="bold"), text_color="#ffffff")
        title_lbl.grid(row=0, column=0, columnspan=2, pady=(20, 15), sticky="w", padx=20)
        
        # --- LEFT SIDE PANEL (Generator settings) ---
        self.left_panel = ctk.CTkFrame(self, fg_color="#181a26", corner_radius=16, border_color="#2b2e42", border_width=1)
        self.left_panel.grid(row=1, column=0, padx=(20, 10), pady=(0, 20), sticky="nsew")
        self.left_panel.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(self.left_panel, text="QR Configurations", font=ctk.CTkFont(size=16, weight="bold"), text_color="#ffffff").pack(anchor="w", padx=20, pady=(20, 10))
        
        # Text/URL entry
        ctk.CTkLabel(self.left_panel, text="Data Payload (URL / Text)", font=ctk.CTkFont(size=12, weight="bold"), text_color="#8b8c9d").pack(anchor="w", padx=20, pady=(10, 2))
        self.input_entry = ctk.CTkEntry(
            self.left_panel, 
            placeholder_text="Enter text or website link...", 
            height=38,
            corner_radius=8,
            border_color="#2b2e42",
            fg_color="#1e2132",
            text_color="#ffffff"
        )
        self.input_entry.pack(fill="x", padx=20, pady=(0, 15))
        self.input_entry.bind("<Return>", lambda e: self.generate_qr())
        
        # Dimensions slider
        self.size_lbl = ctk.CTkLabel(self.left_panel, text="Dimensions: 250 x 250 px", font=ctk.CTkFont(size=12, weight="bold"), text_color="#8b8c9d")
        self.size_lbl.pack(anchor="w", padx=20, pady=(10, 2))
        
        self.size_slider = ctk.CTkSlider(
            self.left_panel, 
            from_=150, 
            to=400, 
            number_of_steps=10, 
            progress_color="#7f00ff",
            command=self.update_size_lbl
        )
        self.size_slider.set(250)
        self.size_slider.pack(fill="x", padx=20, pady=(0, 25))
        
        # Generate Button
        self.gen_btn = ctk.CTkButton(
            self.left_panel, 
            text="Compile QR Code", 
            height=40,
            corner_radius=8,
            fg_color="#7f00ff", 
            hover_color="#6200c8",
            font=ctk.CTkFont(weight="bold"),
            command=self.generate_qr
        )
        self.gen_btn.pack(fill="x", padx=20, pady=(0, 20))
        
        # --- RIGHT SIDE PANEL (Live Preview Card) ---
        self.right_panel = ctk.CTkFrame(self, fg_color="#181a26", corner_radius=16, border_color="#2b2e42", border_width=1)
        self.right_panel.grid(row=1, column=1, padx=(10, 20), pady=(0, 20), sticky="nsew")
        self.right_panel.grid_rowconfigure(0, weight=1)
        self.right_panel.grid_columnconfigure(0, weight=1)
        
        # Inner card holder for QR
        self.preview_card = ctk.CTkFrame(self.right_panel, fg_color="#10121d", corner_radius=12, border_color="#1e2132", border_width=1)
        self.preview_card.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="nsew")
        
        self.preview_card.grid_rowconfigure(0, weight=1)
        self.preview_card.grid_columnconfigure(0, weight=1)
        
        self.qr_label = ctk.CTkLabel(self.preview_card, text="No QR Code compiled yet.\nEnter data and click Compile.", font=ctk.CTkFont(size=12, slant="italic"), text_color="#8b8c9d")
        self.qr_label.grid(row=0, column=0, sticky="nsew")
        
        # Save download button
        self.save_btn = ctk.CTkButton(
            self.right_panel, 
            text="Download PNG Image", 
            height=36,
            corner_radius=8,
            fg_color="#1e2132", 
            hover_color="#2b2e42",
            text_color="#ffffff",
            font=ctk.CTkFont(weight="bold"),
            state="disabled",
            command=self.save_qr
        )
        self.save_btn.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")

    def update_size_lbl(self, val):
        self.size_lbl.configure(text=f"Dimensions: {int(val)} x {int(val)} px")

    def generate_qr(self):
        data = self.input_entry.get().strip()
        if not data:
            notifications.show_warning(self, "Please provide payload text/URL.")
            return
            
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        img.save(self.temp_qr_path)
        
        # Load and resize dynamically to fit preview space
        size_dim = int(self.size_slider.get())
        qr_image = ctk.CTkImage(
            light_image=Image.open(self.temp_qr_path),
            dark_image=Image.open(self.temp_qr_path),
            size=(size_dim, size_dim)
        )
                                
        self.qr_label.configure(image=qr_image, text="")
        self.qr_label.image = qr_image
        
        # Enable save button
        self.save_btn.configure(state="normal", fg_color="#00f2fe", text_color="#0d0e15", hover_color="#00c0cb")
        notifications.show_success(self, "QR Code generated successfully!")

    def save_qr(self):
        if not os.path.exists(self.temp_qr_path):
            notifications.show_error(self, "No QR Code is available to save.")
            return
            
        filepath = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Image", "*.png")])
        if filepath:
            try:
                import shutil
                shutil.copy(self.temp_qr_path, filepath)
                notifications.show_success(self, "QR Code downloaded successfully!")
            except Exception as e:
                notifications.show_error(self, f"Download failed: {e}")
