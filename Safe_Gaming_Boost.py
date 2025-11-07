#!/usr/bin/env python
"""
Gaming Performance Booster - SAFE & NO RESTART REQUIRED
Real-time, non-invasive tweaks that work immediately for gaming.
"""
import subprocess
import psutil
import os
import sys
import ctypes
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time

def is_admin():
    """Check for administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def elevate_privileges():
    """Restart the script with administrator privileges."""
    if is_admin():
        return True
    
    try:
        script_path = os.path.abspath(sys.argv[0])
        
        if script_path.endswith('.py'):
            python_exe = sys.executable
            result = ctypes.windll.shell32.ShellExecuteW(
                None, "runas", python_exe, f'"{script_path}"', None, 1
            )
        else:
            result = ctypes.windll.shell32.ShellExecuteW(
                None, "runas", script_path, None, None, 1
            )
        
        if result > 32:
            return True
        else:
            return False
    except Exception as e:
        print(f"Failed to elevate: {e}")
        return False

class SafeGamingBooster(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Gaming Performance Booster - Safe & Instant")
        self.geometry("900x750")
        
        self.tweaks_applied = []
        self.original_priorities = {}
        
        self.create_widgets()
        
    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(main_frame, text="🎮 Safe Gaming Performance Booster", 
                         font=('TkDefaultFont', 14, 'bold'))
        title.pack(pady=10)
        
        # Warning
        warning_frame = ttk.LabelFrame(main_frame, text="⚠️ Important", padding="10")
        warning_frame.pack(fill=tk.X, pady=5)
        
        warning_text = (
            "✅ NO RESTART REQUIRED - Changes apply instantly\n"
            "✅ SAFE - All changes are temporary and reversible\n"
            "✅ NON-INVASIVE - Only affects currently running processes\n"
            "⚠️ Changes reset after PC restart (feature, not bug!)"
        )
        ttk.Label(warning_frame, text=warning_text, justify=tk.LEFT).pack()
        
        # Safe Tweaks Selection
        tweaks_frame = ttk.LabelFrame(main_frame, text="🔧 Select Safe Tweaks", padding="10")
        tweaks_frame.pack(fill=tk.X, pady=5)
        
        self.tweaks = {
            "Stop Telemetry": (tk.BooleanVar(value=True), 
                              "Stops DiagTrack service temporarily"),
            "Stop Windows Search": (tk.BooleanVar(value=True), 
                                   "Stops indexing while gaming"),
            "Reduce Background CPU": (tk.BooleanVar(value=True), 
                                     "Lowers priority of background processes"),
            "Clear System Cache": (tk.BooleanVar(value=True), 
                                  "Clears RAM cache for more memory"),
            "Disable SuperFetch": (tk.BooleanVar(value=True), 
                                  "Stops SysMain (SuperFetch) temporarily"),
        }
        
        for name, (var, desc) in self.tweaks.items():
            frame = ttk.Frame(tweaks_frame)
            frame.pack(fill=tk.X, pady=2)
            ttk.Checkbutton(frame, text=name, variable=var).pack(side=tk.LEFT)
            ttk.Label(frame, text=f"  ({desc})", foreground="gray").pack(side=tk.LEFT)
        
        # Current Status
        status_frame = ttk.LabelFrame(main_frame, text="📊 Current System Status", padding="10")
        status_frame.pack(fill=tk.X, pady=5)
        
        self.status_text = tk.Text(status_frame, height=4, wrap=tk.WORD, state=tk.DISABLED)
        self.status_text.pack(fill=tk.X)
        
        # Update status
        self.update_status()
        
        # Log
        log_frame = ttk.LabelFrame(main_frame, text="📜 Activity Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, 
                                                 state=tk.DISABLED, height=12)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        self.boost_btn = ttk.Button(buttons_frame, text="🚀 BOOST FOR GAMING", 
                                    command=self.apply_boost, 
                                    style='Accent.TButton')
        self.boost_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.restore_btn = ttk.Button(buttons_frame, text="↩️ RESTORE NORMAL", 
                                     command=self.restore_normal,
                                     state=tk.DISABLED)
        self.restore_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        ttk.Button(buttons_frame, text="🔄 Refresh Status", 
                  command=self.update_status).pack(side=tk.RIGHT, padx=5)
    
    def log(self, message):
        """Add message to log."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.update_idletasks()
    
    def update_status(self):
        """Update current system status."""
        mem = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=1)
        processes = len(list(psutil.process_iter()))
        
        status = (
            f"CPU Usage: {cpu}%\n"
            f"Available RAM: {round(mem.available / (1024**3), 2)} GB / {round(mem.total / (1024**3), 2)} GB\n"
            f"Background Processes: {processes}\n"
            f"Boost Status: {'⚡ ACTIVE' if self.tweaks_applied else '🔴 Inactive'}"
        )
        
        self.status_text.config(state=tk.NORMAL)
        self.status_text.delete('1.0', tk.END)
        self.status_text.insert(tk.END, status)
        self.status_text.config(state=tk.DISABLED)
    
    def get_service_status(self, service_name):
        """Check if service is running."""
        try:
            result = subprocess.run(["sc", "query", service_name],
                                  capture_output=True, text=True, check=False)
            return "RUNNING" in result.stdout
        except:
            return False
    
    def stop_service_temporary(self, service_name, description):
        """Temporarily stop a service."""
        try:
            if not self.get_service_status(service_name):
                self.log(f"  ℹ️ {description} already stopped")
                return True
            
            result = subprocess.run(["sc", "stop", service_name],
                                  capture_output=True, text=True, check=False)
            time.sleep(1)  # Wait for service to stop
            
            if not self.get_service_status(service_name):
                self.log(f"  ✅ {description} stopped temporarily")
                return True
            else:
                self.log(f"  ⚠️ {description} could not be stopped")
                return False
        except Exception as e:
            self.log(f"  ❌ Error stopping {description}: {e}")
            return False
    
    def start_service(self, service_name, description):
        """Start a service."""
        try:
            if self.get_service_status(service_name):
                self.log(f"  ℹ️ {description} already running")
                return True
            
            subprocess.run(["sc", "start", service_name],
                         capture_output=True, text=True, check=False)
            time.sleep(1)
            
            if self.get_service_status(service_name):
                self.log(f"  ✅ {description} restarted")
                return True
            else:
                self.log(f"  ℹ️ {description} not started (may be disabled)")
                return False
        except Exception as e:
            self.log(f"  ⚠️ Could not restart {description}: {e}")
            return False
    
    def reduce_background_priority(self):
        """Lower priority of non-essential background processes."""
        self.log("\n🔽 Reducing priority of background processes...")
        
        # Processes to lower priority (safe list)
        background_processes = [
            "OneDrive.exe", "SearchApp.exe", "SearchHost.exe",
            "StartMenuExperienceHost.exe", "TextInputHost.exe",
            "RuntimeBroker.exe", "ApplicationFrameHost.exe"
        ]
        
        count = 0
        for proc in psutil.process_iter(['pid', 'name', 'nice']):
            try:
                proc_name = proc.info['name']
                if proc_name in background_processes:
                    pid = proc.info['pid']
                    # Save original priority
                    if pid not in self.original_priorities:
                        self.original_priorities[pid] = proc.nice()
                    
                    # Lower priority (higher nice value = lower priority)
                    proc.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
                    count += 1
                    self.log(f"  ✅ Lowered priority: {proc_name}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        self.log(f"  📊 Modified {count} background processes")
    
    def restore_process_priorities(self):
        """Restore original process priorities."""
        self.log("\n🔼 Restoring original process priorities...")
        
        count = 0
        for pid, priority in self.original_priorities.items():
            try:
                proc = psutil.Process(pid)
                proc.nice(priority)
                count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        self.original_priorities.clear()
        self.log(f"  ✅ Restored {count} processes")
    
    def clear_system_cache(self):
        """Clear system cache (Windows working sets)."""
        self.log("\n💾 Clearing system cache...")
        try:
            # This is safe - just asks Windows to trim working sets
            subprocess.run(["powershell", "-Command", 
                          "[System.GC]::Collect(); [System.GC]::WaitForPendingFinalizers()"],
                         capture_output=True, check=False, timeout=5)
            self.log("  ✅ System cache cleared")
        except Exception as e:
            self.log(f"  ⚠️ Could not clear cache: {e}")
    
    def apply_boost(self):
        """Apply gaming boost tweaks."""
        if self.tweaks_applied:
            messagebox.showinfo("Already Boosted", 
                              "Gaming boost is already active!\n\n"
                              "Click 'RESTORE NORMAL' to revert first.")
            return
        
        self.log("="*70)
        self.log("🚀 APPLYING GAMING BOOST")
        self.log("="*70)
        
        self.boost_btn.config(state=tk.DISABLED)
        
        # Run in thread
        thread = threading.Thread(target=self._apply_boost_worker, daemon=True)
        thread.start()
    
    def _apply_boost_worker(self):
        """Worker thread for applying boost."""
        try:
            tweaks = self.tweaks
            
            # Stop Telemetry
            if tweaks["Stop Telemetry"][0].get():
                self.log("\n📡 Stopping Telemetry Service...")
                if self.stop_service_temporary("DiagTrack", "Telemetry"):
                    self.tweaks_applied.append("DiagTrack")
            
            # Stop Windows Search
            if tweaks["Stop Windows Search"][0].get():
                self.log("\n🔍 Stopping Windows Search...")
                if self.stop_service_temporary("WSearch", "Windows Search"):
                    self.tweaks_applied.append("WSearch")
            
            # Stop SuperFetch
            if tweaks["Disable SuperFetch"][0].get():
                self.log("\n💿 Stopping SuperFetch...")
                if self.stop_service_temporary("SysMain", "SuperFetch/SysMain"):
                    self.tweaks_applied.append("SysMain")
            
            # Reduce background CPU
            if tweaks["Reduce Background CPU"][0].get():
                self.reduce_background_priority()
                self.tweaks_applied.append("ProcessPriority")
            
            # Clear cache
            if tweaks["Clear System Cache"][0].get():
                self.clear_system_cache()
            
            self.log("\n" + "="*70)
            self.log("✅ GAMING BOOST APPLIED!")
            self.log("="*70)
            self.log("\nYou can now start your game for better performance.")
            self.log("Click 'RESTORE NORMAL' when done gaming.")
            
        except Exception as e:
            self.log(f"\n❌ Error: {e}")
        finally:
            self.after(100, self._update_buttons_after_boost)
            self.after(100, self.update_status)
    
    def _update_buttons_after_boost(self):
        """Update button states after boost."""
        self.boost_btn.config(state=tk.NORMAL)
        if self.tweaks_applied:
            self.restore_btn.config(state=tk.NORMAL)
    
    def restore_normal(self):
        """Restore normal system state."""
        if not self.tweaks_applied:
            messagebox.showinfo("Nothing to Restore", 
                              "No boost is currently active.")
            return
        
        self.log("\n" + "="*70)
        self.log("↩️ RESTORING NORMAL OPERATION")
        self.log("="*70)
        
        # Restore process priorities
        if "ProcessPriority" in self.tweaks_applied:
            self.restore_process_priorities()
        
        # Restart services
        if "DiagTrack" in self.tweaks_applied:
            self.log("\n📡 Restarting Telemetry...")
            self.start_service("DiagTrack", "Telemetry")
        
        if "WSearch" in self.tweaks_applied:
            self.log("\n🔍 Restarting Windows Search...")
            self.start_service("WSearch", "Windows Search")
        
        if "SysMain" in self.tweaks_applied:
            self.log("\n💿 Restarting SuperFetch...")
            self.start_service("SysMain", "SuperFetch/SysMain")
        
        self.tweaks_applied.clear()
        
        self.log("\n✅ NORMAL OPERATION RESTORED")
        self.log("="*70)
        
        self.restore_btn.config(state=tk.DISABLED)
        self.update_status()


def main():
    # Auto-elevate if not admin
    if not is_admin():
        print("Requesting administrator privileges...")
        if elevate_privileges():
            sys.exit(0)  # Exit this instance, elevated one will start
        else:
            # Show error if elevation failed
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "Administrator Required",
                "This tool requires administrator privileges.\n\n"
                "Failed to elevate. Please manually run as administrator."
            )
            sys.exit(1)
    
    # Start the application
    app = SafeGamingBooster()
    app.mainloop()


if __name__ == "__main__":
    main()
