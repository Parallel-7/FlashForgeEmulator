#!/usr/bin/env python3
"""
Simple startup script for the FlashForge Emulator
"""
import sys
import os
import tkinter as tk

# Add the current directory to path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from emulator.printer import PrinterEmulator
    from ui.main_window import MainWindow
    import ttkbootstrap as ttk
except ImportError as e:
    print(f"Import error: {e}")
    print("\nPlease install required dependencies:")
    print("pip install -r requirements.txt")
    sys.exit(1)

def main():
    """Main application entry point"""
    # Create the main window
    root = ttk.Window(themename="darkly")

    # Create printer emulator instance
    emulator = PrinterEmulator()

    # Create UI
    app = MainWindow(root, emulator)

    # Start the UI
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nShutting down emulator...")
    except Exception as e:
        print(f"Error running application: {e}")
        return 1

    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)