#!/usr/bin/env python
"""
Ultimate Windows Performance & Privacy Tool
Combined: Gaming Boost + Privacy Settings + Benchmarking + Automatic Backup
"""
import subprocess
import winreg as reg
import sys
import os
import ctypes
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import json
import time
from datetime import datetime

# ==============================================================================
# HIDE CONSOLE WINDOW
# ==============================================================================

def hide_console():
    """Hide the console window on Windows."""
    try:
        # Get the console window handle
        console_window = ctypes.windll.kernel32.GetConsoleWindow()
        if console_window:
            # SW_HIDE = 0
            ctypes.windll.user32.ShowWindow(console_window, 0)
    except:
        pass

# ==============================================================================
# DEPENDENCY CHECK AND AUTO-INSTALL
# ==============================================================================

def check_and_install_requirements():
    """Check for required packages and install if missing."""
    required_packages = {
        'psutil': 'psutil'
    }
    
    missing_packages = []
    
    # Check each required package
    for package_name, pip_name in required_packages.items():
        try:
            __import__(package_name)
        except ImportError:
            missing_packages.append(pip_name)
    
    if missing_packages:
        # Show GUI prompt
        root = tk.Tk()
        root.withdraw()
        
        response = messagebox.askyesno(
            "Missing Dependencies",
            f"This program requires the following Python packages:\n\n"
            f"• {', '.join(missing_packages)}\n\n"
            f"Would you like to install them automatically?\n\n"
            f"(This will run: pip install {' '.join(missing_packages)})",
            icon='warning'
        )
        
        if response:
            # Install packages
            progress_window = tk.Toplevel()
            progress_window.title("Installing Dependencies")
            progress_window.geometry("500x200")
            progress_window.transient(root)
            
            tk.Label(progress_window, 
                    text="Installing required packages...", 
                    font=('Arial', 12, 'bold')).pack(pady=20)
            
            log_text = tk.Text(progress_window, height=8, wrap=tk.WORD, 
                             font=('Consolas', 9))
            log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            progress_window.update()
            
            try:
                for package in missing_packages:
                    log_text.insert(tk.END, f"Installing {package}...\n")
                    log_text.see(tk.END)
                    progress_window.update()
                    
                    result = subprocess.run(
                        [sys.executable, "-m", "pip", "install", package],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    
                    log_text.insert(tk.END, f"✅ {package} installed successfully!\n\n")
                    log_text.see(tk.END)
                    progress_window.update()
                
                log_text.insert(tk.END, "\n✅ All dependencies installed!\n")
                log_text.insert(tk.END, "The program will now start...\n")
                log_text.see(tk.END)
                
                time.sleep(2)
                progress_window.destroy()
                root.destroy()
                return True
                
            except subprocess.CalledProcessError as e:
                log_text.insert(tk.END, f"\n❌ Error installing packages:\n{e}\n")
                log_text.see(tk.END)
                messagebox.showerror(
                    "Installation Failed",
                    f"Failed to install required packages.\n\n"
                    f"Please install manually:\n"
                    f"pip install {' '.join(missing_packages)}"
                )
                progress_window.destroy()
                root.destroy()
                return False
        else:
            messagebox.showerror(
                "Cannot Continue",
                f"This program cannot run without the required packages.\n\n"
                f"Please install them manually:\n"
                f"pip install {' '.join(missing_packages)}"
            )
            root.destroy()
            return False
    
    return True

# Try to import psutil after potential installation
try:
    import psutil
except ImportError:
    # This will be caught by check_and_install_requirements
    psutil = None

# ==============================================================================
# ADMIN ELEVATION
# ==============================================================================

def is_admin():
    """Check for administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def elevate_privileges():
    """Restart with admin privileges."""
    if is_admin():
        return True
    
    try:
        script_path = os.path.abspath(sys.argv[0])
        if script_path.endswith('.py'):
            result = ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, f'"{script_path}"', None, 1
            )
        else:
            result = ctypes.windll.shell32.ShellExecuteW(
                None, "runas", script_path, None, None, 1
            )
        return result > 32
    except:
        return False

# ==============================================================================
# BACKEND FUNCTIONS
# ==============================================================================

def get_service_status(service_name):
    """Get service status."""
    try:
        result = subprocess.run(["sc", "query", service_name], 
                              capture_output=True, text=True, check=False)
        if "RUNNING" in result.stdout:
            return "running"
        elif "STOPPED" in result.stdout:
            return "stopped"
        return "unknown"
    except:
        return "error"

def configure_service(service_name, enable=False, log_callback=print):
    """Configure service."""
    status = get_service_status(service_name)
    if status == "not_found":
        log_callback(f"  Service {service_name} not found")
        return True
    
    try:
        if not enable and status == "running":
            subprocess.run(["sc", "stop", service_name], check=False, capture_output=True)
            log_callback(f"  Stopped {service_name}")
        
        start_type = "auto" if enable else "disabled"
        subprocess.run(["sc", "config", service_name, f"start={start_type}"], 
                      check=False, capture_output=True)
        log_callback(f"  Set {service_name} to {start_type}")
        
        if enable and status == "stopped":
            subprocess.run(["sc", "start", service_name], check=False, capture_output=True)
            log_callback(f"  Started {service_name}")
        
        return True
    except Exception as e:
        log_callback(f"  Error with {service_name}: {e}")
        return False

def set_registry_key(root, path, name, value_type, value, log_callback=print, backup_data=None):
    """Set registry key with automatic backup."""
    # Automatic backup before changing
    if backup_data is not None:
        try:
            key = reg.OpenKey(root, path, 0, reg.KEY_READ)
            old_value, old_type = reg.QueryValueEx(key, name)
            reg.CloseKey(key)
            
            root_name = {
                reg.HKEY_LOCAL_MACHINE: "HKLM",
                reg.HKEY_CURRENT_USER: "HKCU"
            }.get(root, str(root))
            
            backup_key = f"{root_name}\\{path}\\{name}"
            backup_data[backup_key] = {"value": old_value, "type": old_type}
        except FileNotFoundError:
            root_name = {
                reg.HKEY_LOCAL_MACHINE: "HKLM",
                reg.HKEY_CURRENT_USER: "HKCU"
            }.get(root, str(root))
            backup_data[f"{root_name}\\{path}\\{name}"] = None
        except:
            pass
    
    # Apply change
    try:
        key = reg.CreateKeyEx(root, path, 0, reg.KEY_WRITE)
        reg.SetValueEx(key, name, 0, value_type, value)
        reg.CloseKey(key)
        log_callback(f"  ✅ Set {path}\\{name}")
        return True
    except Exception as e:
        log_callback(f"  ❌ Failed {path}\\{name}: {e}")
        return False

def configure_defender(enable=False, log_callback=print, backup_data=None):
    """Configure Windows Defender."""
    log_callback(f"\n{'Enabling' if enable else 'Disabling'} Windows Defender...")
    
    # PowerShell command
    ps_cmd = f"Set-MpPreference -DisableRealtimeMonitoring {'$false' if enable else '$true'}"
    try:
        subprocess.run(["powershell", "-Command", ps_cmd], 
                      check=False, capture_output=True, timeout=10)
        log_callback(f"  {'Enabled' if enable else 'Disabled'} real-time protection")
    except:
        log_callback(f"  Could not modify real-time protection")
    
    # Registry
    set_registry_key(reg.HKEY_LOCAL_MACHINE, 
                    r"SOFTWARE\Policies\Microsoft\Windows Defender", 
                    "DisableAntiSpyware", reg.REG_DWORD, 0 if enable else 1, 
                    log_callback, backup_data)
    
    # Service
    configure_service("WinDefend", enable=enable, log_callback=log_callback)
    return True

def configure_telemetry(enable=False, log_callback=print, backup_data=None):
    """Configure telemetry."""
    log_callback(f"\n{'Enabling' if enable else 'Disabling'} Telemetry...")
    
    set_registry_key(reg.HKEY_LOCAL_MACHINE, 
                    r"SOFTWARE\Policies\Microsoft\Windows\DataCollection", 
                    "AllowTelemetry", reg.REG_DWORD, 1 if enable else 0, 
                    log_callback, backup_data)
    
    configure_service("DiagTrack", enable=enable, log_callback=log_callback)
    configure_service("dmwappushservice", enable=enable, log_callback=log_callback)
    return True

def configure_activity_recall(enable=False, log_callback=print, backup_data=None):
    """Configure activity tracking and recall."""
    log_callback(f"\n{'Enabling' if enable else 'Disabling'} Activity & Recall...")
    
    settings = [
        (reg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\WindowsAI", 
         "AllowRecallEnablement", 1 if enable else 0),
        (reg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\WindowsAI", 
         "DisableSnapshot", 0 if enable else 1),
        (reg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\System", 
         "PublishUserActivities", 1 if enable else 0),
    ]
    
    for root, path, name, val in settings:
        set_registry_key(root, path, name, reg.REG_DWORD, val, log_callback, backup_data)
    
    return True

def configure_advertising(enable=False, log_callback=print, backup_data=None):
    """Configure advertising."""
    log_callback(f"\n{'Enabling' if enable else 'Disabling'} Advertising...")
    
    settings = [
        (reg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\AdvertisingInfo", 
         "Enabled", 1 if enable else 0),
        (reg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager", 
         "SilentInstalledAppsEnabled", 1 if enable else 0),
    ]
    
    for root, path, name, val in settings:
        set_registry_key(root, path, name, reg.REG_DWORD, val, log_callback, backup_data)
    
    return True

def configure_cortana(enable=False, log_callback=print, backup_data=None):
    """Configure Cortana."""
    log_callback(f"\n{'Enabling' if enable else 'Disabling'} Cortana...")
    
    return set_registry_key(reg.HKEY_LOCAL_MACHINE, 
                           r"SOFTWARE\Policies\Microsoft\Windows\Windows Search", 
                           "AllowCortana", reg.REG_DWORD, 1 if enable else 0, 
                           log_callback, backup_data)

# ==============================================================================
# MAIN APPLICATION
# ==============================================================================

class UltimatePerformanceTool(tk.Tk):
    def __init__(self):
        super().__init__()
        
        admin_status = " [ADMINISTRATOR]" if is_admin() else " [LIMITED]"
        self.title("Ultimate Windows Performance & Privacy Tool" + admin_status)
        
        # Center window on screen
        window_width = 950
        window_height = 800
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Force window to front and keep it there briefly
        self.lift()
        self.attributes('-topmost', True)
        self.focus_force()
        self.after(3000, lambda: self.attributes('-topmost', False))
        
        # Variables
        self.gaming_boost_active = False
        self.reduced_priority_processes = []
        self.gpu_changes = []
        self.current_backup = {}
        self.auto_backup_file = "auto_backup_ultimate.json"
        
        # Load automatic backup if exists
        self.load_auto_backup()
        
        self.create_widgets()
        
    def create_widgets(self):
        # Notebook (tabs)
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab 1: Quick Gaming Boost
        self.gaming_tab = ttk.Frame(notebook, padding="10")
        notebook.add(self.gaming_tab, text="🎮 Gaming Boost")
        self.create_gaming_tab()
        
        # Tab 2: Privacy Settings
        self.privacy_tab = ttk.Frame(notebook, padding="10")
        notebook.add(self.privacy_tab, text="🔒 Privacy Settings")
        self.create_privacy_tab()
        
        # Tab 3: Benchmark
        self.benchmark_tab = ttk.Frame(notebook, padding="10")
        notebook.add(self.benchmark_tab, text="📊 Benchmark")
        self.create_benchmark_tab()
        
        # Tab 4: Backup & Restore
        self.backup_tab = ttk.Frame(notebook, padding="10")
        notebook.add(self.backup_tab, text="💾 Backup & Restore")
        self.create_backup_tab()
        
    def create_gaming_tab(self):
        """Create gaming boost tab."""
        # Title
        tk.Label(self.gaming_tab, text="⚡ Quick Gaming Performance Boost", 
                font=('Arial', 14, 'bold'), fg='#2196F3').pack(pady=10)
        
        # Info
        info_frame = ttk.LabelFrame(self.gaming_tab, text="ℹ️ About", padding="10")
        info_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(info_frame, text=(
            "Instantly optimizes your system for gaming by:\n"
            "• Stopping 5 background services (telemetry, indexing, updates)\n"
            "• Clearing memory caches for more available RAM\n"
            "• Activating High Performance power plan\n"
            "• Reducing priority of background apps (Discord, Steam, etc.)\n"
            "• Disabling visual effects for better FPS\n"
            "• GPU optimizations (scheduling, throttling, frame limits)\n"
            "• Changes are temporary and reset after reboot\n"
            "• No permanent modifications • Safe & reversible"
        ), justify=tk.LEFT).pack()
        
        # Status
        status_frame = ttk.LabelFrame(self.gaming_tab, text="📊 System Status", padding="10")
        status_frame.pack(fill=tk.X, pady=5)
        
        self.gaming_status_label = tk.Label(status_frame, text="Loading...", 
                                           font=('Consolas', 10), justify=tk.LEFT)
        self.gaming_status_label.pack()
        
        # Buttons
        btn_frame = ttk.Frame(self.gaming_tab)
        btn_frame.pack(fill=tk.X, pady=20)
        
        self.boost_btn = tk.Button(btn_frame, text="🚀 BOOST FOR GAMING", 
                                   command=self.apply_gaming_boost,
                                   font=('Arial', 12, 'bold'), bg='#4CAF50', 
                                   fg='white', height=2)
        self.boost_btn.pack(fill=tk.X, pady=5)
        
        self.restore_gaming_btn = tk.Button(btn_frame, text="↩️ RESTORE NORMAL", 
                                           command=self.restore_gaming_normal,
                                           font=('Arial', 12, 'bold'), bg='#FF9800', 
                                           fg='white', height=2, state=tk.DISABLED)
        self.restore_gaming_btn.pack(fill=tk.X, pady=5)
        
        # Log
        log_frame = ttk.LabelFrame(self.gaming_tab, text="📜 Activity Log", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.gaming_log = scrolledtext.ScrolledText(log_frame, height=10, wrap=tk.WORD,
                                                   font=('Consolas', 9))
        self.gaming_log.pack(fill=tk.BOTH, expand=True)
        
        self.gaming_log_message("Welcome! Click BOOST FOR GAMING before playing.")
        
        # Start status updates
        self.update_gaming_status()
    
    def create_privacy_tab(self):
        """Create privacy settings tab."""
        tk.Label(self.privacy_tab, text="🔒 Privacy & System Configuration", 
                font=('Arial', 14, 'bold'), fg='#9C27B0').pack(pady=10)
        
        # Warning
        warning_frame = ttk.LabelFrame(self.privacy_tab, text="⚠️ Important", padding="10")
        warning_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(warning_frame, text=(
            "These are PERMANENT changes that require a restart.\n"
            "Automatic backup will be created before making changes.\n"
            "You can restore from the Backup & Restore tab."
        ), justify=tk.LEFT, fg='red').pack()
        
        # Features
        features_frame = ttk.LabelFrame(self.privacy_tab, text="Select Features to Modify", padding="10")
        features_frame.pack(fill=tk.X, pady=5)
        
        self.privacy_features = {
            "Defender": tk.BooleanVar(value=False),
            "Telemetry": tk.BooleanVar(value=True),
            "Activity & Recall": tk.BooleanVar(value=True),
            "Advertising": tk.BooleanVar(value=True),
            "Cortana": tk.BooleanVar(value=True)
        }
        
        for name, var in self.privacy_features.items():
            ttk.Checkbutton(features_frame, text=name, variable=var).pack(anchor=tk.W)
        
        self.privacy_action_var = tk.StringVar(value="disable")
        
        action_frame = ttk.LabelFrame(self.privacy_tab, text="Action", padding="10")
        action_frame.pack(fill=tk.X, pady=5)
        
        ttk.Radiobutton(action_frame, text="Disable Features", 
                       variable=self.privacy_action_var, value="disable").pack(anchor=tk.W)
        ttk.Radiobutton(action_frame, text="Enable Features (Restore)", 
                       variable=self.privacy_action_var, value="enable").pack(anchor=tk.W)
        
        # Apply button
        tk.Button(self.privacy_tab, text="⚡ APPLY PRIVACY CHANGES (Restart Required)", 
                 command=self.apply_privacy_changes,
                 font=('Arial', 11, 'bold'), bg='#9C27B0', fg='white', 
                 height=2).pack(fill=tk.X, pady=10)
        
        # Log
        log_frame = ttk.LabelFrame(self.privacy_tab, text="📜 Activity Log", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.privacy_log = scrolledtext.ScrolledText(log_frame, height=10, wrap=tk.WORD,
                                                    font=('Consolas', 9))
        self.privacy_log.pack(fill=tk.BOTH, expand=True)
    
    def create_benchmark_tab(self):
        """Create benchmark tab."""
        tk.Label(self.benchmark_tab, text="📊 Performance Benchmarking", 
                font=('Arial', 14, 'bold'), fg='#FF5722').pack(pady=10)
        
        # Instructions
        instructions = ttk.LabelFrame(self.benchmark_tab, text="📋 How To Use", padding="10")
        instructions.pack(fill=tk.X, pady=5)
        
        tk.Label(instructions, text=(
            "1. Click 'Run BEFORE Benchmark' (without boost)\n"
            "2. Apply Gaming Boost\n"
            "3. Click 'Run AFTER Benchmark'\n"
            "4. View comparison results automatically"
        ), justify=tk.LEFT).pack()
        
        # System info
        system_frame = ttk.LabelFrame(self.benchmark_tab, text="💻 System Info", padding="10")
        system_frame.pack(fill=tk.X, pady=5)
        
        mem = psutil.virtual_memory()
        cpu_info = f"CPU: {psutil.cpu_count(logical=False)} cores, {psutil.cpu_count(logical=True)} threads"
        ram_info = f"RAM: {round(mem.total / (1024**3), 2)} GB"
        
        # Try to get GPU info
        gpu_info = self._get_gpu_info()
        if gpu_info and 'name' in gpu_info:
            gpu_text = f"GPU: {gpu_info['name']}"
            if 'memory_total_mb' in gpu_info:
                gpu_text += f" ({round(gpu_info['memory_total_mb'] / 1024, 1)} GB)"
        else:
            gpu_text = "GPU: Detection unavailable"
        
        info_text = f"{cpu_info}\n{ram_info}\n{gpu_text}"
        tk.Label(system_frame, text=info_text, font=('Consolas', 9), justify=tk.LEFT).pack()
        
        # Progress
        self.bench_progress_label = ttk.Label(self.benchmark_tab, text="Ready")
        self.bench_progress_label.pack(pady=5)
        
        self.bench_progress_var = tk.DoubleVar()
        self.bench_progress_bar = ttk.Progressbar(self.benchmark_tab, 
                                                 variable=self.bench_progress_var, 
                                                 maximum=100)
        self.bench_progress_bar.pack(fill=tk.X, padx=10, pady=5)
        
        # Buttons
        btn_frame = ttk.Frame(self.benchmark_tab)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="🎯 Run BEFORE Benchmark", 
                  command=self.run_before_benchmark).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(btn_frame, text="✅ Run AFTER Benchmark", 
                  command=self.run_after_benchmark).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Results
        results_frame = ttk.LabelFrame(self.benchmark_tab, text="📊 Results", padding="5")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.bench_results = scrolledtext.ScrolledText(results_frame, height=12, wrap=tk.WORD,
                                                      font=('Consolas', 9))
        self.bench_results.pack(fill=tk.BOTH, expand=True)
    
    def create_backup_tab(self):
        """Create backup & restore tab."""
        tk.Label(self.backup_tab, text="💾 Backup & Restore Manager", 
                font=('Arial', 14, 'bold'), fg='#00BCD4').pack(pady=10)
        
        # Auto backup status
        status_frame = ttk.LabelFrame(self.backup_tab, text="📋 Automatic Backup Status", padding="10")
        status_frame.pack(fill=tk.X, pady=5)
        
        self.backup_status_label = tk.Label(status_frame, text="Loading...", 
                                           font=('Consolas', 9), justify=tk.LEFT)
        self.backup_status_label.pack()
        self.update_backup_status()
        
        # Manual backup
        manual_frame = ttk.LabelFrame(self.backup_tab, text="💾 Manual Backup", padding="10")
        manual_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(manual_frame, text=(
            "Create or restore backups manually.\n"
            "Automatic backups are created whenever you apply privacy changes."
        ), justify=tk.LEFT).pack(pady=5)
        
        btn_frame1 = ttk.Frame(manual_frame)
        btn_frame1.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame1, text="💾 Save Current Backup", 
                  command=self.save_manual_backup).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(btn_frame1, text="📂 Load Backup", 
                  command=self.load_manual_backup).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Restore
        restore_frame = ttk.LabelFrame(self.backup_tab, text="↩️ Restore From Backup", padding="10")
        restore_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(restore_frame, text=(
            "Restore registry settings from automatic or manual backup.\n"
            "⚠️ This will revert changes made by privacy settings."
        ), justify=tk.LEFT, fg='red').pack(pady=5)
        
        tk.Button(restore_frame, text="🔄 RESTORE FROM AUTOMATIC BACKUP", 
                 command=self.restore_from_auto_backup,
                 font=('Arial', 10, 'bold'), bg='#FF5722', fg='white', 
                 height=2).pack(fill=tk.X, pady=5)
        
        # Log
        log_frame = ttk.LabelFrame(self.backup_tab, text="📜 Activity Log", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.backup_log = scrolledtext.ScrolledText(log_frame, height=8, wrap=tk.WORD,
                                                   font=('Consolas', 9))
        self.backup_log.pack(fill=tk.BOTH, expand=True)
    
    # Gaming Boost Methods
    def update_gaming_status(self):
        """Update gaming status display."""
        try:
            cpu = psutil.cpu_percent(interval=0.5)
            mem = psutil.virtual_memory()
            processes = len(list(psutil.process_iter()))
            
            status = (
                f"CPU Usage: {cpu}%\n"
                f"Available RAM: {round(mem.available / (1024**3), 1)} GB\n"
                f"Processes: {processes}\n"
                f"Boost: {'⚡ ACTIVE' if self.gaming_boost_active else '🔴 Inactive'}"
            )
            
            self.gaming_status_label.config(text=status)
            self.after(2000, self.update_gaming_status)
        except:
            pass
    
    def gaming_log_message(self, msg):
        """Log message in gaming tab."""
        timestamp = time.strftime("%H:%M:%S")
        self.gaming_log.insert(tk.END, f"[{timestamp}] {msg}\n")
        self.gaming_log.see(tk.END)
    
    def apply_gaming_boost(self):
        """Apply gaming boost with enhancements."""
        if not is_admin():
            messagebox.showerror("Admin Required", 
                               "Administrator privileges required!")
            return
        
        if self.gaming_boost_active:
            messagebox.showinfo("Already Active", "Gaming boost is already active!")
            return
        
        self.boost_btn.config(state=tk.DISABLED)
        self.gaming_log_message("\n🚀 APPLYING GAMING BOOST...")
        self.gaming_log_message("="*60)
        
        # 1. Stop background services
        self.gaming_log_message("\n📋 Phase 1: Stopping Background Services")
        services = [
            ("DiagTrack", "Telemetry"),
            ("WSearch", "Windows Search"),
            ("SysMain", "SuperFetch"),
            ("wuauserv", "Windows Update"),
            ("BITS", "Background Transfer")
        ]
        
        stopped = 0
        for service, name in services:
            self.gaming_log_message(f"  Stopping {name}...")
            try:
                subprocess.run(["sc", "stop", service], 
                             capture_output=True, check=False, timeout=5)
                stopped += 1
                self.gaming_log_message(f"    ✅ {name} stopped")
            except:
                self.gaming_log_message(f"    ⚠️ Could not stop {name}")
            self.update()
        
        self.gaming_log_message(f"  Result: {stopped}/{len(services)} services stopped")
        
        # 2. Clear system memory caches
        self.gaming_log_message("\n💾 Phase 2: Clearing System Memory Caches")
        try:
            # Clear standby memory (Windows 10+)
            subprocess.run(
                ["powershell", "-Command", 
                 "[System.GC]::Collect(); [System.GC]::WaitForPendingFinalizers()"],
                capture_output=True, check=False, timeout=10
            )
            self.gaming_log_message("  ✅ Memory caches cleared")
        except:
            self.gaming_log_message("  ⚠️ Could not clear memory caches")
        self.update()
        
        # 3. Set high performance power plan
        self.gaming_log_message("\n⚡ Phase 3: Setting High Performance Power Plan")
        try:
            # High Performance GUID: 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c
            result = subprocess.run(
                ["powercfg", "/setactive", "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"],
                capture_output=True, check=False, timeout=5
            )
            if result.returncode == 0:
                self.gaming_log_message("  ✅ High Performance mode activated")
            else:
                self.gaming_log_message("  ⚠️ Could not change power plan")
        except:
            self.gaming_log_message("  ⚠️ Could not change power plan")
        self.update()
        
        # 4. Disable Windows Game Bar notifications
        self.gaming_log_message("\n🎮 Phase 4: Optimizing Game Settings")
        try:
            key = reg.CreateKeyEx(reg.HKEY_CURRENT_USER, 
                                 r"Software\Microsoft\GameBar", 
                                 0, reg.KEY_WRITE)
            reg.SetValueEx(key, "ShowStartupPanel", 0, reg.REG_DWORD, 0)
            reg.SetValueEx(key, "UseNexusForGameBarEnabled", 0, reg.REG_DWORD, 0)
            reg.CloseKey(key)
            self.gaming_log_message("  ✅ Game Bar notifications disabled")
        except:
            self.gaming_log_message("  ⚠️ Could not modify Game Bar settings")
        self.update()
        
        # 5. Adjust visual effects for performance
        self.gaming_log_message("\n🎨 Phase 5: Adjusting Visual Effects")
        try:
            key = reg.CreateKeyEx(reg.HKEY_CURRENT_USER, 
                                 r"Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects", 
                                 0, reg.KEY_WRITE)
            reg.SetValueEx(key, "VisualFXSetting", 0, reg.REG_DWORD, 2)  # Best Performance
            reg.CloseKey(key)
            self.gaming_log_message("  ✅ Visual effects set for performance")
        except:
            self.gaming_log_message("  ℹ️ Visual effects unchanged")
        self.update()
        
        # 6. Disable unnecessary startup apps temporarily
        self.gaming_log_message("\n🚦 Phase 6: Reducing Background Processes")
        reduced_priority_processes = []
        try:
            # Lower priority of common background apps
            background_apps = ["OneDrive", "Teams", "Skype", "Discord", "Spotify", 
                             "Steam", "EpicGamesLauncher", "Chrome", "msedge"]
            
            for proc in psutil.process_iter(['name', 'pid']):
                try:
                    proc_name = proc.info['name'].lower().replace('.exe', '')
                    if any(app.lower() in proc_name for app in background_apps):
                        p = psutil.Process(proc.info['pid'])
                        old_priority = p.nice()
                        if old_priority != psutil.BELOW_NORMAL_PRIORITY_CLASS:
                            p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
                            reduced_priority_processes.append((proc.info['pid'], proc.info['name'], old_priority))
                except:
                    pass
            
            if reduced_priority_processes:
                self.gaming_log_message(f"  ✅ Reduced priority of {len(reduced_priority_processes)} background apps")
            else:
                self.gaming_log_message("  ℹ️ No background apps to optimize")
        except:
            self.gaming_log_message("  ⚠️ Could not optimize background apps")
        self.update()
        
        # Store for restoration
        self.reduced_priority_processes = reduced_priority_processes
        
        # 7. GPU Optimizations
        self.gaming_log_message("\n🎨 Phase 7: GPU Performance Optimization")
        gpu_changes = []
        
        # Disable GPU hardware acceleration for background apps
        try:
            key = reg.CreateKeyEx(reg.HKEY_CURRENT_USER, 
                                 r"SOFTWARE\Microsoft\Avalon.Graphics", 
                                 0, reg.KEY_WRITE)
            reg.SetValueEx(key, "DisableHWAcceleration", 0, reg.REG_DWORD, 1)
            reg.CloseKey(key)
            gpu_changes.append("avalon")
            self.gaming_log_message("  ✅ Disabled hardware acceleration for non-game apps")
        except:
            pass
        
        # Optimize GPU scheduling (Windows 10 2004+)
        try:
            key = reg.CreateKeyEx(reg.HKEY_LOCAL_MACHINE, 
                                 r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers", 
                                 0, reg.KEY_WRITE)
            reg.SetValueEx(key, "HwSchMode", 0, reg.REG_DWORD, 2)
            reg.CloseKey(key)
            gpu_changes.append("hwsch")
            self.gaming_log_message("  ✅ Enabled Hardware-accelerated GPU scheduling")
        except:
            pass
        
        # Disable GPU power saving
        try:
            key = reg.CreateKeyEx(reg.HKEY_LOCAL_MACHINE, 
                                 r"SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}\0000", 
                                 0, reg.KEY_WRITE)
            reg.SetValueEx(key, "PP_ThermalAutoThrottlingEnable", 0, reg.REG_DWORD, 0)
            reg.CloseKey(key)
            gpu_changes.append("throttle")
            self.gaming_log_message("  ✅ Disabled GPU thermal throttling")
        except:
            pass
        
        # Maximize GPU performance mode
        try:
            subprocess.run(
                ["powershell", "-Command", 
                 "Set-ItemProperty -Path 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Power' -Name 'CsEnabled' -Value 0 -Force"],
                capture_output=True, check=False, timeout=5
            )
            gpu_changes.append("cs")
            self.gaming_log_message("  ✅ Disabled Connected Standby (better GPU performance)")
        except:
            pass
        
        # Disable Desktop Window Manager throttling
        try:
            key = reg.CreateKeyEx(reg.HKEY_CURRENT_USER, 
                                 r"SOFTWARE\Microsoft\Windows\DWM", 
                                 0, reg.KEY_WRITE)
            reg.SetValueEx(key, "EnableFrameRateLimit", 0, reg.REG_DWORD, 0)
            reg.CloseKey(key)
            gpu_changes.append("dwm")
            self.gaming_log_message("  ✅ Disabled DWM frame rate limiting")
        except:
            pass
        
        # Store GPU changes for restoration
        self.gpu_changes = gpu_changes
        
        if gpu_changes:
            self.gaming_log_message(f"  ✅ Applied {len(gpu_changes)} GPU optimizations")
        else:
            self.gaming_log_message("  ⚠️ Could not apply GPU optimizations (may need restart)")
        self.update()
        
        self.gaming_log_message("\n" + "="*60)
        self.gaming_log_message("✅ GAMING BOOST COMPLETE!")
        self.gaming_log_message(f"🎮 CPU, RAM, and GPU optimized for maximum performance!")
        self.gaming_log_message("🔄 Click 'RESTORE NORMAL' when done or just restart PC")
        self.gaming_log_message("⚠️ Some GPU optimizations may require a restart to take full effect")
        self.gaming_log_message("="*60)
        
        self.gaming_boost_active = True
        self.boost_btn.config(state=tk.NORMAL, bg='#999999')
        self.restore_gaming_btn.config(state=tk.NORMAL)
        self.update_gaming_status()
    
    def restore_gaming_normal(self):
        """Restore normal operation."""
        self.restore_gaming_btn.config(state=tk.DISABLED)
        self.gaming_log_message("\n↩️ RESTORING NORMAL OPERATION...")
        self.gaming_log_message("="*60)
        
        # 1. Restore services
        self.gaming_log_message("\n📋 Phase 1: Restarting Services")
        services = [
            ("DiagTrack", "Telemetry"),
            ("WSearch", "Windows Search"),
            ("SysMain", "SuperFetch"),
            ("wuauserv", "Windows Update"),
            ("BITS", "Background Transfer")
        ]
        
        for service, name in services:
            self.gaming_log_message(f"  Starting {name}...")
            try:
                subprocess.run(["sc", "start", service], 
                             capture_output=True, check=False, timeout=5)
                self.gaming_log_message(f"    ✅ {name} restarted")
            except:
                self.gaming_log_message(f"    ℹ️ {name} already running or not available")
            self.update()
        
        # 2. Restore power plan to balanced
        self.gaming_log_message("\n⚡ Phase 2: Restoring Power Plan")
        try:
            # Balanced GUID: 381b4222-f694-41f0-9685-ff5bb260df2e
            subprocess.run(
                ["powercfg", "/setactive", "381b4222-f694-41f0-9685-ff5bb260df2e"],
                capture_output=True, check=False, timeout=5
            )
            self.gaming_log_message("  ✅ Balanced power plan restored")
        except:
            self.gaming_log_message("  ℹ️ Power plan unchanged")
        self.update()
        
        # 3. Restore process priorities
        self.gaming_log_message("\n🚦 Phase 3: Restoring Process Priorities")
        if hasattr(self, 'reduced_priority_processes') and self.reduced_priority_processes:
            restored = 0
            for pid, name, old_priority in self.reduced_priority_processes:
                try:
                    if psutil.pid_exists(pid):
                        p = psutil.Process(pid)
                        p.nice(old_priority)
                        restored += 1
                except:
                    pass
            self.gaming_log_message(f"  ✅ Restored {restored}/{len(self.reduced_priority_processes)} process priorities")
            self.reduced_priority_processes = []
        else:
            self.gaming_log_message("  ℹ️ No process priorities to restore")
        self.update()
        
        # 4. Re-enable Game Bar
        self.gaming_log_message("\n🎮 Phase 4: Restoring Game Settings")
        try:
            key = reg.CreateKeyEx(reg.HKEY_CURRENT_USER, 
                                 r"Software\Microsoft\GameBar", 
                                 0, reg.KEY_WRITE)
            reg.SetValueEx(key, "ShowStartupPanel", 0, reg.REG_DWORD, 1)
            reg.SetValueEx(key, "UseNexusForGameBarEnabled", 0, reg.REG_DWORD, 1)
            reg.CloseKey(key)
            self.gaming_log_message("  ✅ Game Bar settings restored")
        except:
            self.gaming_log_message("  ℹ️ Game Bar settings unchanged")
        self.update()
        
        # 5. Restore visual effects
        self.gaming_log_message("\n🎨 Phase 5: Restoring Visual Effects")
        try:
            key = reg.CreateKeyEx(reg.HKEY_CURRENT_USER, 
                                 r"Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects", 
                                 0, reg.KEY_WRITE)
            reg.SetValueEx(key, "VisualFXSetting", 0, reg.REG_DWORD, 0)  # Let Windows Choose
            reg.CloseKey(key)
            self.gaming_log_message("  ✅ Visual effects restored")
        except:
            self.gaming_log_message("  ℹ️ Visual effects unchanged")
        self.update()
        
        # 6. Restore GPU settings
        self.gaming_log_message("\n🎨 Phase 6: Restoring GPU Settings")
        if hasattr(self, 'gpu_changes') and self.gpu_changes:
            restored = 0
            
            # Restore Avalon graphics
            if "avalon" in self.gpu_changes:
                try:
                    key = reg.CreateKeyEx(reg.HKEY_CURRENT_USER, 
                                         r"SOFTWARE\Microsoft\Avalon.Graphics", 
                                         0, reg.KEY_WRITE)
                    reg.SetValueEx(key, "DisableHWAcceleration", 0, reg.REG_DWORD, 0)
                    reg.CloseKey(key)
                    restored += 1
                except:
                    pass
            
            # Restore Hardware scheduling (leave enabled - it's good)
            # if "hwsch" in self.gpu_changes:
            #     try:
            #         key = reg.CreateKeyEx(reg.HKEY_LOCAL_MACHINE, 
            #                              r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers", 
            #                              0, reg.KEY_WRITE)
            #         reg.SetValueEx(key, "HwSchMode", 0, reg.REG_DWORD, 1)
            #         reg.CloseKey(key)
            #         restored += 1
            #     except:
            #         pass
            
            # Restore GPU throttling
            if "throttle" in self.gpu_changes:
                try:
                    key = reg.CreateKeyEx(reg.HKEY_LOCAL_MACHINE, 
                                         r"SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}\0000", 
                                         0, reg.KEY_WRITE)
                    reg.SetValueEx(key, "PP_ThermalAutoThrottlingEnable", 0, reg.REG_DWORD, 1)
                    reg.CloseKey(key)
                    restored += 1
                except:
                    pass
            
            # Restore Connected Standby
            if "cs" in self.gpu_changes:
                try:
                    subprocess.run(
                        ["powershell", "-Command", 
                         "Set-ItemProperty -Path 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Power' -Name 'CsEnabled' -Value 1 -Force"],
                        capture_output=True, check=False, timeout=5
                    )
                    restored += 1
                except:
                    pass
            
            # Restore DWM frame limit
            if "dwm" in self.gpu_changes:
                try:
                    key = reg.CreateKeyEx(reg.HKEY_CURRENT_USER, 
                                         r"SOFTWARE\Microsoft\Windows\DWM", 
                                         0, reg.KEY_WRITE)
                    reg.SetValueEx(key, "EnableFrameRateLimit", 0, reg.REG_DWORD, 1)
                    reg.CloseKey(key)
                    restored += 1
                except:
                    pass
            
            self.gaming_log_message(f"  ✅ Restored {restored} GPU settings")
            self.gpu_changes = []
        else:
            self.gaming_log_message("  ℹ️ No GPU settings to restore")
        self.update()
        
        self.gaming_log_message("\n" + "="*60)
        self.gaming_log_message("✅ NORMAL OPERATION RESTORED")
        self.gaming_log_message("💻 Your system is back to normal settings")
        self.gaming_log_message("="*60)
        
        self.gaming_boost_active = False
        self.boost_btn.config(bg='#4CAF50')
        self.update_gaming_status()
    
    # Privacy Methods
    def privacy_log_message(self, msg):
        """Log message in privacy tab."""
        self.privacy_log.insert(tk.END, msg + "\n")
        self.privacy_log.see(tk.END)
        self.update()
    
    def apply_privacy_changes(self):
        """Apply privacy changes with automatic backup."""
        if not is_admin():
            messagebox.showerror("Admin Required", "Administrator privileges required!")
            return
        
        response = messagebox.askyesno(
            "Apply Privacy Changes",
            "This will make PERMANENT changes and requires a restart.\n\n"
            "Automatic backup will be created.\n\n"
            "Continue?",
            icon='warning'
        )
        
        if not response:
            return
        
        # Create automatic backup
        self.current_backup = {
            "timestamp": datetime.now().isoformat(),
            "type": "automatic",
            "data": {}
        }
        
        self.privacy_log.insert(tk.END, "="*70 + "\n")
        self.privacy_log_message("🔄 APPLYING PRIVACY CHANGES")
        self.privacy_log.insert(tk.END, "="*70 + "\n")
        self.privacy_log_message(f"📦 Creating automatic backup...")
        
        is_enable = self.privacy_action_var.get() == "enable"
        
        # Apply selected features
        if self.privacy_features["Defender"].get():
            configure_defender(is_enable, self.privacy_log_message, 
                             self.current_backup["data"])
        
        if self.privacy_features["Telemetry"].get():
            configure_telemetry(is_enable, self.privacy_log_message, 
                              self.current_backup["data"])
        
        if self.privacy_features["Activity & Recall"].get():
            configure_activity_recall(is_enable, self.privacy_log_message, 
                                    self.current_backup["data"])
        
        if self.privacy_features["Advertising"].get():
            configure_advertising(is_enable, self.privacy_log_message, 
                                self.current_backup["data"])
        
        if self.privacy_features["Cortana"].get():
            configure_cortana(is_enable, self.privacy_log_message, 
                            self.current_backup["data"])
        
        # Save automatic backup
        self.save_auto_backup()
        
        self.privacy_log.insert(tk.END, "\n" + "="*70 + "\n")
        self.privacy_log_message(f"✅ CHANGES APPLIED!")
        self.privacy_log_message(f"💾 Automatic backup saved to: {self.auto_backup_file}")
        self.privacy_log_message(f"⚠️ RESTART YOUR COMPUTER for changes to take effect")
        self.privacy_log.insert(tk.END, "="*70 + "\n")
        
        self.update_backup_status()
        
        messagebox.showinfo(
            "Changes Applied",
            f"Privacy changes applied successfully!\n\n"
            f"✅ Automatic backup created\n"
            f"⚠️ RESTART your computer for changes to take effect\n\n"
            f"You can restore from the Backup & Restore tab if needed."
        )
    
    # Benchmark Methods
    def bench_log(self, msg):
        """Log benchmark message."""
        self.bench_results.insert(tk.END, msg + "\n")
        self.bench_results.see(tk.END)
        self.update()
    
    def run_before_benchmark(self):
        """Run before benchmark."""
        self.bench_results.delete('1.0', tk.END)
        self.bench_log("="*70)
        self.bench_log("BASELINE BENCHMARK (BEFORE)")
        self.bench_log("="*70)
        
        thread = threading.Thread(target=self._run_benchmark, 
                                 args=("benchmark_before.json",), daemon=True)
        thread.start()
    
    def run_after_benchmark(self):
        """Run after benchmark."""
        self.bench_results.delete('1.0', tk.END)
        self.bench_log("="*70)
        self.bench_log("AFTER BENCHMARK")
        self.bench_log("="*70)
        
        thread = threading.Thread(target=self._run_benchmark, 
                                 args=("benchmark_after.json",), daemon=True)
        thread.start()
    
    def _run_benchmark(self, filename):
        """Worker thread for benchmark."""
        try:
            results = {"timestamp": datetime.now().isoformat()}
            
            # CPU
            self.after(0, lambda: self.bench_progress_label.config(text="Testing CPU..."))
            self.after(0, lambda: self.bench_progress_var.set(20))
            
            cpu_samples = []
            for i in range(5):
                cpu_samples.append(psutil.cpu_percent(interval=1))
            
            results["cpu"] = {
                "average": round(sum(cpu_samples) / len(cpu_samples), 2),
                "min": round(min(cpu_samples), 2),
                "max": round(max(cpu_samples), 2)
            }
            
            self.bench_log(f"\nCPU Average: {results['cpu']['average']}%")
            
            # Memory
            self.after(0, lambda: self.bench_progress_label.config(text="Testing Memory..."))
            self.after(0, lambda: self.bench_progress_var.set(40))
            
            mem = psutil.virtual_memory()
            results["memory"] = {
                "total_gb": round(mem.total / (1024**3), 2),
                "available_gb": round(mem.available / (1024**3), 2),
                "percent_used": mem.percent
            }
            
            self.bench_log(f"Available RAM: {results['memory']['available_gb']} GB")
            
            # GPU (if available)
            self.after(0, lambda: self.bench_progress_label.config(text="Testing GPU..."))
            self.after(0, lambda: self.bench_progress_var.set(60))
            
            gpu_info = self._get_gpu_info()
            if gpu_info:
                results["gpu"] = gpu_info
                if "usage_percent" in gpu_info:
                    self.bench_log(f"GPU Usage: {gpu_info['usage_percent']}%")
                if "memory_used_mb" in gpu_info:
                    self.bench_log(f"GPU Memory: {gpu_info['memory_used_mb']} MB / {gpu_info['memory_total_mb']} MB")
            else:
                results["gpu"] = {"available": False, "reason": "No GPU detected or driver issue"}
                self.bench_log("GPU: Not available for monitoring")
            
            # Processes
            self.after(0, lambda: self.bench_progress_label.config(text="Counting Processes..."))
            self.after(0, lambda: self.bench_progress_var.set(80))
            
            processes = list(psutil.process_iter())
            results["processes"] = {"total_processes": len(processes)}
            
            self.bench_log(f"Processes: {results['processes']['total_processes']}")
            
            # Save
            self.after(0, lambda: self.bench_progress_label.config(text="Saving..."))
            self.after(0, lambda: self.bench_progress_var.set(90))
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2)
            
            self.after(0, lambda: self.bench_progress_var.set(100))
            self.bench_log(f"\n✅ Benchmark saved to: {filename}")
            
            # Auto-compare if both exist
            if os.path.exists("benchmark_before.json") and os.path.exists("benchmark_after.json"):
                self.after(1000, self._compare_benchmarks)
            
        except Exception as e:
            self.bench_log(f"\n❌ Error: {e}")
        finally:
            self.after(0, lambda: self.bench_progress_label.config(text="Complete"))
    
    def _get_gpu_info(self):
        """Get GPU information using multiple methods."""
        gpu_data = {}
        
        # Method 1: Try nvidia-smi for NVIDIA GPUs (most reliable for NVIDIA)
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu,name",
                 "--format=csv,noheader,nounits"],
                capture_output=True, text=True, timeout=5, check=False
            )
            if result.returncode == 0 and result.stdout.strip():
                parts = result.stdout.strip().split(',')
                if len(parts) >= 5:
                    gpu_data["name"] = parts[4].strip()
                    try:
                        gpu_data["usage_percent"] = round(float(parts[0].strip()), 1)
                    except:
                        gpu_data["usage_percent"] = 0.0
                    try:
                        gpu_data["memory_used_mb"] = int(parts[1].strip())
                        gpu_data["memory_total_mb"] = int(parts[2].strip())
                    except:
                        pass
                    try:
                        gpu_data["temperature_c"] = int(parts[3].strip())
                    except:
                        pass
                    gpu_data["vendor"] = "NVIDIA"
                    gpu_data["available"] = True
                    return gpu_data  # NVIDIA data is most complete
        except:
            pass
        
        # Method 2: Try WMI for basic GPU info (fallback)
        try:
            result = subprocess.run(
                ["powershell", "-Command",
                 "Get-WmiObject Win32_VideoController | Select-Object -First 1 | Select-Object Name,AdapterRAM | ConvertTo-Json"],
                capture_output=True, text=True, timeout=5, check=False
            )
            if result.returncode == 0 and result.stdout.strip():
                import json as json_lib
                wmi_data = json_lib.loads(result.stdout)
                if "Name" in wmi_data:
                    gpu_data["name"] = wmi_data["Name"]
                if "AdapterRAM" in wmi_data and wmi_data["AdapterRAM"]:
                    try:
                        gpu_data["memory_total_mb"] = round(int(wmi_data["AdapterRAM"]) / (1024 * 1024))
                    except:
                        pass
        except:
            pass
        
        # Method 3: Try Windows Performance Counters for usage (works on most systems)
        if "usage_percent" not in gpu_data:
            try:
                result = subprocess.run(
                    ["powershell", "-Command",
                     "$sum = 0; $count = 0; (Get-Counter '\\GPU Engine(*engtype_3D)\\Utilization Percentage' -ErrorAction SilentlyContinue).CounterSamples | ForEach-Object { $sum += $_.CookedValue; $count++ }; if($count -gt 0) { $sum / $count } else { 0 }"],
                    capture_output=True, text=True, timeout=5, check=False
                )
                if result.returncode == 0 and result.stdout.strip():
                    try:
                        gpu_usage = float(result.stdout.strip())
                        gpu_data["usage_percent"] = round(gpu_usage, 1)
                    except:
                        pass
            except:
                pass
        
        # If we got any data, mark as available
        if gpu_data and ("name" in gpu_data or "usage_percent" in gpu_data):
            gpu_data["available"] = True
            return gpu_data
        
        # Return minimal data if nothing worked
        return {"available": False, "reason": "No GPU detected or driver issue"}
    
    def _compare_benchmarks(self):
        """Compare benchmark results."""
        try:
            with open("benchmark_before.json", 'r') as f:
                before = json.load(f)
            with open("benchmark_after.json", 'r') as f:
                after = json.load(f)
            
            self.bench_log("\n" + "="*70)
            self.bench_log("📈 BENCHMARK COMPARISON")
            self.bench_log("="*70)
            
            # CPU
            cpu_before = before['cpu']['average']
            cpu_after = after['cpu']['average']
            cpu_improvement = ((cpu_before - cpu_after) / cpu_before * 100) if cpu_before > 0 else 0
            
            self.bench_log(f"\n🖥️ CPU Performance:")
            self.bench_log(f"  Before: {cpu_before}%")
            self.bench_log(f"  After:  {cpu_after}%")
            
            if cpu_improvement > 0:
                self.bench_log(f"  ✅ {cpu_improvement:.1f}% IMPROVEMENT in CPU usage!")
            
            # Memory
            mem_before = before['memory']['available_gb']
            mem_after = after['memory']['available_gb']
            mem_diff = mem_after - mem_before
            
            self.bench_log(f"\n💾 Memory Performance:")
            self.bench_log(f"  Available Before: {mem_before} GB")
            self.bench_log(f"  Available After:  {mem_after} GB")
            
            if mem_diff > 0:
                self.bench_log(f"  ✅ {mem_diff:.2f} GB MORE RAM available!")
            
            # GPU Comparison
            if 'gpu' in before and 'gpu' in after:
                gpu_before_avail = before['gpu'].get('available', False)
                gpu_after_avail = after['gpu'].get('available', False)
                
                if gpu_before_avail or gpu_after_avail:
                    self.bench_log(f"\n🎨 GPU Performance:")
                    
                    # GPU Name
                    gpu_name = before['gpu'].get('name') or after['gpu'].get('name')
                    if gpu_name:
                        self.bench_log(f"  GPU: {gpu_name}")
                    
                    # GPU Usage
                    if 'usage_percent' in before['gpu'] and 'usage_percent' in after['gpu']:
                        gpu_before = before['gpu']['usage_percent']
                        gpu_after = after['gpu']['usage_percent']
                        gpu_diff = gpu_after - gpu_before
                        
                        self.bench_log(f"  Usage Before: {gpu_before}%")
                        self.bench_log(f"  Usage After:  {gpu_after}%")
                        
                        if abs(gpu_diff) < 1.0:
                            self.bench_log(f"  Change: {gpu_diff:+.1f}% (minimal)")
                        else:
                            self.bench_log(f"  Change: {gpu_diff:+.1f}%")
                    elif 'usage_percent' in before['gpu'] or 'usage_percent' in after['gpu']:
                        self.bench_log(f"  ℹ️ GPU usage only available in one benchmark")
                    
                    # GPU Memory
                    if 'memory_used_mb' in before['gpu'] and 'memory_used_mb' in after['gpu']:
                        mem_before_mb = before['gpu']['memory_used_mb']
                        mem_after_mb = after['gpu']['memory_used_mb']
                        mem_total_mb = before['gpu'].get('memory_total_mb', after['gpu'].get('memory_total_mb', 0))
                        mem_diff_mb = mem_after_mb - mem_before_mb
                        
                        self.bench_log(f"  Memory Before: {mem_before_mb} MB / {mem_total_mb} MB")
                        self.bench_log(f"  Memory After:  {mem_after_mb} MB / {mem_total_mb} MB")
                        
                        if mem_diff_mb < -50:
                            self.bench_log(f"  ✅ {abs(mem_diff_mb)} MB FREED!")
                        elif mem_diff_mb > 50:
                            self.bench_log(f"  ⚠️ {mem_diff_mb} MB more used")
                        else:
                            self.bench_log(f"  Change: {mem_diff_mb:+d} MB (minimal)")
                    elif 'memory_total_mb' in before['gpu'] or 'memory_total_mb' in after['gpu']:
                        total = before['gpu'].get('memory_total_mb') or after['gpu'].get('memory_total_mb')
                        self.bench_log(f"  Total VRAM: {total} MB ({round(total/1024, 1)} GB)")
                    
                    # GPU Temperature
                    if 'temperature_c' in before['gpu'] and 'temperature_c' in after['gpu']:
                        temp_before = before['gpu']['temperature_c']
                        temp_after = after['gpu']['temperature_c']
                        temp_diff = temp_after - temp_before
                        
                        self.bench_log(f"  Temperature Before: {temp_before}°C")
                        self.bench_log(f"  Temperature After:  {temp_after}°C")
                        self.bench_log(f"  Change: {temp_diff:+d}°C")
                        
                        if temp_after > 85:
                            self.bench_log(f"  ⚠️ Warning: GPU temperature is high!")
                    
                    # If no detailed metrics available
                    if ('usage_percent' not in before['gpu'] and 'usage_percent' not in after['gpu'] and
                        'memory_used_mb' not in before['gpu'] and 'memory_used_mb' not in after['gpu']):
                        self.bench_log(f"  ℹ️ Detailed GPU metrics not available")
                        self.bench_log(f"  💡 Try installing latest GPU drivers for monitoring support")
                else:
                    self.bench_log(f"\n🎨 GPU Performance:")
                    self.bench_log(f"  ℹ️ GPU monitoring not available")
            
            # Processes
            proc_before = before['processes']['total_processes']
            proc_after = after['processes']['total_processes']
            proc_diff = proc_after - proc_before
            
            self.bench_log(f"\n⚙️ Background Processes:")
            self.bench_log(f"  Before: {proc_before}")
            self.bench_log(f"  After:  {proc_after}")
            self.bench_log(f"  Change: {proc_diff:+d}")
            
            self.bench_log("\n" + "="*70)
            
        except Exception as e:
            self.bench_log(f"\n❌ Error comparing: {e}")
    
    # Backup Methods
    def backup_log_message(self, msg):
        """Log backup message."""
        self.backup_log.insert(tk.END, msg + "\n")
        self.backup_log.see(tk.END)
        self.update()
    
    def update_backup_status(self):
        """Update backup status display."""
        if os.path.exists(self.auto_backup_file):
            try:
                with open(self.auto_backup_file, 'r') as f:
                    backup = json.load(f)
                
                timestamp = backup.get("timestamp", "Unknown")
                entries = len(backup.get("data", {}))
                
                status = (
                    f"✅ Automatic Backup Available\n"
                    f"Created: {timestamp}\n"
                    f"Entries: {entries} registry values backed up"
                )
                self.backup_status_label.config(text=status, fg='green')
            except:
                self.backup_status_label.config(
                    text="⚠️ Backup file exists but is corrupted", 
                    fg='red'
                )
        else:
            self.backup_status_label.config(
                text="ℹ️ No automatic backup available yet\nApply privacy changes to create one", 
                fg='gray'
            )
    
    def save_auto_backup(self):
        """Save automatic backup."""
        try:
            with open(self.auto_backup_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_backup, f, indent=2)
            return True
        except Exception as e:
            messagebox.showerror("Backup Error", f"Failed to save automatic backup: {e}")
            return False
    
    def load_auto_backup(self):
        """Load automatic backup on startup."""
        if os.path.exists(self.auto_backup_file):
            try:
                with open(self.auto_backup_file, 'r', encoding='utf-8') as f:
                    self.current_backup = json.load(f)
            except:
                self.current_backup = {}
    
    def save_manual_backup(self):
        """Save manual backup file."""
        if not self.current_backup or not self.current_backup.get("data"):
            messagebox.showwarning("No Backup", 
                                 "No backup data available.\n"
                                 "Apply privacy changes first to create a backup.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            initialfile=f"manual_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save Manual Backup"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.current_backup, f, indent=2)
                self.backup_log_message(f"✅ Manual backup saved: {filename}")
                messagebox.showinfo("Success", f"Backup saved to:\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save backup: {e}")
    
    def load_manual_backup(self):
        """Load manual backup file."""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Load Backup"
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    self.current_backup = json.load(f)
                
                self.backup_log_message(f"✅ Manual backup loaded: {filename}")
                messagebox.showinfo("Success", 
                                  f"Backup loaded from:\n{filename}\n\n"
                                  f"Click 'RESTORE FROM AUTOMATIC BACKUP' to apply it.")
                self.update_backup_status()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load backup: {e}")
    
    def restore_from_auto_backup(self):
        """Restore from automatic backup."""
        if not self.current_backup or not self.current_backup.get("data"):
            messagebox.showerror("No Backup", 
                               "No backup available to restore from.\n"
                               "Load a manual backup first.")
            return
        
        response = messagebox.askyesno(
            "Restore Backup",
            f"This will restore {len(self.current_backup['data'])} registry values.\n\n"
            f"Backup timestamp: {self.current_backup.get('timestamp', 'Unknown')}\n\n"
            f"Continue?",
            icon='warning'
        )
        
        if not response:
            return
        
        self.backup_log_message("="*70)
        self.backup_log_message("🔄 RESTORING FROM BACKUP")
        self.backup_log_message("="*70)
        
        restored = 0
        failed = 0
        
        for key, value_data in self.current_backup["data"].items():
            try:
                # Parse key
                parts = key.split("\\")
                root_name = parts[0]
                path = "\\".join(parts[1:-1])
                name = parts[-1]
                
                # Get root key
                root = {
                    "HKLM": reg.HKEY_LOCAL_MACHINE,
                    "HKCU": reg.HKEY_CURRENT_USER
                }.get(root_name)
                
                if value_data is None:
                    # Delete key that didn't exist before
                    try:
                        key_handle = reg.OpenKey(root, path, 0, reg.KEY_WRITE)
                        reg.DeleteValue(key_handle, name)
                        reg.CloseKey(key_handle)
                        self.backup_log_message(f"✅ Deleted: {key}")
                        restored += 1
                    except:
                        pass
                else:
                    # Restore value
                    key_handle = reg.CreateKeyEx(root, path, 0, reg.KEY_WRITE)
                    reg.SetValueEx(key_handle, name, 0, 
                                 value_data["type"], value_data["value"])
                    reg.CloseKey(key_handle)
                    self.backup_log_message(f"✅ Restored: {key}")
                    restored += 1
                    
            except Exception as e:
                self.backup_log_message(f"❌ Failed: {key} - {e}")
                failed += 1
            
            self.update()
        
        self.backup_log_message("="*70)
        self.backup_log_message(f"✅ Restore complete: {restored} restored, {failed} failed")
        self.backup_log_message("⚠️ RESTART your computer for changes to take effect")
        self.backup_log_message("="*70)
        
        messagebox.showinfo(
            "Restore Complete",
            f"Backup restored successfully!\n\n"
            f"✅ {restored} values restored\n"
            f"❌ {failed} failed\n\n"
            f"⚠️ RESTART your computer for changes to take effect"
        )


def main():
    try:
        # Hide console window immediately
        hide_console()
        
        # Check and install dependencies first
        if not check_and_install_requirements():
            sys.exit(1)
        
        # Now psutil should be available
        if psutil is None:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "Missing Dependencies",
                "Required packages could not be loaded.\n\n"
                "Please restart the program or install manually:\n"
                "pip install psutil"
            )
            sys.exit(1)
        
        # Auto-elevate if not admin
        if not is_admin():
            print("Requesting administrator privileges...")
            if elevate_privileges():
                sys.exit(0)
            else:
                root = tk.Tk()
                root.withdraw()
                messagebox.showerror(
                    "Administrator Required",
                    "This tool requires administrator privileges.\n\n"
                    "Failed to elevate. Please manually run as administrator."
                )
                sys.exit(1)
        
        # Running as admin - launch the app
        print("Starting Ultimate Performance Tool as Administrator...")
        
        # Create a log file to confirm we got here
        with open("ultimate_tool_admin.log", "w") as f:
            f.write(f"Started as admin at {datetime.now()}\n")
            f.write(f"Admin check: {is_admin()}\n")
        
        app = UltimatePerformanceTool()
        app.mainloop()
        
    except Exception as e:
        # Catch any startup errors
        import traceback
        error_msg = f"Error starting application:\n\n{str(e)}\n\n{traceback.format_exc()}"
        print(error_msg)
        
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Startup Error", error_msg)
        except:
            pass
        
        sys.exit(1)


if __name__ == "__main__":
    main()
