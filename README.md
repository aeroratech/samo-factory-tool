# Factory Test Tool

A Qt-based desktop GUI tool for testing and updating SAMO (qrb5165-rb5) devices. The tool communicates with devices over ADB/fastboot and provides a streamlined interface for device management and factory testing.

## Features

The tool is organized into three tabs:

### Info Tab
- Display device version information
- Shows camera version (`/etc/aerora-version`)
- Shows gimbal version (`/etc/gimbal-version`)
- Real-time log output with timestamps

### Update Tab
- Bootloader update (`abl.elf` flashed to both `abl_a` and `abl_b` slots)
- Kernel update (`qti-ubuntu-robotics-image-qrb5165-rb5-boot.img`)
- Filesystem update (`qti-ubuntu-robotics-image-qrb5165-rb5-sysfs.ext4`)
- Device reboot functionality
- Automatic update sequence (bootloader → kernel → filesystem)
- Real-time update progress logging

### Test Tab
- **Device Status Monitor**: Real-time device connection status
- **Dual Mode Test**: Configures camera for dual mode operation by setting `CAM_DIS_MODE` to `3` in `/data/camera/cam_param.bin`
- **SDCard Test**: Verifies SD card presence and performs write/read functionality test
- **Reset**: Deletes camera parameter file and reboots device to restore defaults
- All test functions automatically reboot the device upon completion

## Requirements

### System Requirements
- Python 3.7 or higher
- Linux/Windows/macOS with GUI support

### External Dependencies
- **ADB** - Android Debug Bridge must be installed and in your `PATH`
- **Fastboot** - Required for device updates and bootloader operations

### Python Dependencies
```
PySide6>=6.5.0
pyinstaller>=6.0
```

## Installation

### 1. Clone the repository
```bash
cd factory_tool
```

### 2. Create and activate virtual environment (optional but recommended)
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Verify ADB and Fastboot
```bash
adb version
fastboot --version
```

## Usage

### Starting the Application
```bash
python main.py
```

The application window will open with three tabs: Info, Update, and TEST.

### Info Tab Usage
1. Connect your device via USB
2. Verify device is visible: `adb devices`
3. Click the **Version** button to retrieve version information
4. Output will display camera and gimbal versions with timestamps
5. Use **Clear** to clear the log output

### Update Tab Usage
1. Connect device via USB
2. Select your update folder using **Select Update Folder** button
   - The folder must contain:
     - `abl.elf` (bootloader)
     - `qti-ubuntu-robotics-image-qrb5165-rb5-boot.img` (kernel)
     - `qti-ubuntu-robotics-image-qrb5165-rb5-sysfs.ext4` (filesystem)
3. Click **Entry update mode** to reboot device to bootloader
4. Wait for device to be detected in fastboot mode
5. Click **Update** to start the full update sequence:
   - Bootloader updates (both A and B slots)
   - Kernel update
   - Filesystem update
6. After successful update, click **Reboot** to restart the device

### TEST Tab Usage
1. Connect device via USB
2. Observe device status (Online/Offline) indicator
3. **Dual Mode Test**: Click to set camera to dual mode and reboot
4. **SDCard Test**: Click to verify SD card is mounted and functional
5. **Reset**: Click to reset camera parameters to defaults and reboot

## Building as Executable

To build the tool as a standalone executable:

```bash
pyinstaller --onefile --windowed main.py
```

The executable will be created in the `dist/` directory.

## Project Structure

```
factory_tool/
├── main.py          # Main application window and tab management
├── info.py          # Info tab - device version information
├── update.py        # Update tab - bootloader/kernel/filesystem updates
├── test.py          # Test tab - factory tests and device monitoring
├── requirements.txt # Python dependencies
└── README.md        # This file
```

## Troubleshooting

### Device not detected
- Verify USB cable is properly connected
- Run `adb devices` to check if device is visible
- Try disconnecting and reconnecting the device
- Ensure ADB drivers are installed (Windows)

### Update fails
- Ensure all required files are present in the selected folder
- Verify device is in fastboot mode (`fastboot devices`)
- Check that files are not corrupted
- Ensure sufficient disk space on device

### ADB permission errors (Linux)
```bash
# Add udev rules for ADB
sudo nano /etc/udev/rules.d/51-android.rules
# Add: SUBSYSTEM=="usb", ATTR{idVendor}=="05c6", MODE="0666"
sudo service udev restart
```

### Tests not working
- Ensure device is online (status indicator shows "Online" in green)
- Verify device is not in bootloader/fastboot mode (run `adb get-state`)
- Check test logs for specific error messages

## License

Internal / factory use only. Do not redistribute without permission.
