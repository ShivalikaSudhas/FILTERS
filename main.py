"""
main.py - EdgeCam Application Launcher
---------------------------------------
Bootstraps the Tkinter event loop, sets Windows high-DPI awareness,
loads window icons, and initializes the EdgeCam GUI application.
"""

import sys
import os
import ctypes
import tkinter as tk
from gui import EdgeCamGUI


def enable_windows_dpi_awareness():
    """Enables crisp high-DPI scaling on Windows displays."""
    if sys.platform == "win32":
        try:
            # Per-monitor DPI awareness
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass


def main():
    enable_windows_dpi_awareness()

    root = tk.Tk()
    
    # Load window icon if present
    icon_path = os.path.join("assets", "icon.ico")
    if os.path.exists(icon_path):
        try:
            root.iconbitmap(icon_path)
        except Exception:
            pass

    app = EdgeCamGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
