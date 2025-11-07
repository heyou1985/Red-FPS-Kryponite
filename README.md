# Windows Privacy & Performance Utility

A comprehensive GUI tool for managing Windows privacy settings, telemetry, and performance-related features.

## ⚠️ Important Warnings

- **Administrator Rights Required**: This tool requires administrator privileges to modify system settings.
- **Use with Caution**: Disabling Windows Defender or other security features can leave your system vulnerable.
- **Backup Your Settings**: Always create a backup before making changes.
- **Test First**: Use "Dry Run" mode to see what changes will be made before applying them.

## Features

### Privacy Controls
- **Windows Defender**: Enable/disable real-time protection and antispyware
- **Telemetry**: Control Windows data collection and diagnostic tracking
- **Activity & Recall**: Manage Windows Timeline, Activity History, and Recall features
- **Advertising**: Disable advertising ID and content suggestions
- **Cortana**: Enable/disable Cortana assistant

### Advanced Options
- **Aggressive Mode**: Disables Windows Update (use with extreme caution)
- **Dry Run**: Preview changes without applying them
- **Backup System**: Save and restore registry settings

### Safety Features
- Admin privilege detection and elevation
- Registry backup before making changes
- Detailed logging of all operations
- Service status verification
- Rollback capability

## How to Use

1. **Run as Administrator**: Right-click the script and select "Run as administrator" or use the "Restart as Admin" button in the app.

2. **Select Action**:
   - **Disable Features**: Turns off privacy-invasive features
   - **Enable Features**: Restores default Windows settings

3. **Choose Tweaks**: Select which privacy features to modify (all selected by default)

4. **Configure Options**:
   - Enable **Aggressive Mode** if you want to disable Windows Update (not recommended)
   - Keep **Dry Run** enabled to test without making changes
   - Keep **Create backup** enabled to save current settings

5. **Apply Changes**: Click "Apply Changes" to execute

6. **Save Backup**: After making changes, use "Save Backup" to save your registry backup to a file

7. **Restart**: Restart your computer for all changes to take effect

## Requirements

- Windows 10/11
- Python 3.7 or higher
- Administrator privileges

## Installation

1. Ensure Python is installed:
   ```powershell
   python --version
   ```

2. Run the script:
   ```powershell
   python "Privacy Utility - Copy.py"
   ```

## What This Tool Modifies

### Registry Changes
- `HKLM\SOFTWARE\Policies\Microsoft\Windows Defender`
- `HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection`
- `HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsAI`
- `HKCU\Software\Microsoft\Windows\CurrentVersion\AdvertisingInfo`
- And more...

### Services Modified
- Windows Defender (WinDefend)
- Connected User Experiences and Telemetry (DiagTrack)
- Windows Update (wuauserv) - only in Aggressive Mode
- Device Management Wireless Application Protocol (dmwappushservice)

## Backup & Restore

### Creating Backups
1. Enable "Create backup before making changes"
2. Apply changes
3. Click "Save Backup" and choose a location
4. Backup files are saved as JSON with timestamp

### Restoring from Backup
1. Click "Load Backup"
2. Select your backup JSON file
3. The backup data will be loaded (restore functionality can be implemented)

## Troubleshooting

### "Permission Denied" Errors
- Ensure you're running as Administrator
- Some settings may be controlled by Group Policy

### Changes Not Taking Effect
- Restart your computer
- Check if Group Policy overrides your changes
- Verify Windows Defender Tamper Protection is disabled

### Services Won't Stop/Start
- Some services are protected by Windows
- Check Windows Event Viewer for more details

## Security Recommendations

⚠️ **DO NOT disable Windows Defender unless you have alternative antivirus software installed!**

- Keep Windows Defender enabled for security
- Only disable telemetry if privacy is a major concern
- Avoid using Aggressive Mode (it disables Windows Update)
- Always create backups before making changes
- Test changes in a virtual machine first if possible

## Technical Details

- Built with Python's `tkinter` for GUI
- Uses `winreg` module for registry operations
- Uses `subprocess` for service management
- Threaded operations to prevent UI freezing
- Comprehensive error handling and logging

## License

This tool is provided as-is for educational purposes. Use at your own risk.

## Version

Version 1.0 - Enhanced Edition with Auto-Elevation
