import customtkinter as ctk
import datetime
import wikipedia
import re
import threading
from tkinter import filedialog, messagebox
from PIL import Image
from fpdf import FPDF
from database import db
from voice import VoiceAssistant
from weather import get_weather
import notifications

class ChatBubble(ctk.CTkFrame):
    def __init__(self, master, msg_id, sender, text, timestamp, delete_callback):
        super().__init__(master, fg_color="transparent")
        self.msg_id = msg_id
        self.sender = sender
        self.text = text
        
        # Format timestamp
        # If timestamp is string like "2026-06-21 16:20:00", extract time
        try:
            if " " in timestamp:
                t_part = timestamp.split(" ")[1]
                h, m, s = t_part.split(":")[:3]
                h_val = int(h)
                period = "AM" if h_val < 12 else "PM"
                h_12 = h_val % 12
                if h_12 == 0: h_12 = 12
                self.time_str = f"{h_12}:{m} {period}"
            else:
                self.time_str = timestamp
        except Exception:
            self.time_str = timestamp
            
        self.delete_callback = delete_callback
        
        # Layout
        self.pack(fill="x", pady=8, padx=10)
        
        # Align: user on right, bot on left
        align = "right" if sender == "You" else "left"
        bubble_color = ("#1f1437", "#4b228b") if sender == "You" else ("#1e2132", "#1e2132")
        # Let's adjust self alignment
        self.bubble_inner = ctk.CTkFrame(
            self,
            fg_color=bubble_color[1] if sender == "You" else bubble_color[0],
            corner_radius=14,
            border_color="#7f00ff" if sender == "You" else "#2b2e42",
            border_width=1
        )
        self.bubble_inner.pack(side=align, ipadx=5, ipady=5)
        
        # Render text vs code blocks
        self.render_content()
        
        # Meta info row (timestamp, copy, delete)
        self.meta_frame = ctk.CTkFrame(self.bubble_inner, fg_color="transparent", height=20)
        self.meta_frame.pack(fill="x", padx=10, pady=(2, 0))
        
        lbl_time = ctk.CTkLabel(self.meta_frame, text=self.time_str, font=ctk.CTkFont(size=9), text_color="#8b8c9d")
        lbl_time.pack(side="left")
        
        # Action Buttons
        self.btn_del = ctk.CTkButton(
            self.meta_frame, text="🗑️", width=18, height=18, 
            fg_color="transparent", hover_color="#2b2e42", 
            text_color="#eb4034", font=ctk.CTkFont(size=10),
            command=self.delete_message
        )
        self.btn_del.pack(side="right", padx=(5, 0))
        
        self.btn_copy = ctk.CTkButton(
            self.meta_frame, text="📋", width=18, height=18, 
            fg_color="transparent", hover_color="#2b2e42", 
            text_color="#8b8c9d", font=ctk.CTkFont(size=10),
            command=self.copy_message
        )
        self.btn_copy.pack(side="right")

    def render_content(self):
        # Splits message by triple backticks ``` for coding helper formatting
        parts = self.text.split("```")
        for idx, part in enumerate(parts):
            if idx % 2 == 1:
                # Code Block
                lines = part.strip().split("\n")
                lang = "Code Block"
                code_text = part.strip()
                if lines and lines[0].strip() in ["python", "javascript", "html", "css", "c++", "java", "sql"]:
                    lang = f"{lines[0].strip().title()} Code"
                    code_text = "\n".join(lines[1:])
                
                code_header = ctk.CTkLabel(self.bubble_inner, text=lang, font=ctk.CTkFont(size=10, weight="bold"), text_color="#00f2fe")
                code_header.pack(anchor="w", padx=10, pady=(4, 0))
                
                code_box = ctk.CTkTextbox(
                    self.bubble_inner, 
                    wrap="none", 
                    font=ctk.CTkFont(family="Consolas", size=12), 
                    fg_color="#0a0b12", 
                    border_width=1, 
                    border_color="#2b2e42", 
                    height=130,
                    width=420
                )
                code_box.insert("1.0", code_text)
                code_box.configure(state="disabled")
                code_box.pack(fill="x", padx=10, pady=(2, 6))
            else:
                # Standard Text
                text_content = part.strip()
                if text_content:
                    lbl = ctk.CTkLabel(
                        self.bubble_inner, 
                        text=text_content, 
                        wraplength=440, 
                        justify="left",
                        font=ctk.CTkFont(size=13),
                        text_color="#ffffff" if self.sender == "You" else "#e0e0e6"
                    )
                    lbl.pack(anchor="w", padx=10, pady=5)

    def copy_message(self):
        self.clipboard_clear()
        self.clipboard_append(self.text)
        notifications.show_success(self, "Message copied to clipboard!")

    def delete_message(self):
        self.delete_callback(self.msg_id, self)


class ChatbotFrame(ctk.CTkFrame):
    def __init__(self, master, user_id):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.user_id = user_id
        self.voice_assistant = VoiceAssistant()
        
        # Smart context variables
        self.session_context = [] # List of tuples: (user_msg, bot_msg)
        self.last_subject = ""
        
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Header Controls Frame
        self.controls_frame = ctk.CTkFrame(self, fg_color="#181a26", corner_radius=16, border_color="#2b2e42", border_width=1)
        self.controls_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10), ipady=5)
        self.controls_frame.grid_columnconfigure(1, weight=1)
        
        title_icon_lbl = ctk.CTkLabel(
            self.controls_frame, 
            text="🤖  HireBot AI Assistant", 
            font=ctk.CTkFont(size=16, weight="bold"), 
            text_color="#ffffff"
        )
        title_icon_lbl.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        # Actions Right Aligned
        actions_frame = ctk.CTkFrame(self.controls_frame, fg_color="transparent")
        actions_frame.grid(row=0, column=2, padx=20, pady=10, sticky="e")
        
        self.btn_export_txt = ctk.CTkButton(
            actions_frame, text="Export TXT", width=90, height=32, corner_radius=8,
            fg_color="#1e2132", hover_color="#2b2e42", text_color="#ffffff",
            font=ctk.CTkFont(size=12, weight="bold"), command=self.export_txt
        )
        self.btn_export_txt.pack(side="left", padx=5)
        
        self.btn_export_pdf = ctk.CTkButton(
            actions_frame, text="Export PDF", width=90, height=32, corner_radius=8,
            fg_color="#1e2132", hover_color="#2b2e42", text_color="#ffffff",
            font=ctk.CTkFont(size=12, weight="bold"), command=self.export_pdf
        )
        self.btn_export_pdf.pack(side="left", padx=5)
        
        self.btn_clear = ctk.CTkButton(
            actions_frame, text="Clear Chat", width=90, height=32, corner_radius=8,
            fg_color="#eb4034", hover_color="#c8362b", text_color="#ffffff",
            font=ctk.CTkFont(size=12, weight="bold"), command=self.clear_chat
        )
        self.btn_clear.pack(side="left", padx=5)
        
        # Chat display area
        self.chat_display = ctk.CTkScrollableFrame(self, fg_color="#10121d", corner_radius=16, border_color="#1e2132", border_width=1)
        self.chat_display.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 10))
        
        # Input row
        self.input_container = ctk.CTkFrame(self, fg_color="transparent")
        self.input_container.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))
        self.input_container.grid_columnconfigure(0, weight=1)
        
        self.msg_entry = ctk.CTkEntry(
            self.input_container, 
            placeholder_text="Message HireBot assistant... (Type 'help' to see command options)", 
            height=44,
            corner_radius=10,
            border_color="#2b2e42",
            fg_color="#181a26",
            text_color="#ffffff",
            placeholder_text_color="#8b8c9d"
        )
        self.msg_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.msg_entry.bind("<Return>", lambda e: self.send_message())
        
        # Speech input button
        self.mic_btn = ctk.CTkButton(
            self.input_container, 
            text="🎙️", 
            width=44, 
            height=44, 
            corner_radius=10,
            fg_color="#1e2132",
            hover_color="#2b2e42",
            font=ctk.CTkFont(size=16),
            command=self.voice_input
        )
        self.mic_btn.grid(row=0, column=1, padx=(0, 10))
        
        # Send button
        self.send_btn = ctk.CTkButton(
            self.input_container, 
            text="Send", 
            width=90, 
            height=44, 
            corner_radius=10,
            fg_color="#7f00ff",
            hover_color="#6200c8",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.send_message
        )
        self.send_btn.grid(row=0, column=2)
        
        # Load messages from SQLite database
        self.load_history()
        
        # Show default greeting if blank
        if len(self.chat_display.winfo_children()) == 0:
            self.show_bot_greeting()

    def show_bot_greeting(self):
        t = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.display_message(-1, "HireBot", "Hello! I am your visual AI assistant, here to boost your productivity.\n\nType **help** to explore specialized modules like mathematics, wikipedia searching, coding, and system integrations.", t)

    def display_message(self, msg_id, sender, text, timestamp):
        # Instantiate ChatBubble widget inside scrollframe
        bubble = ChatBubble(self.chat_display, msg_id, sender, text, timestamp, self.delete_individual_message)
        self.scroll_to_bottom()

    def scroll_to_bottom(self):
        # Delay scroll execution slightly so widgets layout completes
        self.after(50, lambda: self.chat_display._parent_canvas.yview_moveto(1.0))

    def load_history(self):
        for widget in self.chat_display.winfo_children():
            widget.destroy()
        history = db.get_chat_history(self.user_id)
        for msg_id, sender, msg, timestamp in history:
            self.display_message(msg_id, sender, msg, timestamp)
        self.scroll_to_bottom()

    def send_message(self):
        msg = self.msg_entry.get().strip()
        if not msg:
            return
            
        self.msg_entry.delete(0, 'end')
        
        # Add to DB & display user message
        t = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user_msg_id = db.add_chat_message(self.user_id, "You", msg)
        self.display_message(user_msg_id, "You", msg, t)
        
        # Add temporary typing indicator bubble
        self.show_typing_indicator()
        
        # Query reply asynchronously in thread to prevent freezing UI
        threading.Thread(target=self.process_response, args=(msg,), daemon=True).start()

    def show_typing_indicator(self):
        self.typing_frame = ctk.CTkFrame(self.chat_display, fg_color="transparent")
        self.typing_frame.pack(fill="x", pady=6, padx=10)
        
        self.typing_bubble = ctk.CTkFrame(self.typing_frame, fg_color="#1e2132", corner_radius=12, border_color="#2b2e42", border_width=1)
        self.typing_bubble.pack(side="left", ipadx=10, ipady=8)
        
        self.typing_lbl = ctk.CTkLabel(self.typing_bubble, text="HireBot is thinking", font=ctk.CTkFont(size=12, slant="italic"), text_color="#8b8c9d")
        self.typing_lbl.pack()
        self.scroll_to_bottom()
        
        self.typing_active = True
        self.animate_typing(0)

    def animate_typing(self, step):
        if not hasattr(self, 'typing_active') or not self.typing_active:
            return
        dots = "." * (step % 4)
        self.typing_lbl.configure(text=f"HireBot is thinking{dots}")
        self.after(400, lambda: self.animate_typing(step + 1))

    def remove_typing_indicator(self):
        self.typing_active = False
        if hasattr(self, 'typing_frame'):
            self.typing_frame.destroy()

    def process_response(self, text):
        # Process bot output
        response = self.get_bot_response(text)
        
        # Add context memory
        self.session_context.append((text, response))
        if len(self.session_context) > 5:
            self.session_context.pop(0)
            
        # Update UI inside main thread safely
        self.after(200, lambda: self.post_bot_message(response))

    def post_bot_message(self, response):
        self.remove_typing_indicator()
        
        # Save to DB & Display
        t = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        bot_msg_id = db.add_chat_message(self.user_id, "HireBot", response)
        self.display_message(bot_msg_id, "HireBot", response, t)
        
        # Speak response
        self.voice_assistant.speak(response)

    def voice_input(self):
        self.msg_entry.delete(0, 'end')
        self.msg_entry.insert(0, "Listening...")
        self.msg_entry.configure(state="disabled")
        self.update()
        
        def _listen_thread():
            text = self.voice_assistant.listen()
            
            def _apply():
                self.msg_entry.configure(state="normal")
                self.msg_entry.delete(0, 'end')
                if not text.startswith("Timeout") and not text.startswith("Could not") and not text.startswith("Microphone error"):
                    self.msg_entry.insert(0, text)
                    self.send_message()
                else:
                    notifications.show_warning(self, text)
            self.after(0, _apply)
            
        threading.Thread(target=_listen_thread, daemon=True).start()

    def get_bot_response(self, text):
        raw_text = text
        text = text.lower().strip()
        
        # 1. HELP command
        if text == "help":
            return (
                "Here are the core tasks I can perform for you:\n\n"
                "• **Calculator**: Type 'calculate <expression>' (e.g. `calculate 4 * (12 + 6)`)\n"
                "• **Wikipedia Search**: Ask 'what is...' or 'who is...' (e.g. `who is Alan Turing?`)\n"
                "• **Weather Updates**: Ask 'weather in <city>' (e.g. `weather in New York`)\n"
                "• **Coding Helper**: Ask me to write code (e.g. `write a python sorting function`)\n"
                "• **System Queries**: Ask for current 'time' or 'date'\n\n"
                "I also retain conversational session context memory!"
            )
            
        # 2. Greetings and Small Talk
        if any(greet in text for greet in ["hello", "hi", "hey", "greetings", "good morning", "good afternoon", "good evening"]):
            return "Greetings! I'm HireBot, your AI Assistant. How can I facilitate your tasks today?"
            
        if "how are you" in text:
            return "I am functioning at peak specifications. Ready to process queries and organize your data!"
            
        if "who are you" in text:
            return "I am HireBot, your workspace automation AI Assistant. I feature task tracking, note writing, password hashing, and visual customization capabilities."

        # 3. System time/date
        if "time" in text:
            now = datetime.datetime.now()
            return f"The local system time is **{now.strftime('%I:%M %p')}**."
            
        if "date" in text:
            now = datetime.datetime.now()
            return f"Today's date is **{now.strftime('%B %d, %Y')}** ({now.strftime('%A')})."

        # 4. Coding Assistant Detection
        coding_triggers = ["write code", "code a", "python function", "python script", "write a program", "write a class"]
        if any(trigger in text for trigger in coding_triggers):
            # Formulate a helpful mock coding response with formatting
            if "sort" in text:
                return (
                    "Certainly! Here is a clean python implementation of the bubble sort algorithm:\n\n"
                    "```python\n"
                    "def bubble_sort(arr):\n"
                    "    n = len(arr)\n"
                    "    for i in range(n):\n"
                    "        for j in range(0, n-i-1):\n"
                    "            if arr[j] > arr[j+1]:\n"
                    "                arr[j], arr[j+1] = arr[j+1], arr[j]\n"
                    "    return arr\n\n"
                    "# Example Usage\n"
                    "numbers = [64, 34, 25, 12, 22, 11, 90]\n"
                    "print(bubble_sort(numbers))\n"
                    "```\n\n"
                    "Bubble sort has a time complexity of O(n²) in the worst case."
                )
            elif "fibonacci" in text:
                return (
                    "Here is a code snippet to calculate Fibonacci numbers using recursion with memoization:\n\n"
                    "```python\n"
                    "def fibonacci(n, memo={}):\n"
                    "    if n in memo: return memo[n]\n"
                    "    if n <= 1: return n\n"
                    "    memo[n] = fibonacci(n-1, memo) + fibonacci(n-2, memo)\n"
                    "    return memo[n]\n\n"
                    "print([fibonacci(i) for i in range(10)])\n"
                    "```"
                )
            else:
                return (
                    "Here is a standard Python template script for your workspace operations:\n\n"
                    "```python\n"
                    "import os\n"
                    "import sys\n\n"
                    "def main():\n"
                    "    print('Initializing local workspace execution...')\n"
                    "    # Your code goes here\n\n"
                    "if __name__ == '__main__':\n"
                    "    main()\n"
                    "```"
                )

        # 5. Calculator parser
        if text.startswith("calculate"):
            expr = raw_text[9:].strip()
            try:
                # Strip unsafe characters
                expr_clean = re.sub(r'[^0-9+\-*/(). ]', '', expr)
                if not expr_clean:
                    return "Please provide an arithmetic expression. Example: `calculate (15 + 5) * 3`"
                result = eval(expr_clean)
                return f"Calculation Result:\n`{expr_clean}` = **{result}**"
            except Exception:
                return "Failed to parse math equation. Please verify brackets and operators (+, -, *, /)."

        # 6. Weather Service wttr.in
        if "weather in" in text:
            city = text.split("weather in")[-1].strip()
            if city:
                return get_weather(city)
            return "Please provide a city. Example: `weather in Chicago`"

        # 7. Smart Session Context Pronoun Resolution
        # If user asks a follow up question like "where is it?" or "who is he?"
        resolved_query = ""
        context_pronouns = ["what is it", "tell me about it", "where is it", "who is he", "who is she", "tell me more"]
        if any(p in text for p in context_pronouns) and self.last_subject:
            resolved_query = self.last_subject
        
        # 8. Wikipedia API
        wiki_patterns = [r"who is ([a-zA-Z0-9\s]+)", r"what is ([a-zA-Z0-9\s]+)", r"tell me about ([a-zA-Z0-9\s]+)"]
        wiki_query = resolved_query
        
        if not wiki_query:
            for pattern in wiki_patterns:
                match = re.search(pattern, text)
                if match:
                    wiki_query = match.group(1).strip()
                    break
                    
        if wiki_query:
            self.last_subject = wiki_query # Store for follow up
            try:
                summary = wikipedia.summary(wiki_query, sentences=2)
                return f"**Wikipedia search summary for '{wiki_query.title()}':**\n\n{summary}"
            except wikipedia.exceptions.DisambiguationError as e:
                # Get top options
                options = ", ".join(e.options[:4])
                return f"Your search term **'{wiki_query}'** has multiple meanings. Did you mean:\n{options}?"
            except wikipedia.exceptions.PageError:
                return f"I couldn't locate any Wikipedia page matching **'{wiki_query}'**."
            except Exception:
                pass

        return "I am not fully trained on that specific inquiry. Try asking for system **time**, **date**, **weather in <city>**, or search wikipedia using **'what is <topic>'**."

    def delete_individual_message(self, msg_id, bubble_widget):
        if msg_id == -1: # Temporary greeting
            bubble_widget.destroy()
            return
            
        db.delete_chat_message(msg_id)
        bubble_widget.destroy()
        notifications.show_success(self, "Message deleted.")

    def clear_chat(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to clear your conversation history?"):
            db.clear_chat_history(self.user_id)
            for widget in self.chat_display.winfo_children():
                widget.destroy()
            self.show_bot_greeting()
            notifications.show_success(self, "Chat history cleared.")

    def export_txt(self):
        history = db.get_chat_history(self.user_id)
        if not history:
            notifications.show_error(self, "No conversation history exists.")
            return
            
        filepath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if filepath:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("HireBot Chat Assistant Export\n" + "="*30 + "\n\n")
                for _, sender, msg, timestamp in history:
                    f.write(f"[{timestamp}] {sender}: {msg}\n\n")
            notifications.show_success(self, "Conversation exported successfully as TXT.")

    def export_pdf(self):
        history = db.get_chat_history(self.user_id)
        if not history:
            notifications.show_error(self, "No conversation history exists.")
            return
            
        filepath = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
        if filepath:
            try:
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(200, 10, txt="HireBot Assistant Chat History", ln=True, align='C')
                pdf.ln(10)
                
                pdf.set_font("Arial", size=12)
                for _, sender, msg, timestamp in history:
                    # Clean encoding values for FPDF basic latin compatibility
                    msg = msg.encode('latin-1', 'replace').decode('latin-1')
                    pdf.set_font("Arial", 'B', 11)
                    pdf.cell(0, 8, txt=f"{sender} [{timestamp}]:", ln=True)
                    pdf.set_font("Arial", size=11)
                    pdf.multi_cell(0, 7, txt=msg)
                    pdf.ln(4)
                    
                pdf.output(filepath)
                notifications.show_success(self, "Conversation exported successfully as PDF.")
            except Exception as e:
                notifications.show_error(self, f"PDF export failed: {e}")
