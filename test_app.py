import customtkinter as ctk
import sys
from main import App

def test_dashboard():
    print("Initializing App...")
    app = App()
    
    # We bypass splash screen and show auth directly, then trigger login success
    print("Simulating login_success(1, 'testuser')...")
    try:
        app.login_success(1, 'testuser')
        print("Dashboard setup completed successfully!")
        
        # Run update to process tkinter grid events
        app.update()
        print("Tkinter update loop executed without exceptions!")
        
    except Exception as e:
        import traceback
        print("CRITICAL ERROR during dashboard initialization:")
        traceback.print_exc()
        sys.exit(1)
        
    app.destroy()
    print("Test run completed successfully!")

if __name__ == "__main__":
    test_dashboard()
