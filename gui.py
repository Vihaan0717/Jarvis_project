import customtkinter as ctk
from core.logger import get_logger

logger = get_logger("GUI")

# Set the modern dark mode theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class JarvisGUI(ctk.CTk):
    """The visual dashboard for the J.A.R.V.I.S. system."""
    
    def __init__(self):
        super().__init__()
        
        # Configure the main window
        self.title("J.A.R.V.I.S. Core System")
        self.geometry("700x500")
        self.resizable(False, False)
        
        # 1. Main Status Header
        self.status_label = ctk.CTkLabel(
            self, 
            text="SYSTEM STANDBY", 
            font=("Consolas", 28, "bold"), 
            text_color="#00ffcc" # A cool futuristic cyan color
        )
        self.status_label.pack(pady=(20, 5))
        
        # 2. Sub-status (What he is currently doing)
        self.activity_label = ctk.CTkLabel(
            self, 
            text="Waiting for voice input...", 
            font=("Consolas", 14), 
            text_color="#a9a9a9"
        )
        self.activity_label.pack(pady=(0, 20))
        
        # 3. The Live Console Output Box
        self.console_box = ctk.CTkTextbox(
            self, 
            width=600, 
            height=300, 
            font=("Consolas", 14),
            fg_color="#1e1e1e", # Dark gray background
            text_color="#ffffff"
        )
        self.console_box.pack(pady=10)
        self.console_box.insert("0.0", "J.A.R.V.I.S. Visual Interface Initialized...\n")
        self.console_box.configure(state="disabled") # Make it read-only for the user

    def update_console(self, text: str):
        """Safely injects new text into the visual console."""
        self.console_box.configure(state="normal") # Unlock it
        self.console_box.insert("end", text + "\n") # Add the text
        self.console_box.see("end") # Auto-scroll to the bottom
        self.console_box.configure(state="disabled") # Lock it again

    def update_status(self, main_text: str, sub_text: str, color: str = "#00ffcc"):
        """Changes the big header text and color."""
        self.status_label.configure(text=main_text, text_color=color)
        self.activity_label.configure(text=sub_text)

# Test the GUI visually!
if __name__ == "__main__":
    app = JarvisGUI()
    app.mainloop()