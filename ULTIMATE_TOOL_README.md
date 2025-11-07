# 🎮 Ultimate Windows Performance & Privacy Tool

**All-in-one solution for Windows optimization, privacy configuration, and gaming performance.**

## 🌟 Features

### 🎮 Gaming Boost
- One-click temporary performance boost
- Stops telemetry, search indexing, and SuperFetch
- Real-time system monitoring (CPU, RAM, processes)
- Safe & reversible - resets after reboot

### 🔒 Privacy Settings
- Permanent privacy configurations
- **Automatic backup before changes**
- Configure: Defender, Telemetry, Activity Tracking, Advertising, Cortana
- Enable/disable mode for easy restoration

### 📊 Performance Benchmarking
- Before/after comparison testing
- Measures CPU, RAM, and process counts
- Automatic comparison when both tests complete
- Saved results for tracking improvements

### 💾 Automatic Backup & Restore
- **Auto-creates backups** before applying privacy changes
- One-click restore to original settings
- Manual backup export/import
- Full registry value restoration

---

## 📋 Requirements

- **Windows 10/11**
- **Python 3.7+** (tested with Python 3.13)
- **Administrator privileges** (auto-requested)
- **Python package:** psutil

---

## 🚀 Quick Start (For New Users)

### Option 1: No Console Window (Cleanest - Recommended)
1. Double-click `Ultimate_Performance_Tool_NoConsole.pyw`
2. No console window appears - just the GUI
3. Click **Yes** when prompted for administrator privileges
4. Tool launches with clean interface!

### Option 2: Automatic Installation (With Console)
1. Double-click `Ultimate_Performance_Tool.py`
2. Console window will hide automatically after starting
3. If prompted about missing packages, click **Yes** to auto-install
4. Click **Yes** when prompted for administrator privileges
5. Tool will launch automatically!

### Option 3: Manual Installation
1. **Install Python** (if not installed):
   - Download from: https://www.python.org/downloads/
   - ✅ Check "Add Python to PATH" during installation

2. **Open Command Prompt or PowerShell**

3. **Install required package:**
   ```powershell
   pip install psutil
   ```
   
   Or install from requirements file:
   ```powershell
   pip install -r requirements.txt
   ```

4. **Run the program:**
   ```powershell
   python Ultimate_Performance_Tool.py
   ```

5. **Click Yes** when prompted for administrator privileges

---

## 📖 How to Use

### 🎮 Gaming Boost Tab
1. View current system status (CPU, RAM, processes)
2. Click **"🚀 BOOST FOR GAMING"** before playing games
3. Play your games with optimized performance
4. Click **"↩️ RESTORE NORMAL"** when done gaming
5. Or just restart your computer (auto-restores)

### 🔒 Privacy Settings Tab
1. Select features you want to modify (checkboxes)
2. Choose action: **Disable** (privacy) or **Enable** (restore)
3. Click **"⚡ APPLY PRIVACY CHANGES"**
4. **Automatic backup is created** before changes
5. **Restart your computer** for changes to take effect

⚠️ **Important:** Privacy changes are permanent until restored!

### 📊 Benchmark Tab
1. Click **"🎯 Run BEFORE Benchmark"** (without boost active)
2. Wait for test to complete (~10 seconds)
3. Apply gaming boost from Gaming Boost tab
4. Click **"✅ Run AFTER Benchmark"**
5. View automatic comparison results

### 💾 Backup & Restore Tab
- **View automatic backup status**: See when backup was created
- **Save manual backup**: Export backup file for safekeeping
- **Load backup**: Import previously saved backup
- **Restore from backup**: Revert all privacy changes (requires restart)

---

## 🛡️ Safety Features

✅ **Automatic backups** - No manual backup needed  
✅ **Administrator verification** - Won't run without proper privileges  
✅ **Clear warnings** - Know what requires restart  
✅ **Reversible changes** - Can always restore original settings  
✅ **Gaming boost is temporary** - Automatically resets on reboot  
✅ **No permanent damage** - All changes can be undone

---

## 📊 What Gets Optimized?

### Gaming Boost (Temporary):
- **DiagTrack** - Telemetry and diagnostics
- **WSearch** - Windows Search indexing
- **SysMain** - SuperFetch memory pre-loading

### Privacy Settings (Permanent):
- **Windows Defender** - Real-time protection, antispyware
- **Telemetry** - Data collection, diagnostics tracking
- **Activity & Recall** - Timeline, activity history, AI snapshots
- **Advertising** - Advertising ID, suggested apps
- **Cortana** - Voice assistant

---

## ❓ Troubleshooting

### "Missing Dependencies" error
- Click **Yes** to auto-install, or
- Manually run: `pip install psutil`

### Tool won't start
- Make sure you have Python installed
- Right-click `Ultimate_Performance_Tool.py` → **"Run as administrator"**

### Changes not taking effect
- Privacy changes require a **restart**
- Gaming boost is temporary - check if services were stopped

### Can't restore backup
- Make sure you applied privacy changes first (creates backup)
- Check that `auto_backup_ultimate.json` exists
- Try loading a manual backup if available

### Admin privileges not working
- Right-click PowerShell → **"Run as administrator"**
- Run: `python Ultimate_Performance_Tool.py`

---

## 📁 Files Created

- `auto_backup_ultimate.json` - Automatic backup (created on privacy changes)
- `benchmark_before.json` - Before benchmark results
- `benchmark_after.json` - After benchmark results
- Manual backup files (user-created, optional)

---

## ⚠️ Important Notes

1. **Administrator privileges required** - Tool modifies system settings
2. **Privacy changes are permanent** - Until restored from backup
3. **Gaming boost is temporary** - Resets after reboot
4. **Always create backups** - Done automatically for privacy changes
5. **Restart required** - For privacy setting changes to take effect

---

## 🎯 Best Practices

### For Gaming:
1. Run BEFORE benchmark without boost
2. Close unnecessary programs
3. Apply gaming boost
4. Run AFTER benchmark to see improvement
5. Keep boost active while gaming
6. Restore normal when done

### For Privacy:
1. Read what each feature does
2. Start with one feature at a time
3. Automatic backup is created for you
4. Test changes after restart
5. Keep manual backup for extra safety
6. Can always restore from Backup & Restore tab

### For Benchmarking:
1. Close all unnecessary programs before testing
2. Wait a few minutes after boot for system to settle
3. Run tests multiple times for accuracy
4. Results vary based on system activity

---

## 🔧 Technical Details

- **Language:** Python 3
- **GUI Framework:** tkinter (built-in)
- **System Libraries:** winreg, subprocess, ctypes
- **Monitoring:** psutil
- **Platform:** Windows 10/11 (64-bit)

---

## 📝 License

Free to use for personal purposes. No warranty provided.

---

## 💬 Support

If you encounter issues:
1. Check the Troubleshooting section above
2. Ensure Python and psutil are installed
3. Run as administrator
4. Check that you're on Windows 10/11

---

## 🎉 Enjoy Your Optimized System!

**Remember:** Gaming boost is temporary (safe), privacy changes are permanent (backup created automatically).
