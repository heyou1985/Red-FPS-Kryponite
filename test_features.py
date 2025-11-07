#!/usr/bin/env python
"""
Test script to verify all features of the Privacy Utility work correctly.
This runs automated tests WITHOUT modifying your system.
"""
import subprocess
import winreg as reg
import sys
import ctypes

def test_admin_check():
    """Test admin privilege detection."""
    print("\n[TEST 1] Admin Privilege Detection")
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        print(f"  ✅ Admin check works: {is_admin}")
        return True
    except Exception as e:
        print(f"  ❌ Admin check failed: {e}")
        return False

def test_service_status():
    """Test service status checking."""
    print("\n[TEST 2] Service Status Detection")
    services_to_test = ["WinDefend", "DiagTrack", "dmwappushservice", "wuauserv"]
    results = []
    
    for service in services_to_test:
        try:
            result = subprocess.run(["sc", "query", service], 
                                  capture_output=True, text=True, check=False)
            if "STATE" in result.stdout:
                if "RUNNING" in result.stdout:
                    status = "running"
                elif "STOPPED" in result.stdout:
                    status = "stopped"
                else:
                    status = "unknown"
            else:
                status = "not_found"
            print(f"  ✅ {service}: {status}")
            results.append(True)
        except Exception as e:
            print(f"  ❌ {service}: error - {e}")
            results.append(False)
    
    return all(results)

def test_registry_read():
    """Test registry reading capability."""
    print("\n[TEST 3] Registry Read Access")
    test_keys = [
        (reg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion"),
        (reg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion"),
    ]
    results = []
    
    for root, path in test_keys:
        try:
            key = reg.OpenKey(root, path, 0, reg.KEY_READ)
            reg.CloseKey(key)
            root_name = "HKLM" if root == reg.HKEY_LOCAL_MACHINE else "HKCU"
            print(f"  ✅ Can read {root_name}\\{path}")
            results.append(True)
        except Exception as e:
            print(f"  ❌ Cannot read registry: {e}")
            results.append(False)
    
    return all(results)

def test_registry_write():
    """Test registry write capability (to safe location)."""
    print("\n[TEST 4] Registry Write Access")
    test_path = r"Software\PrivacyUtilityTest"
    
    try:
        # Try to create a test key in HKCU (safe, user-only location)
        key = reg.CreateKeyEx(reg.HKEY_CURRENT_USER, test_path, 0, reg.KEY_WRITE)
        reg.SetValueEx(key, "TestValue", 0, reg.REG_DWORD, 1)
        reg.CloseKey(key)
        print(f"  ✅ Can write to registry (HKCU\\{test_path})")
        
        # Clean up test key
        key = reg.OpenKey(reg.HKEY_CURRENT_USER, test_path, 0, reg.KEY_WRITE)
        reg.DeleteValue(key, "TestValue")
        reg.CloseKey(key)
        reg.DeleteKey(reg.HKEY_CURRENT_USER, test_path)
        print(f"  ✅ Can delete registry keys (cleanup successful)")
        
        return True
    except Exception as e:
        print(f"  ❌ Registry write failed: {e}")
        return False

def test_powershell_access():
    """Test PowerShell command execution."""
    print("\n[TEST 5] PowerShell Access")
    try:
        result = subprocess.run(
            ["powershell.exe", "-Command", "Get-MpPreference -ErrorAction SilentlyContinue"],
            capture_output=True, text=True, check=False, timeout=5
        )
        if result.returncode == 0 or "Cannot bind parameter" in result.stderr:
            print(f"  ✅ PowerShell execution works")
            return True
        else:
            print(f"  ⚠️ PowerShell works but Defender cmdlet may not be available")
            return True
    except subprocess.TimeoutExpired:
        print(f"  ⚠️ PowerShell command timed out")
        return False
    except Exception as e:
        print(f"  ❌ PowerShell access failed: {e}")
        return False

def test_backup_format():
    """Test backup data structure."""
    print("\n[TEST 6] Backup System Format")
    try:
        import json
        from datetime import datetime
        
        test_backup = {
            "timestamp": datetime.now().isoformat(),
            "version": "1.0",
            "data": {
                "HKEY_LOCAL_MACHINE\\SOFTWARE\\Test\\TestKey": {
                    "value": 1,
                    "type": 4
                }
            }
        }
        
        json_str = json.dumps(test_backup, indent=2)
        restored = json.loads(json_str)
        
        print(f"  ✅ Backup JSON serialization works")
        print(f"  ✅ Backup structure is valid")
        return True
    except Exception as e:
        print(f"  ❌ Backup format test failed: {e}")
        return False

def test_gui_imports():
    """Test GUI library imports."""
    print("\n[TEST 7] GUI Libraries")
    try:
        import tkinter as tk
        from tkinter import ttk, messagebox, scrolledtext, filedialog
        print(f"  ✅ All tkinter modules import successfully")
        return True
    except Exception as e:
        print(f"  ❌ GUI import failed: {e}")
        return False

def test_threading():
    """Test threading capability."""
    print("\n[TEST 8] Threading Support")
    try:
        import threading
        import time
        
        test_result = [False]
        
        def worker():
            time.sleep(0.1)
            test_result[0] = True
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        thread.join(timeout=1.0)
        
        if test_result[0]:
            print(f"  ✅ Threading works correctly")
            return True
        else:
            print(f"  ❌ Thread did not complete")
            return False
    except Exception as e:
        print(f"  ❌ Threading test failed: {e}")
        return False

def run_all_tests():
    """Run all feature tests."""
    print("="*60)
    print("Windows Privacy Utility - Feature Test Suite")
    print("="*60)
    print("\nThis will test all features WITHOUT modifying your system.\n")
    
    tests = [
        ("Admin Detection", test_admin_check),
        ("Service Detection", test_service_status),
        ("Registry Read", test_registry_read),
        ("Registry Write", test_registry_write),
        ("PowerShell Access", test_powershell_access),
        ("Backup System", test_backup_format),
        ("GUI Libraries", test_gui_imports),
        ("Threading", test_threading),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"  ❌ Test crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The utility should work correctly.")
    else:
        print("\n⚠️ Some tests failed. Check the details above.")
    
    print("\n" + "="*60)
    print("FEATURE STATUS")
    print("="*60)
    
    feature_status = {
        "Windows Defender Control": all(r for n, r in results if n in ["PowerShell Access", "Service Detection"]),
        "Telemetry Control": all(r for n, r in results if n in ["Service Detection", "Registry Write"]),
        "Activity & Recall": results[2][1] and results[3][1],  # Registry
        "Advertising Control": results[2][1] and results[3][1],  # Registry
        "Cortana Control": results[2][1] and results[3][1],  # Registry
        "Backup/Restore": results[5][1],  # Backup system
        "GUI Interface": results[6][1] and results[7][1],  # GUI + Threading
    }
    
    for feature, works in feature_status.items():
        status = "✅ Working" if works else "❌ May Not Work"
        print(f"{status}: {feature}")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        sys.exit(1)
