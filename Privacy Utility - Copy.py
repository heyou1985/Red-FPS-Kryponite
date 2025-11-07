#!/usr/bin/env python
import subprocess
import winreg as reg
import sys
import ctypes
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import json
import os
from datetime import datetime

# ==============================================================================
# AUTO-ELEVATION FUNCTIONALITY
# ==============================================================================

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
        # Get the current script path
        script_path = os.path.abspath(sys.argv[0])
        
        # Use ShellExecuteW to run with elevated privileges
        if script_path.endswith('.py'):
            # For .py files, use python.exe
            python_exe = sys.executable
            result = ctypes.windll.shell32.ShellExecuteW(
                None, 
                "runas", 
                python_exe,
                f'"{script_path}"',
                None, 
                1  # SW_SHOWNORMAL
            )
        else:
            # For .exe files (compiled with PyInstaller, etc.)
            result = ctypes.windll.shell32.ShellExecuteW(
                None, 
                "runas", 
                script_path,
                None,
                None, 
                1  # SW_SHOWNORMAL
            )
        
        # If successful, result will be > 32
        if result > 32:
            return True
        else:
            return False
            
    except Exception as e:
        print(f"Failed to elevate privileges: {e}")
        return False

def check_and_elevate():
    """Check admin status and elevate if needed."""
    if not is_admin():
        print("Administrator privileges required. Attempting to elevate...")
        
        # Show a message box before elevating
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        response = messagebox.askyesno(
            "Administrator Privileges Required",
            "This application requires administrator privileges to function properly.\n\n"
            "Would you like to restart the application as an administrator?",
            icon='warning'
        )
        
        root.destroy()
        
        if response:
            if elevate_privileges():
                # If elevation was successful, exit this instance
                sys.exit(0)
            else:
                # If elevation failed, show error and exit
                root = tk.Tk()
                root.withdraw()
                messagebox.showerror(
                    "Elevation Failed",
                    "Failed to obtain administrator privileges.\n"
                    "Please manually run this application as an administrator."
                )
                root.destroy()
                sys.exit(1)
        else:
            # User declined elevation
            sys.exit(1)
    
    return True

# Alternative method using UAC prompt without dialog
def auto_elevate_silent():
    """Automatically elevate without user dialog (more aggressive approach)."""
    if not is_admin():
        try:
            # Re-run the current script with admin privileges
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
            sys.exit(0)
        except:
            # If silent elevation fails, fall back to manual request
            return check_and_elevate()
    return True

# ==============================================================================
# ENHANCED SCRIPT BACKEND LOGIC (unchanged from original)
# ==============================================================================

def backup_registry_value(root, path, name, backup_data):
    """Backup a registry value before modifying it."""
    try:
        key = reg.OpenKey(root, path, 0, reg.KEY_READ)
        value, value_type = reg.QueryValueEx(key, name)
        reg.CloseKey(key)
        # Store root key name instead of memory address
        root_name = {
            reg.HKEY_LOCAL_MACHINE: "HKEY_LOCAL_MACHINE",
            reg.HKEY_CURRENT_USER: "HKEY_CURRENT_USER"
        }.get(root, str(root))
        backup_data[f"{root_name}\\{path}\\{name}"] = {"value": value, "type": value_type}
        return True
    except FileNotFoundError:
        root_name = {
            reg.HKEY_LOCAL_MACHINE: "HKEY_LOCAL_MACHINE",
            reg.HKEY_CURRENT_USER: "HKEY_CURRENT_USER"
        }.get(root, str(root))
        backup_data[f"{root_name}\\{path}\\{name}"] = None  # Key doesn't exist
        return True
    except Exception as e:
        return False

def set_registry_key(root, path, name, value_type, value, dry_run=False, log_callback=print, backup_data=None):
    """Enhanced registry setting function with backup capability."""
    if backup_data is not None:
        backup_registry_value(root, path, name, backup_data)
    
    if dry_run:
        log_callback(f"  [DRY-RUN] Would set {path}\\{name} to {value}")
        return True
    
    try:
        # Ensure parent key exists
        key = reg.CreateKeyEx(root, path, 0, reg.KEY_WRITE)
        reg.SetValueEx(key, name, 0, value_type, value)
        reg.CloseKey(key)
        log_callback(f"  [SUCCESS] Set registry key {path}\\{name} to {value}")
        return True
    except PermissionError:
        log_callback(f"  [ERROR] Permission denied accessing {path}\\{name}")
        return False
    except Exception as e:
        log_callback(f"  [ERROR] Failed to set registry key {path}\\{name}: {e}")
        return False

def get_service_status(service_name):
    """Get the current status of a Windows service."""
    try:
        result = subprocess.run(["sc", "query", service_name], 
                              capture_output=True, text=True, check=False)
        if "STATE" in result.stdout:
            if "RUNNING" in result.stdout:
                return "running"
            elif "STOPPED" in result.stdout:
                return "stopped"
            else:
                return "unknown"
        return "not_found"
    except Exception:
        return "error"

def configure_service(service_name, enable=False, dry_run=False, log_callback=print):
    """Enhanced service configuration with status verification."""
    initial_status = get_service_status(service_name)
    if initial_status == "not_found":
        log_callback(f"  [INFO] Service {service_name} does not exist. Skipping.")
        return True
    
    action = "Enabling" if enable else "Disabling"
    start_type = "auto" if enable else "disabled"
    log_callback(f"- {action} service: {service_name} (currently {initial_status})")
    
    if dry_run:
        log_callback(f"  [DRY-RUN] Would set {service_name} startup to '{start_type}' and {'start' if enable else 'stop'} it.")
        return True
    
    try:
        # Stop service if disabling
        if not enable and initial_status == "running":
            subprocess.run(["sc", "stop", service_name], check=False, capture_output=True)
            log_callback(f"  [INFO] Stopped {service_name} service.")
        
        # Configure startup type
        result = subprocess.run(["sc", "config", service_name, f"start={start_type}"], 
                              check=True, capture_output=True, text=True)
        log_callback(f"  [SUCCESS] Set {service_name} startup type to '{start_type}'")
        
        # Start service if enabling
        if enable:
            subprocess.run(["sc", "start", service_name], check=False, capture_output=True)
            final_status = get_service_status(service_name)
            if final_status == "running":
                log_callback(f"  [SUCCESS] Started {service_name} service.")
            else:
                log_callback(f"  [WARNING] {service_name} may not have started properly.")
        
        return True
        
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.decode('utf-8', 'replace').strip() if e.stderr else "Unknown error"
        log_callback(f"  [ERROR] Failed to configure {service_name}: {error_msg}")
        return False
    except Exception as e:
        log_callback(f"  [ERROR] Unexpected error with service {service_name}: {e}")
        return False

# --- Enhanced Configuration Modules (unchanged from original) ---

def configure_defender(enable=False, dry_run=False, log_callback=print, backup_data=None):
    """Enhanced Windows Defender configuration."""
    action = "Enabling" if enable else "Disabling"
    log_callback(f"\n--- {action} Windows Defender ---")
    
    success = True
    
    # PowerShell command for real-time monitoring
    ps_command = ["powershell.exe", "-Command", 
                 f"Set-MpPreference -DisableRealtimeMonitoring {'$false' if enable else '$true'}"]
    
    if dry_run:
        log_callback(f"  [DRY-RUN] Would run: {' '.join(ps_command)}")
    else:
        try:
            result = subprocess.run(ps_command, check=True, capture_output=True, text=True)
            log_callback(f"  [SUCCESS] Real-time monitoring {'enabled' if enable else 'disabled'}.")
        except subprocess.CalledProcessError as e:
            log_callback(f"  [WARNING] Could not set real-time monitoring. May be controlled by policy or Tamper Protection.")
            success = False
        except Exception as e:
            log_callback(f"  [ERROR] PowerShell command failed: {e}")
            success = False
    
    # Registry settings
    if not set_registry_key(reg.HKEY_LOCAL_MACHINE, 
                           r"SOFTWARE\Policies\Microsoft\Windows Defender", 
                           "DisableAntiSpyware", reg.REG_DWORD, 0 if enable else 1, 
                           dry_run, log_callback, backup_data):
        success = False
    
    # Service configuration
    if not configure_service("WinDefend", enable=enable, dry_run=dry_run, log_callback=log_callback):
        success = False
    
    return success

def configure_telemetry(enable=False, full=False, dry_run=False, log_callback=print, backup_data=None):
    """Enhanced telemetry configuration."""
    action = "Enabling" if enable else "Disabling"
    log_callback(f"\n--- {action} Telemetry & Data Collection ---")
    
    success = True
    telemetry_value = 1 if enable else 0
    
    if not set_registry_key(reg.HKEY_LOCAL_MACHINE, 
                           r"SOFTWARE\Policies\Microsoft\Windows\DataCollection", 
                           "AllowTelemetry", reg.REG_DWORD, telemetry_value, 
                           dry_run, log_callback, backup_data):
        success = False
    
    if not configure_service("DiagTrack", enable=enable, dry_run=dry_run, log_callback=log_callback):
        success = False
    
    if not configure_service("dmwappushservice", enable=enable, dry_run=dry_run, log_callback=log_callback):
        success = False
    
    # Full mode handling
    if full and not enable:
        log_callback("- Applying aggressive mode tweak:")
        if not configure_service("wuauserv", enable=False, dry_run=dry_run, log_callback=log_callback):
            success = False
    elif enable:  # Re-enable wuauserv if enabling
        if not configure_service("wuauserv", enable=True, dry_run=dry_run, log_callback=log_callback):
            success = False
    
    return success

def configure_activity_and_recall(enable=False, dry_run=False, log_callback=print, backup_data=None):
    """Enhanced activity tracking and recall configuration."""
    action = "Enabling" if enable else "Disabling"
    log_callback(f"\n--- {action} Activity Tracking, Timeline, and Recall ---")
    
    success = True
    value = 1 if enable else 0
    
    registry_settings = [
        (reg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\WindowsAI", 
         "AllowRecallEnablement", value),
        (reg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\WindowsAI", 
         "DisableSnapshot", 1 if not enable else 0),
        (reg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\System", 
         "PublishUserActivities", value),
        (reg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Privacy", 
         "TailoredExperiencesWithDiagnosticDataEnabled", value)
    ]
    
    for root, path, name, val in registry_settings:
        if not set_registry_key(root, path, name, reg.REG_DWORD, val, 
                               dry_run, log_callback, backup_data):
            success = False
    
    return success

def configure_advertising_and_suggestions(enable=False, dry_run=False, log_callback=print, backup_data=None):
    """Enhanced advertising and suggestions configuration."""
    action = "Enabling" if enable else "Disabling"
    log_callback(f"\n--- {action} Advertising ID & Content Suggestions ---")
    
    success = True
    value = 1 if enable else 0
    
    registry_settings = [
        (reg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\AdvertisingInfo", 
         "Enabled", value),
        (reg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager", 
         "SilentInstalledAppsEnabled", value),
        (reg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager", 
         "SubscribedContent-338389Enabled", value)
    ]
    
    for root, path, name, val in registry_settings:
        if not set_registry_key(root, path, name, reg.REG_DWORD, val, 
                               dry_run, log_callback, backup_data):
            success = False
    
    return success

def configure_cortana(enable=False, dry_run=False, log_callback=print, backup_data=None):
    """Enhanced Cortana configuration."""
    action = "Enabling" if enable else "Disabling"
    log_callback(f"\n--- {action} Cortana ---")
    
    return set_registry_key(reg.HKEY_LOCAL_MACHINE, 
                           r"SOFTWARE\Policies\Microsoft\Windows\Windows Search", 
                           "AllowCortana", reg.REG_DWORD, 1 if enable else 0, 
                           dry_run, log_callback, backup_data)

# ==============================================================================
# ENHANCED GUI APPLICATION (updated with admin status indicator)
# ==============================================================================

class EnhancedApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Update title to show admin status
        admin_status = " [ADMINISTRATOR]" if is_admin() else " [LIMITED USER]"
        self.title("Enhanced Windows Privacy & Performance Utility" + admin_status)
        self.geometry("800x750")
        
        # Set window icon (if available)
        try:
            self.iconbitmap(default='')
        except:
            pass
        
        # --- Class variables ---
        self.action_var = tk.StringVar(value="disable")
        self.dry_run_var = tk.BooleanVar(value=True)
        self.full_mode_var = tk.BooleanVar()
        self.backup_enabled_var = tk.BooleanVar(value=True)
        self.current_backup = {}
        
        self.tasks = {
            "Defender": (tk.BooleanVar(value=True), configure_defender),
            "Telemetry": (tk.BooleanVar(value=True), configure_telemetry),
            "Activity & Recall": (tk.BooleanVar(value=True), configure_activity_and_recall),
            "Advertising": (tk.BooleanVar(value=True), configure_advertising_and_suggestions),
            "Cortana": (tk.BooleanVar(value=True), configure_cortana)
        }
        
        self.create_widgets()

    def create_widgets(self):
        # --- Main frame ---
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Admin status indicator ---
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        admin_text = "✅ Running as Administrator" if is_admin() else "⚠️ NOT running as Administrator"
        status_label = tk.Label(status_frame, text=admin_text, 
                               fg="green" if is_admin() else "red",
                               font=('TkDefaultFont', 9, 'bold'))
        status_label.pack()
        
        if not is_admin():
            warning_label = tk.Label(status_frame, 
                                    text="Some features may not work properly without administrator privileges",
                                    fg="red", font=('TkDefaultFont', 8))
            warning_label.pack()

        # --- Action selection ---
        action_frame = ttk.LabelFrame(main_frame, text="⚙️ Action", padding="10")
        action_frame.pack(fill=tk.X, pady=5)
        
        ttk.Radiobutton(action_frame, text="Disable Features", 
                       variable=self.action_var, value="disable", 
                       command=self.toggle_options).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(action_frame, text="Enable Features (Revert)", 
                       variable=self.action_var, value="enable", 
                       command=self.toggle_options).pack(side=tk.LEFT, padx=5)

        # --- Task selection ---
        tasks_frame = ttk.LabelFrame(main_frame, text="🔧 Select Tweaks to Apply", padding="10")
        tasks_frame.pack(fill=tk.X, pady=5)

        # Add select all/none buttons
        button_frame = ttk.Frame(tasks_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Button(button_frame, text="Select All", command=self.select_all_tasks).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Select None", command=self.select_no_tasks).pack(side=tk.LEFT)

        for name, (var, _) in self.tasks.items():
            ttk.Checkbutton(tasks_frame, text=name, variable=var).pack(anchor=tk.W)

        # --- Enhanced options ---
        options_frame = ttk.LabelFrame(main_frame, text="⚙️ Options", padding="10")
        options_frame.pack(fill=tk.X, pady=5)
        
        self.full_mode_check = ttk.Checkbutton(options_frame, 
                                              text="Aggressive Mode (Disables Windows Update)", 
                                              variable=self.full_mode_var, state=tk.NORMAL)
        self.full_mode_check.pack(anchor=tk.W)
        
        ttk.Checkbutton(options_frame, text="Dry Run (Simulate changes without applying)", 
                       variable=self.dry_run_var).pack(anchor=tk.W)
        
        ttk.Checkbutton(options_frame, text="Create backup before making changes", 
                       variable=self.backup_enabled_var).pack(anchor=tk.W)

        # --- Backup management ---
        backup_frame = ttk.LabelFrame(main_frame, text="💾 Backup Management", padding="10")
        backup_frame.pack(fill=tk.X, pady=5)
        
        backup_buttons = ttk.Frame(backup_frame)
        backup_buttons.pack(fill=tk.X)
        ttk.Button(backup_buttons, text="Save Backup", command=self.save_backup).pack(side=tk.LEFT, padx=5)
        ttk.Button(backup_buttons, text="Load Backup", command=self.load_backup).pack(side=tk.LEFT, padx=5)
        ttk.Button(backup_buttons, text="Restart as Admin", command=self.restart_as_admin).pack(side=tk.RIGHT, padx=5)

        # --- Progress bar ---
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, 
                                          maximum=100, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=5)

        # --- Log display ---
        log_frame = ttk.LabelFrame(main_frame, text="📜 Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, state=tk.DISABLED, height=12)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # --- Control buttons ---
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10, fill=tk.X)
        
        self.apply_button = ttk.Button(button_frame, text="Apply Changes", command=self.start_task_thread)
        self.apply_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        ttk.Button(button_frame, text="Clear Log", command=self.clear_log).pack(side=tk.RIGHT, padx=5)

    def restart_as_admin(self):
        """Manually restart the application as administrator."""
        response = messagebox.askyesno(
            "Restart as Administrator",
            "This will restart the application with administrator privileges.\n\n"
            "Continue?",
            icon='question'
        )
        
        if response:
            if elevate_privileges():
                self.destroy()
                sys.exit(0)
            else:
                messagebox.showerror("Elevation Failed", 
                                   "Failed to restart with administrator privileges.")

    def toggle_options(self):
        """Enable/disable options based on action selection."""
        if self.action_var.get() == "disable":
            self.full_mode_check.config(state=tk.NORMAL)
        else:
            self.full_mode_check.config(state=tk.DISABLED)
            self.full_mode_var.set(False)

    def select_all_tasks(self):
        """Select all tasks."""
        for var, _ in self.tasks.values():
            var.set(True)

    def select_no_tasks(self):
        """Deselect all tasks."""
        for var, _ in self.tasks.values():
            var.set(False)

    def clear_log(self):
        """Clear the log display."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete('1.0', tk.END)
        self.log_text.config(state=tk.DISABLED)

    def save_backup(self):
        """Save current backup to file."""
        if not self.current_backup:
            messagebox.showwarning("No Backup", "No backup data available to save.")
            return
        
        default_filename = f"windows_privacy_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            initialfile=default_filename,
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save Backup"
        )
        
        if filename:
            try:
                backup_with_metadata = {
                    "timestamp": datetime.now().isoformat(),
                    "version": "1.0",
                    "data": self.current_backup
                }
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(backup_with_metadata, f, indent=2)
                messagebox.showinfo("Success", f"Backup saved to:\n{filename}")
                self.log(f"Backup saved to: {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save backup: {e}")

    def load_backup(self):
        """Load backup from file."""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Load Backup"
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    backup_data = json.load(f)
                
                # Handle both old and new backup formats
                if "data" in backup_data:
                    self.current_backup = backup_data["data"]
                    timestamp = backup_data.get("timestamp", "Unknown")
                    messagebox.showinfo("Success", f"Backup loaded from:\n{timestamp}")
                    self.log(f"Backup loaded from: {filename}")
                else:
                    self.current_backup = backup_data
                    messagebox.showinfo("Success", "Backup loaded successfully")
                    self.log(f"Backup loaded from: {filename}")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load backup: {e}")
                self.log(f"[ERROR] Failed to load backup: {e}")
            
    def log(self, message):
        """Thread-safe logging to the text widget."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def update_progress(self, value):
        """Update progress bar."""
        self.progress_var.set(value)

    def start_task_thread(self):
        """Start the configuration task in a new thread."""
        if not is_admin():
            response = messagebox.askyesnocancel(
                "Administrator Privileges Required",
                "This application needs administrator privileges to function properly.\n\n"
                "Click 'Yes' to restart as administrator\n"
                "Click 'No' to continue anyway (some features may not work)\n"
                "Click 'Cancel' to abort",
                icon='warning'
            )
            
            if response is True:  # Yes - restart as admin
                if elevate_privileges():
                    self.destroy()
                    sys.exit(0)
                else:
                    messagebox.showerror("Elevation Failed", "Failed to restart with administrator privileges.")
                    return
            elif response is None:  # Cancel
                return
            # If No, continue with warning

        self.apply_button.config(state=tk.DISABLED, text="Applying...")
        self.clear_log()
        self.update_progress(0)
        
        # Create and start the worker thread
        thread = threading.Thread(target=self.run_tasks, daemon=True)
        thread.start()

    def run_tasks(self):
        """The worker function that runs in a separate thread."""
        is_enable = self.action_var.get() == "enable"
        is_dry_run = self.dry_run_var.get()
        is_full_mode = self.full_mode_var.get()
        create_backup = self.backup_enabled_var.get()
        
        if create_backup and not is_dry_run:
            self.current_backup = {}
        else:
            self.current_backup = None
            
        self.log(f"*** Starting action: '{'ENABLE' if is_enable else 'DISABLE'}' | Dry Run: {is_dry_run} ***")
        
        if not is_admin():
            self.log("WARNING: Running without administrator privileges - some operations may fail.")
        
        selected_tasks = [(name, func) for name, (var, func) in self.tasks.items() if var.get()]
        total_tasks = len(selected_tasks)
        
        if total_tasks == 0:
            self.log("No tasks selected.")
            self.after(100, self.task_finished)
            return
        
        success_count = 0
        
        for i, (name, func) in enumerate(selected_tasks):
            progress = (i / total_tasks) * 100
            self.after(10, lambda p=progress: self.update_progress(p))
            
            try:
                if name == "Telemetry":
                    result = func(enable=is_enable, full=is_full_mode, dry_run=is_dry_run, 
                                log_callback=self.log, backup_data=self.current_backup)
                else:
                    result = func(enable=is_enable, dry_run=is_dry_run, 
                                log_callback=self.log, backup_data=self.current_backup)
                
                if result:
                    success_count += 1
                    
            except Exception as e:
                self.log(f"[ERROR] Unexpected error in {name}: {e}")
        
        self.after(10, lambda: self.update_progress(100))
        
        # Summary
        self.log("\n" + "="*60)
        self.log(f"Script finished. {success_count}/{total_tasks} tasks completed successfully.")
        
        if create_backup and self.current_backup and not is_dry_run:
            self.log(f"Backup created with {len(self.current_backup)} registry entries.")
            self.log("IMPORTANT: Save your backup using the 'Save Backup' button!")
        
        if not is_enable and not is_dry_run:
            self.log("WARNING: Security and telemetry features were disabled.")
            self.log("RECOMMENDATION: Keep Windows Defender enabled for security!")
        elif is_dry_run:
            self.log("Dry run finished. No changes were made.")
        else:
            self.log("System settings have been reverted towards their defaults.")
        
        self.log("A restart may be required for all changes to take full effect.")
        
        # Re-enable the button
        self.after(100, self.task_finished)
        
    def task_finished(self):
        """Called when the task is done to update the GUI."""
        self.apply_button.config(state=tk.NORMAL, text="Apply Changes")
        self.update_progress(0)


# ==============================================================================
# MAIN EXECUTION WITH AUTO-ELEVATION
# ==============================================================================

if __name__ == "__main__":
    # Choose elevation method:
    # Method 1: Ask user before elevating (recommended)
    check_and_elevate()
    
    # Method 2: Silent elevation (uncomment to use instead)
    # auto_elevate_silent()
    
    # Method 3: No automatic elevation (original behavior)
    # Just proceed without elevation check
    
    # Start the application
    app = EnhancedApp()
    app.mainloop()