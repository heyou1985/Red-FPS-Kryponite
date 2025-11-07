#!/usr/bin/env python
"""
Ultimate Windows Performance & Privacy Tool - No Console Version
This is a launcher that runs without showing a console window.
"""
import subprocess
import sys
import os

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
main_script = os.path.join(script_dir, "Ultimate_Performance_Tool.py")

# Run the main script with pythonw (no console)
if os.path.exists(main_script):
    subprocess.Popen([sys.executable, main_script])
else:
    import tkinter as tk
    from tkinter import messagebox
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(
        "File Not Found",
        f"Could not find:\n{main_script}\n\n"
        "Make sure Ultimate_Performance_Tool.py is in the same folder."
    )
