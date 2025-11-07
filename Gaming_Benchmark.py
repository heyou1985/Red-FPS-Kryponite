#!/usr/bin/env python
"""
Gaming Performance Benchmark Tool
Measures system performance metrics relevant to gaming before/after privacy tweaks.
"""
import psutil
import time
import json
import os
from datetime import datetime
import platform
import subprocess
import threading

class GamingBenchmark:
    def __init__(self):
        self.results = {}
        
    def get_system_info(self):
        """Get basic system information."""
        print("\n" + "="*70)
        print("SYSTEM INFORMATION")
        print("="*70)
        
        info = {
            "os": platform.system() + " " + platform.release(),
            "processor": platform.processor(),
            "cpu_cores": psutil.cpu_count(logical=False),
            "cpu_threads": psutil.cpu_count(logical=True),
            "ram_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "timestamp": datetime.now().isoformat()
        }
        
        for key, value in info.items():
            print(f"  {key}: {value}")
        
        self.results["system_info"] = info
        return info
    
    def test_cpu_performance(self, duration=10):
        """Test CPU performance and usage."""
        print("\n" + "="*70)
        print(f"CPU PERFORMANCE TEST (Running for {duration} seconds)")
        print("="*70)
        
        # Get baseline CPU usage
        print("  Measuring baseline CPU usage...")
        cpu_percent_samples = []
        cpu_freq_samples = []
        
        for i in range(duration):
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_freq = psutil.cpu_freq()
            cpu_percent_samples.append(cpu_percent)
            if cpu_freq:
                cpu_freq_samples.append(cpu_freq.current)
            print(f"    Sample {i+1}/{duration}: CPU Usage: {cpu_percent}% | Freq: {cpu_freq.current if cpu_freq else 'N/A'} MHz")
        
        # CPU stress test
        print("\n  Running CPU stress test...")
        stress_samples = []
        
        def cpu_stress():
            """CPU intensive task."""
            end_time = time.time() + duration
            while time.time() < end_time:
                _ = sum([i**2 for i in range(10000)])
        
        # Start stress test
        stress_thread = threading.Thread(target=cpu_stress)
        stress_thread.start()
        
        for i in range(duration):
            cpu_percent = psutil.cpu_percent(interval=1)
            stress_samples.append(cpu_percent)
            print(f"    Stress Sample {i+1}/{duration}: CPU Usage: {cpu_percent}%")
        
        stress_thread.join()
        
        results = {
            "baseline_cpu_avg": round(sum(cpu_percent_samples) / len(cpu_percent_samples), 2),
            "baseline_cpu_min": round(min(cpu_percent_samples), 2),
            "baseline_cpu_max": round(max(cpu_percent_samples), 2),
            "stress_cpu_avg": round(sum(stress_samples) / len(stress_samples), 2),
            "cpu_freq_avg_mhz": round(sum(cpu_freq_samples) / len(cpu_freq_samples), 2) if cpu_freq_samples else None,
            "cpu_cores": psutil.cpu_count(logical=False),
            "cpu_threads": psutil.cpu_count(logical=True)
        }
        
        print("\n  Results:")
        for key, value in results.items():
            print(f"    {key}: {value}")
        
        self.results["cpu"] = results
        return results
    
    def test_memory_performance(self):
        """Test memory availability and performance."""
        print("\n" + "="*70)
        print("MEMORY PERFORMANCE TEST")
        print("="*70)
        
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        results = {
            "total_ram_gb": round(mem.total / (1024**3), 2),
            "available_ram_gb": round(mem.available / (1024**3), 2),
            "used_ram_gb": round(mem.used / (1024**3), 2),
            "ram_percent_used": mem.percent,
            "swap_total_gb": round(swap.total / (1024**3), 2),
            "swap_used_gb": round(swap.used / (1024**3), 2),
            "swap_percent_used": swap.percent
        }
        
        print("  RAM Information:")
        print(f"    Total: {results['total_ram_gb']} GB")
        print(f"    Available: {results['available_ram_gb']} GB")
        print(f"    Used: {results['used_ram_gb']} GB ({results['ram_percent_used']}%)")
        print(f"  Swap/Page File:")
        print(f"    Total: {results['swap_total_gb']} GB")
        print(f"    Used: {results['swap_used_gb']} GB ({results['swap_percent_used']}%)")
        
        self.results["memory"] = results
        return results
    
    def test_disk_performance(self):
        """Test disk I/O performance."""
        print("\n" + "="*70)
        print("DISK PERFORMANCE TEST")
        print("="*70)
        
        # Get disk I/O counters before
        disk_io_before = psutil.disk_io_counters()
        time.sleep(2)
        disk_io_after = psutil.disk_io_counters()
        
        read_mb = (disk_io_after.read_bytes - disk_io_before.read_bytes) / (1024**2)
        write_mb = (disk_io_after.write_bytes - disk_io_before.write_bytes) / (1024**2)
        
        results = {
            "read_mb_per_sec": round(read_mb / 2, 2),
            "write_mb_per_sec": round(write_mb / 2, 2),
            "read_count": disk_io_after.read_count - disk_io_before.read_count,
            "write_count": disk_io_after.write_count - disk_io_before.write_count
        }
        
        print("  Disk I/O (2-second sample):")
        print(f"    Read Speed: {results['read_mb_per_sec']} MB/s")
        print(f"    Write Speed: {results['write_mb_per_sec']} MB/s")
        print(f"    Read Operations: {results['read_count']}")
        print(f"    Write Operations: {results['write_count']}")
        
        self.results["disk"] = results
        return results
    
    def test_background_processes(self):
        """Count and analyze background processes."""
        print("\n" + "="*70)
        print("BACKGROUND PROCESS ANALYSIS")
        print("="*70)
        
        processes = list(psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']))
        
        # Sort by CPU usage
        processes_by_cpu = sorted(processes, key=lambda p: p.info['cpu_percent'] or 0, reverse=True)
        
        # Sort by memory usage
        processes_by_mem = sorted(processes, key=lambda p: p.info['memory_percent'] or 0, reverse=True)
        
        # Count processes
        total_processes = len(processes)
        
        # Get top CPU consumers
        top_cpu = []
        for p in processes_by_cpu[:10]:
            if p.info['cpu_percent'] and p.info['cpu_percent'] > 0:
                top_cpu.append({
                    "name": p.info['name'],
                    "cpu_percent": round(p.info['cpu_percent'], 2)
                })
        
        # Get top memory consumers
        top_mem = []
        for p in processes_by_mem[:10]:
            if p.info['memory_percent'] and p.info['memory_percent'] > 0:
                top_mem.append({
                    "name": p.info['name'],
                    "memory_percent": round(p.info['memory_percent'], 2)
                })
        
        results = {
            "total_processes": total_processes,
            "top_cpu_users": top_cpu[:5],
            "top_memory_users": top_mem[:5]
        }
        
        print(f"  Total Running Processes: {total_processes}")
        print(f"\n  Top 5 CPU Users:")
        for proc in top_cpu[:5]:
            print(f"    {proc['name']}: {proc['cpu_percent']}%")
        
        print(f"\n  Top 5 Memory Users:")
        for proc in top_mem[:5]:
            print(f"    {proc['name']}: {proc['memory_percent']}%")
        
        self.results["processes"] = results
        return results
    
    def test_windows_services(self):
        """Check status of privacy-related services."""
        print("\n" + "="*70)
        print("WINDOWS SERVICES STATUS")
        print("="*70)
        
        services_to_check = {
            "WinDefend": "Windows Defender",
            "DiagTrack": "Telemetry",
            "dmwappushservice": "WAP Push Service",
            "wuauserv": "Windows Update",
            "SysMain": "Superfetch/Prefetch",
            "WSearch": "Windows Search"
        }
        
        service_status = {}
        
        for service_name, description in services_to_check.items():
            try:
                result = subprocess.run(
                    ["sc", "query", service_name],
                    capture_output=True, text=True, check=False
                )
                if "RUNNING" in result.stdout:
                    status = "running"
                elif "STOPPED" in result.stdout:
                    status = "stopped"
                else:
                    status = "unknown"
            except:
                status = "error"
            
            service_status[service_name] = status
            print(f"  {description} ({service_name}): {status.upper()}")
        
        self.results["services"] = service_status
        return service_status
    
    def test_network_latency(self):
        """Test network latency (useful for online gaming)."""
        print("\n" + "="*70)
        print("NETWORK LATENCY TEST")
        print("="*70)
        
        # Get network stats
        net_io_before = psutil.net_io_counters()
        time.sleep(2)
        net_io_after = psutil.net_io_counters()
        
        sent_mb = (net_io_after.bytes_sent - net_io_before.bytes_sent) / (1024**2)
        recv_mb = (net_io_after.bytes_recv - net_io_before.bytes_recv) / (1024**2)
        
        results = {
            "upload_mb_per_sec": round(sent_mb / 2, 2),
            "download_mb_per_sec": round(recv_mb / 2, 2),
            "packets_sent": net_io_after.packets_sent - net_io_before.packets_sent,
            "packets_recv": net_io_after.packets_recv - net_io_before.packets_recv
        }
        
        print("  Network Activity (2-second sample):")
        print(f"    Upload: {results['upload_mb_per_sec']} MB/s")
        print(f"    Download: {results['download_mb_per_sec']} MB/s")
        print(f"    Packets Sent: {results['packets_sent']}")
        print(f"    Packets Received: {results['packets_recv']}")
        
        self.results["network"] = results
        return results
    
    def run_full_benchmark(self, quick=False):
        """Run all benchmarks."""
        print("\n" + "="*70)
        print("GAMING PERFORMANCE BENCHMARK SUITE")
        print("="*70)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        duration = 5 if quick else 10
        
        self.get_system_info()
        self.test_memory_performance()
        self.test_disk_performance()
        self.test_network_latency()
        self.test_background_processes()
        self.test_windows_services()
        self.test_cpu_performance(duration=duration)
        
        print("\n" + "="*70)
        print("BENCHMARK COMPLETE")
        print("="*70)
        
        return self.results
    
    def save_results(self, filename=None):
        """Save benchmark results to JSON file."""
        if filename is None:
            filename = f"benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n✅ Results saved to: {filename}")
        return filename
    
    def compare_benchmarks(self, before_file, after_file):
        """Compare two benchmark results."""
        print("\n" + "="*70)
        print("BENCHMARK COMPARISON")
        print("="*70)
        
        with open(before_file, 'r', encoding='utf-8') as f:
            before = json.load(f)
        
        with open(after_file, 'r', encoding='utf-8') as f:
            after = json.load(f)
        
        print("\n📊 PERFORMANCE CHANGES:")
        
        # CPU comparison
        if 'cpu' in before and 'cpu' in after:
            print("\n  CPU Performance:")
            cpu_before = before['cpu']['baseline_cpu_avg']
            cpu_after = after['cpu']['baseline_cpu_avg']
            diff = cpu_after - cpu_before
            improvement = ((cpu_before - cpu_after) / cpu_before * 100) if cpu_before > 0 else 0
            
            print(f"    Baseline CPU Usage: {cpu_before}% → {cpu_after}% ({diff:+.2f}%)")
            if improvement > 0:
                print(f"    ✅ {improvement:.1f}% reduction in CPU usage!")
            elif improvement < 0:
                print(f"    ⚠️ {abs(improvement):.1f}% increase in CPU usage")
        
        # Memory comparison
        if 'memory' in before and 'memory' in after:
            print("\n  Memory Performance:")
            mem_before = before['memory']['available_ram_gb']
            mem_after = after['memory']['available_ram_gb']
            diff = mem_after - mem_before
            
            print(f"    Available RAM: {mem_before} GB → {mem_after} GB ({diff:+.2f} GB)")
            if diff > 0:
                print(f"    ✅ {diff:.2f} GB more RAM available!")
            elif diff < 0:
                print(f"    ⚠️ {abs(diff):.2f} GB less RAM available")
        
        # Process comparison
        if 'processes' in before and 'processes' in after:
            print("\n  Background Processes:")
            proc_before = before['processes']['total_processes']
            proc_after = after['processes']['total_processes']
            diff = proc_after - proc_before
            
            print(f"    Total Processes: {proc_before} → {proc_after} ({diff:+d})")
            if diff < 0:
                print(f"    ✅ {abs(diff)} fewer background processes!")
            elif diff > 0:
                print(f"    ⚠️ {diff} more background processes")
        
        # Service comparison
        if 'services' in before and 'services' in after:
            print("\n  Services Changed:")
            for service, status_after in after['services'].items():
                status_before = before['services'].get(service, 'unknown')
                if status_before != status_after:
                    print(f"    {service}: {status_before} → {status_after}")
        
        print("\n" + "="*70)


def main():
    import sys
    
    print("="*70)
    print("GAMING PERFORMANCE BENCHMARK TOOL")
    print("="*70)
    print("\nThis tool measures system performance metrics relevant to gaming.")
    print("\nUsage:")
    print("  1. Run BEFORE applying privacy tweaks: benchmark_before.json")
    print("  2. Apply privacy tweaks using the Privacy Utility")
    print("  3. Restart your computer")
    print("  4. Run AFTER applying tweaks: benchmark_after.json")
    print("  5. Compare results to see improvements")
    print("\n" + "="*70)
    
    if len(sys.argv) > 1 and sys.argv[1] == "compare":
        if len(sys.argv) < 4:
            print("\nUsage: python Gaming_Benchmark.py compare <before.json> <after.json>")
            return
        
        benchmark = GamingBenchmark()
        benchmark.compare_benchmarks(sys.argv[2], sys.argv[3])
        return
    
    # Run benchmark
    benchmark = GamingBenchmark()
    
    response = input("\nRun Quick Benchmark (5 sec) or Full Benchmark (10 sec)? [Q/F]: ").strip().upper()
    quick = response == 'Q'
    
    results = benchmark.run_full_benchmark(quick=quick)
    
    # Save results
    default_name = "benchmark_before.json" if not os.path.exists("benchmark_before.json") else "benchmark_after.json"
    filename = input(f"\nSave results as [{default_name}]: ").strip() or default_name
    
    benchmark.save_results(filename)
    
    print("\n" + "="*70)
    print("NEXT STEPS:")
    print("="*70)
    
    if "before" in filename:
        print("\n1. ✅ Baseline benchmark saved!")
        print("2. Now apply your privacy tweaks using the Privacy Utility")
        print("3. Restart your computer")
        print("4. Run this benchmark again to save 'benchmark_after.json'")
        print("5. Compare: python Gaming_Benchmark.py compare benchmark_before.json benchmark_after.json")
    else:
        print("\n1. ✅ After-tweaks benchmark saved!")
        print("2. To compare with before:")
        print(f"   python Gaming_Benchmark.py compare benchmark_before.json {filename}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nBenchmark interrupted by user.")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
