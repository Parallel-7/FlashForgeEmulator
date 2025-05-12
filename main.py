import tkinter as tk
import ttkbootstrap as ttk
import os

from utils.thumbnail import create_standard_thumbnail
from emulator.printer import PrinterEmulator
from ui.main_window import MainWindow


def main():
    thumbnail_path = create_standard_thumbnail()
    emulator = PrinterEmulator()
    
    if thumbnail_path:
        emulator.set_thumbnail(thumbnail_path)
    
    root = ttk.Window(
        title="FlashForge API Emulator",
        themename="darkly",
        resizable=(True, True)
    )
    
    app = MainWindow(root, emulator)
    emulator.log = app.log
    emulator.server.log = app.log
    root.mainloop()


if __name__ == "__main__":
    main()
