#!/usr/bin/env python
"""
Gaming Performance Benchmark Tool - GUI Version
Visual benchmark with real-time progress and comparison features.
"""
import psutil
import time
import json
import os
from datetime import datetime
import platform
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog

class BenchmarkGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Gaming Performance Benchmark Tool")
        self.geometry("900x700")
        
        self.results = {}
        self.is_running = False
        
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="🎮 Gaming Performance Benchmark", 
                               font=('TkDefaultFont', 14, 'bold'))
        title_label.pack(pady=10)
        
        # Instructions
        instructions = ttk.LabelFrame(main_frame, text="📋 Instructions", padding="10")
        instructions.pack(fill=tk.X, pady=5)
        
        instr_text = (
            "1. Click 'Run BEFORE Benchmark' to establish baseline\n"
            "2. Apply privacy tweaks using the Privacy Utility\n"
            "3. Restart your computer\n"
            "4. Click 'Run AFTER Benchmark' to measure improvements\n"
            "5. Click 'Compare Results' to see the difference"
        )
        ttk.Label(instructions, text=instr_text, justify=tk.LEFT).pack()
        
        # System Info Frame
        self.info_frame = ttk.LabelFrame(main_frame, text="💻 System Information", padding="10")
        self.info_frame.pack(fill=tk.X, pady=5)
        
        self.info_text = tk.Text(self.info_frame, height=4, wrap=tk.WORD, state=tk.DISABLED)
        self.info_text.pack(fill=tk.X)
        
        # Progress Frame
        progress_frame = ttk.LabelFrame(main_frame, text="⏱️ Benchmark Progress", padding="10")
        progress_frame.pack(fill=tk.X, pady=5)
        
        self.progress_label = ttk.Label(progress_frame, text="Ready to start benchmark")
        self.progress_label.pack()
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                           maximum=100, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        # Results Frame
        results_frame = ttk.LabelFrame(main_frame, text="📊 Benchmark Results", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, 
                                                     state=tk.DISABLED, height=15)
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        # Buttons Frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        self.before_btn = ttk.Button(buttons_frame, text="🎯 Run BEFORE Benchmark", 
                                     command=self.run_before_benchmark)
        self.before_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.after_btn = ttk.Button(buttons_frame, text="✅ Run AFTER Benchmark", 
                                    command=self.run_after_benchmark)
        self.after_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.compare_btn = ttk.Button(buttons_frame, text="📈 Compare Results", 
                                      command=self.compare_results)
        self.compare_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        ttk.Button(buttons_frame, text="🗑️ Clear", 
                  command=self.clear_results).pack(side=tk.RIGHT, padx=5)
        
        # Load system info immediately
        self.load_system_info()
    
    def load_system_info(self):
        """Load and display system information."""
        info = {
            "OS": f"{platform.system()} {platform.release()}",
            "Processor": platform.processor(),
            "CPU Cores": f"{psutil.cpu_count(logical=False)} physical, {psutil.cpu_count(logical=True)} logical",
            "RAM": f"{round(psutil.virtual_memory().total / (1024**3), 2)} GB"
        }
        
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete('1.0', tk.END)
        for key, value in info.items():
            self.info_text.insert(tk.END, f"{key}: {value}\n")
        self.info_text.config(state=tk.DISABLED)
    
    def log(self, message):
        """Add message to results display."""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.insert(tk.END, message + "\n")
        self.results_text.see(tk.END)
        self.results_text.config(state=tk.DISABLED)
        self.update_idletasks()
    
    def clear_results(self):
        """Clear the results display."""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete('1.0', tk.END)
        self.results_text.config(state=tk.DISABLED)
        self.progress_var.set(0)
        self.progress_label.config(text="Ready to start benchmark")
    
    def update_progress(self, value, label=""):
        """Update progress bar and label."""
        self.progress_var.set(value)
        if label:
            self.progress_label.config(text=label)
        self.update_idletasks()
    
    def disable_buttons(self):
        """Disable all benchmark buttons."""
        self.before_btn.config(state=tk.DISABLED)
        self.after_btn.config(state=tk.DISABLED)
        self.compare_btn.config(state=tk.DISABLED)
    
    def enable_buttons(self):
        """Enable all benchmark buttons."""
        self.before_btn.config(state=tk.NORMAL)
        self.after_btn.config(state=tk.NORMAL)
        self.compare_btn.config(state=tk.NORMAL)
    
    def run_before_benchmark(self):
        """Run benchmark before privacy tweaks."""
        self.clear_results()
        self.log("="*70)
        self.log("BASELINE BENCHMARK (BEFORE Privacy Tweaks)")
        self.log("="*70)
        self.run_benchmark("benchmark_before.json")
    
    def run_after_benchmark(self):
        """Run benchmark after privacy tweaks."""
        self.clear_results()
        self.log("="*70)
        self.log("AFTER BENCHMARK (AFTER Privacy Tweaks)")
        self.log("="*70)
        self.run_benchmark("benchmark_after.json")
    
    def run_benchmark(self, filename):
        """Run the full benchmark suite."""
        if self.is_running:
            messagebox.showwarning("Benchmark Running", "A benchmark is already in progress.")
            return
        
        self.is_running = True
        self.disable_buttons()
        
        # Run in thread to avoid freezing GUI
        thread = threading.Thread(target=self._benchmark_worker, args=(filename,), daemon=True)
        thread.start()
    
    def _benchmark_worker(self, filename):
        """Worker thread for benchmark."""
        try:
            self.results = {"timestamp": datetime.now().isoformat()}
            
            # Test 1: System Info
            self.update_progress(10, "Collecting system information...")
            self._test_system_info()
            
            # Test 2: Memory
            self.update_progress(20, "Testing memory performance...")
            self._test_memory()
            
            # Test 3: Disk
            self.update_progress(30, "Testing disk I/O...")
            self._test_disk()
            
            # Test 4: Network
            self.update_progress(40, "Testing network activity...")
            self._test_network()
            
            # Test 5: Processes
            self.update_progress(50, "Analyzing background processes...")
            self._test_processes()
            
            # Test 6: Services
            self.update_progress(60, "Checking Windows services...")
            self._test_services()
            
            # Test 7: CPU (takes longest)
            self.update_progress(70, "Testing CPU performance (this may take a moment)...")
            self._test_cpu()
            
            # Save results
            self.update_progress(90, "Saving results...")
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2)
            
            self.update_progress(100, f"Benchmark complete! Saved to {filename}")
            self.log(f"\n✅ Benchmark saved to: {filename}")
            
            # Show summary
            self.after(100, lambda: self._show_summary())
            
        except Exception as e:
            self.log(f"\n❌ Error during benchmark: {e}")
            import traceback
            self.log(traceback.format_exc())
        finally:
            self.is_running = False
            self.after(100, self.enable_buttons)
    
    def _test_system_info(self):
        """Test system information."""
        self.log("\n📋 System Information:")
        info = {
            "os": platform.system() + " " + platform.release(),
            "processor": platform.processor(),
            "cpu_cores": psutil.cpu_count(logical=False),
            "cpu_threads": psutil.cpu_count(logical=True),
            "ram_total_gb": round(psutil.virtual_memory().total / (1024**3), 2)
        }
        self.results["system"] = info
        for key, value in info.items():
            self.log(f"  {key}: {value}")
    
    def _test_memory(self):
        """Test memory."""
        self.log("\n💾 Memory Performance:")
        mem = psutil.virtual_memory()
        
        results = {
            "total_gb": round(mem.total / (1024**3), 2),
            "available_gb": round(mem.available / (1024**3), 2),
            "used_gb": round(mem.used / (1024**3), 2),
            "percent_used": mem.percent
        }
        self.results["memory"] = results
        
        self.log(f"  Total RAM: {results['total_gb']} GB")
        self.log(f"  Available: {results['available_gb']} GB")
        self.log(f"  Used: {results['used_gb']} GB ({results['percent_used']}%)")
    
    def _test_disk(self):
        """Test disk I/O."""
        self.log("\n💿 Disk I/O Performance:")
        
        disk_io_before = psutil.disk_io_counters()
        time.sleep(2)
        disk_io_after = psutil.disk_io_counters()
        
        read_mb = (disk_io_after.read_bytes - disk_io_before.read_bytes) / (1024**2)
        write_mb = (disk_io_after.write_bytes - disk_io_before.write_bytes) / (1024**2)
        
        results = {
            "read_mb_per_sec": round(read_mb / 2, 2),
            "write_mb_per_sec": round(write_mb / 2, 2)
        }
        self.results["disk"] = results
        
        self.log(f"  Read Speed: {results['read_mb_per_sec']} MB/s")
        self.log(f"  Write Speed: {results['write_mb_per_sec']} MB/s")
    
    def _test_network(self):
        """Test network."""
        self.log("\n🌐 Network Activity:")
        
        net_io_before = psutil.net_io_counters()
        time.sleep(2)
        net_io_after = psutil.net_io_counters()
        
        sent_mb = (net_io_after.bytes_sent - net_io_before.bytes_sent) / (1024**2)
        recv_mb = (net_io_after.bytes_recv - net_io_before.bytes_recv) / (1024**2)
        
        results = {
            "upload_mb_per_sec": round(sent_mb / 2, 2),
            "download_mb_per_sec": round(recv_mb / 2, 2)
        }
        self.results["network"] = results
        
        self.log(f"  Upload: {results['upload_mb_per_sec']} MB/s")
        self.log(f"  Download: {results['download_mb_per_sec']} MB/s")
    
    def _test_processes(self):
        """Test background processes."""
        self.log("\n⚙️ Background Processes:")
        
        processes = list(psutil.process_iter(['name', 'cpu_percent', 'memory_percent']))
        total = len(processes)
        
        # Get top CPU users
        processes.sort(key=lambda p: p.info['cpu_percent'] or 0, reverse=True)
        top_cpu = [{"name": p.info['name'], "cpu": round(p.info['cpu_percent'] or 0, 2)} 
                   for p in processes[:5] if p.info['cpu_percent']]
        
        results = {
            "total_processes": total,
            "top_cpu_users": top_cpu
        }
        self.results["processes"] = results
        
        self.log(f"  Total Running: {total}")
        self.log(f"  Top CPU Users:")
        for proc in top_cpu[:3]:
            self.log(f"    - {proc['name']}: {proc['cpu']}%")
    
    def _test_services(self):
        """Test Windows services."""
        self.log("\n🔧 Windows Services:")
        
        services = {
            "WinDefend": "Windows Defender",
            "DiagTrack": "Telemetry",
            "dmwappushservice": "WAP Push",
            "wuauserv": "Windows Update"
        }
        
        status = {}
        for service, desc in services.items():
            try:
                result = subprocess.run(["sc", "query", service], 
                                      capture_output=True, text=True, check=False)
                if "RUNNING" in result.stdout:
                    stat = "running"
                elif "STOPPED" in result.stdout:
                    stat = "stopped"
                else:
                    stat = "unknown"
            except:
                stat = "error"
            
            status[service] = stat
            self.log(f"  {desc}: {stat.upper()}")
        
        self.results["services"] = status
    
    def _test_cpu(self):
        """Test CPU performance."""
        self.log("\n🖥️ CPU Performance (10 seconds):")
        
        samples = []
        for i in range(10):
            cpu = psutil.cpu_percent(interval=1)
            samples.append(cpu)
            self.log(f"  Sample {i+1}/10: {cpu}%")
        
        results = {
            "average": round(sum(samples) / len(samples), 2),
            "min": round(min(samples), 2),
            "max": round(max(samples), 2)
        }
        self.results["cpu"] = results
        
        self.log(f"\n  Average CPU: {results['average']}%")
        self.log(f"  Min: {results['min']}% | Max: {results['max']}%")
    
    def _show_summary(self):
        """Show benchmark summary."""
        self.log("\n" + "="*70)
        self.log("📊 BENCHMARK SUMMARY")
        self.log("="*70)
        
        if "cpu" in self.results:
            self.log(f"Average CPU Usage: {self.results['cpu']['average']}%")
        if "memory" in self.results:
            self.log(f"Available RAM: {self.results['memory']['available_gb']} GB")
        if "processes" in self.results:
            self.log(f"Background Processes: {self.results['processes']['total_processes']}")
        
        self.log("\n✅ Benchmark complete!")
    
    def compare_results(self):
        """Compare before and after benchmarks."""
        before_file = "benchmark_before.json"
        after_file = "benchmark_after.json"
        
        if not os.path.exists(before_file) or not os.path.exists(after_file):
            messagebox.showwarning(
                "Missing Benchmarks",
                f"Please run both 'BEFORE' and 'AFTER' benchmarks first.\n\n"
                f"Found:\n"
                f"  Before: {'✅' if os.path.exists(before_file) else '❌'}\n"
                f"  After: {'✅' if os.path.exists(after_file) else '❌'}"
            )
            return
        
        self.clear_results()
        self.log("="*70)
        self.log("📈 BENCHMARK COMPARISON")
        self.log("="*70)
        
        try:
            with open(before_file, 'r') as f:
                before = json.load(f)
            with open(after_file, 'r') as f:
                after = json.load(f)
            
            # CPU Comparison
            if 'cpu' in before and 'cpu' in after:
                self.log("\n🖥️ CPU Performance:")
                cpu_before = before['cpu']['average']
                cpu_after = after['cpu']['average']
                diff = cpu_after - cpu_before
                improvement = ((cpu_before - cpu_after) / cpu_before * 100) if cpu_before > 0 else 0
                
                self.log(f"  Before: {cpu_before}%")
                self.log(f"  After:  {cpu_after}%")
                self.log(f"  Change: {diff:+.2f}%")
                
                if improvement > 0:
                    self.log(f"  ✅ {improvement:.1f}% IMPROVEMENT in CPU usage!")
                elif improvement < 0:
                    self.log(f"  ⚠️ {abs(improvement):.1f}% increase in CPU usage")
                else:
                    self.log(f"  ➡️ No significant change")
            
            # Memory Comparison
            if 'memory' in before and 'memory' in after:
                self.log("\n💾 Memory Performance:")
                mem_before = before['memory']['available_gb']
                mem_after = after['memory']['available_gb']
                diff = mem_after - mem_before
                
                self.log(f"  Available RAM Before: {mem_before} GB")
                self.log(f"  Available RAM After:  {mem_after} GB")
                self.log(f"  Change: {diff:+.2f} GB")
                
                if diff > 0.1:
                    self.log(f"  ✅ {diff:.2f} GB MORE RAM available!")
                elif diff < -0.1:
                    self.log(f"  ⚠️ {abs(diff):.2f} GB less RAM available")
                else:
                    self.log(f"  ➡️ No significant change")
            
            # Process Comparison
            if 'processes' in before and 'processes' in after:
                self.log("\n⚙️ Background Processes:")
                proc_before = before['processes']['total_processes']
                proc_after = after['processes']['total_processes']
                diff = proc_after - proc_before
                
                self.log(f"  Before: {proc_before} processes")
                self.log(f"  After:  {proc_after} processes")
                self.log(f"  Change: {diff:+d}")
                
                if diff < -5:
                    self.log(f"  ✅ {abs(diff)} FEWER background processes!")
                elif diff > 5:
                    self.log(f"  ⚠️ {diff} more background processes")
                else:
                    self.log(f"  ➡️ No significant change")
            
            # Service Changes
            if 'services' in before and 'services' in after:
                self.log("\n🔧 Service Changes:")
                changes = []
                for service, status_after in after['services'].items():
                    status_before = before['services'].get(service, 'unknown')
                    if status_before != status_after:
                        changes.append(f"  {service}: {status_before} → {status_after}")
                
                if changes:
                    for change in changes:
                        self.log(change)
                else:
                    self.log("  No service changes detected")
            
            self.log("\n" + "="*70)
            self.log("🎮 GAMING IMPACT ASSESSMENT")
            self.log("="*70)
            
            # Calculate overall score
            improvements = 0
            if 'cpu' in before and 'cpu' in after:
                if before['cpu']['average'] > after['cpu']['average']:
                    improvements += 1
            if 'memory' in before and 'memory' in after:
                if before['memory']['available_gb'] < after['memory']['available_gb']:
                    improvements += 1
            if 'processes' in before and 'processes' in after:
                if before['processes']['total_processes'] > after['processes']['total_processes']:
                    improvements += 1
            
            if improvements >= 2:
                self.log("\n✅ POSITIVE IMPACT - Should improve gaming performance!")
            elif improvements == 1:
                self.log("\n➡️ SLIGHT IMPACT - Minor improvements detected")
            else:
                self.log("\n⚠️ MINIMAL IMPACT - No significant improvements")
            
        except Exception as e:
            self.log(f"\n❌ Error comparing results: {e}")
            import traceback
            self.log(traceback.format_exc())


def main():
    app = BenchmarkGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
