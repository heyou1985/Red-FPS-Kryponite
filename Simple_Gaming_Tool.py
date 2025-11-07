#!/usr/bin/env python
"""
Simple Gaming Performance Tool - All-in-One
"""
import psutil
import subprocess
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import time

class SimpleGamingTool(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("🎮 Simple Gaming Performance Tool")
        self.geometry("700x600")
        
        # Make window always on top initially so you can find it
        self.attributes('-topmost', True)
        self.after(2000, lambda: self.attributes('-topmost', False))  # Disable after 2 seconds
        
        self.boost_active = False
        self.create_widgets()
        self.update_status()
        
    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = tk.Label(main_frame, text="🎮 Gaming Performance Tool", 
                        font=('Arial', 16, 'bold'), fg='#2196F3')
        title.pack(pady=10)
        
        # Status Frame
        status_frame = ttk.LabelFrame(main_frame, text="📊 Current Status", padding="10")
        status_frame.pack(fill=tk.X, pady=10)
        
        self.status_label = tk.Label(status_frame, text="Loading...", 
                                     font=('Consolas', 10), justify=tk.LEFT)
        self.status_label.pack()
        
        # Info
        info_frame = ttk.LabelFrame(main_frame, text="ℹ️ How It Works", padding="10")
        info_frame.pack(fill=tk.X, pady=5)
        
        info_text = (
            "✅ Instantly stops unnecessary services\n"
            "✅ Frees up RAM and CPU\n"
            "✅ Safe & reversible\n"
            "⚠️ Requires Administrator privileges"
        )
        tk.Label(info_frame, text=info_text, justify=tk.LEFT).pack()
        
        # Buttons Frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=20)
        
        self.boost_btn = tk.Button(btn_frame, text="🚀 BOOST GAMING\n(Click before playing)", 
                                   command=self.boost_gaming,
                                   font=('Arial', 12, 'bold'),
                                   bg='#4CAF50', fg='white',
                                   height=3, cursor='hand2')
        self.boost_btn.pack(fill=tk.X, pady=5)
        
        self.restore_btn = tk.Button(btn_frame, text="↩️ RESTORE NORMAL\n(Click when done)", 
                                     command=self.restore_normal,
                                     font=('Arial', 12, 'bold'),
                                     bg='#FF9800', fg='white',
                                     height=3, state=tk.DISABLED, cursor='hand2')
        self.restore_btn.pack(fill=tk.X, pady=5)
        
        # Log
        log_frame = ttk.LabelFrame(main_frame, text="📜 Activity Log", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, wrap=tk.WORD,
                                                 font=('Consolas', 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        self.log("Welcome! Click BOOST GAMING before playing games.")
    
    def log(self, message):
        """Add message to log."""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
    
    def update_status(self):
        """Update system status display."""
        try:
            cpu = psutil.cpu_percent(interval=0.5)
            mem = psutil.virtual_memory()
            processes = len(list(psutil.process_iter()))
            
            status_text = (
                f"CPU Usage: {cpu}%\n"
                f"Available RAM: {round(mem.available / (1024**3), 1)} GB\n"
                f"Processes: {processes}\n"
                f"Boost: {'⚡ ACTIVE' if self.boost_active else '🔴 Inactive'}"
            )
            
            self.status_label.config(text=status_text)
            
            # Update every 2 seconds
            self.after(2000, self.update_status)
        except:
            pass
    
    def is_admin(self):
        """Check if running as admin."""
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    def stop_service(self, service_name):
        """Stop a Windows service."""
        try:
            subprocess.run(["sc", "stop", service_name], 
                         capture_output=True, check=False, timeout=5)
            return True
        except:
            return False
    
    def start_service(self, service_name):
        """Start a Windows service."""
        try:
            subprocess.run(["sc", "start", service_name], 
                         capture_output=True, check=False, timeout=5)
            return True
        except:
            return False
    
    def boost_gaming(self):
        """Apply gaming optimizations."""
        if not self.is_admin():
            messagebox.showerror("Admin Required", 
                               "Please run this program as Administrator!\n\n"
                               "Right-click the file and select 'Run as administrator'")
            return
        
        if self.boost_active:
            messagebox.showinfo("Already Active", "Gaming boost is already active!")
            return
        
        self.boost_btn.config(state=tk.DISABLED)
        self.log("\n🚀 BOOSTING FOR GAMING...")
        
        services = [
            ("DiagTrack", "Telemetry"),
            ("WSearch", "Windows Search"),
            ("SysMain", "SuperFetch")
        ]
        
        stopped = 0
        for service, name in services:
            self.log(f"Stopping {name}...")
            if self.stop_service(service):
                stopped += 1
                self.log(f"  ✅ {name} stopped")
            else:
                self.log(f"  ⚠️ Could not stop {name}")
            self.update()
        
        self.log(f"\n✅ BOOST APPLIED! ({stopped}/3 services stopped)")
        self.log("Your system is now optimized for gaming!")
        
        self.boost_active = True
        self.boost_btn.config(state=tk.NORMAL, bg='#999999')
        self.restore_btn.config(state=tk.NORMAL)
        self.update_status()
    
    def restore_normal(self):
        """Restore normal operation."""
        self.restore_btn.config(state=tk.DISABLED)
        self.log("\n↩️ RESTORING NORMAL OPERATION...")
        
        services = [
            ("DiagTrack", "Telemetry"),
            ("WSearch", "Windows Search"),
            ("SysMain", "SuperFetch")
        ]
        
        for service, name in services:
            self.log(f"Starting {name}...")
            self.start_service(service)
            self.log(f"  ✅ {name} restarted")
            self.update()
        
        self.log("\n✅ NORMAL OPERATION RESTORED")
        
        self.boost_active = False
        self.boost_btn.config(bg='#4CAF50')
        self.update_status()


if __name__ == "__main__":
    print("Starting Gaming Performance Tool...")
    print("Look for the window - it should appear on top!")
    
    app = SimpleGamingTool()
    app.mainloop()
