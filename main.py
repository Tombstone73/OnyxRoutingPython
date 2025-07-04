#!/usr/bin/env python3
"""
Titan Automation Suite - Entry Point
Main application launcher
"""
import sys
import os

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main entry point for Titan Automation Suite"""
    try:
        print("Starting Titan Automation Suite...")
        
        # Import and create the main application
        from ui.main_window import TitanAutomationApp
        
        app = TitanAutomationApp()
        print("Application created successfully, starting mainloop...")
        app.mainloop()
        
    except Exception as e:
        print(f"Failed to start application: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
