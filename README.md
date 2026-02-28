# Factory Test Tool

A Qt-based desktop application for factory testing and firmware management of SAMO (qrb5165-rb5) robotics devices. The tool provides a graphical interface for querying device information, performing firmware updates, and running hardware tests via ADB and fastboot.

## Features

### Info Tab
- **Version Query** — Retrieve camera and gimbal firmware versions from the connected device
- Displays output from `/etc/aerora-version` and `/etc/gimbal-version`

### Update Tab
- **Enter Update Mode** — Reboot device into bootloader (fastboot) mode
- **Update Bootloader** — Flash `abl.elf` to both `abl_a` and `abl_b` partitions
- **Update Kernel** — Flash boot image (`qti-ubuntu-robotics-image-qrb5165-rb5-boot.img`)
- **Update File System** — Flash system image (`qti-ubuntu-robotics-image-qrb5165-rb5-sysfs.ext4`)
- **Reboot** — Reboot device from fastboot mode
- Real-time log output with timestamps

### Test Tab
- **Dual Mode Test** — Configure camera for dual mode (`CAM_DIS_MODE` = 3) and reboot
- **SDCard Test** — Verify SD card mount and run read/write test
- **Reset** — Remove camera parameters and reboot device

## Requirements

### System
- **ADB** (Android Debug Bridge) — must be installed and in `PATH`
- **Fastboot** — must be installed and in `PATH`
- Linux (tested on Ubuntu)

### Python
- Python 3.8+
- PySide6 >= 6.5.0

## Installation

```bash
# Clone or navigate to the project
cd factory_tool

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Run the application

```bash
python main.py
```

### Update workflow

1. Connect the device via USB and ensure ADB can see it (`adb devices`)
2. Open the **Update** tab
3. Click **Select Update Folder** and choose the folder containing:
   - `abl.elf` — bootloader image
   - `qti-ubuntu-robotics-image-qrb5165-rb5-boot.img` — kernel/boot image
   - `qti-ubuntu-robotics-image-qrb5165-rb5-sysfs.ext4` — system filesystem image
4. Click **Entry update mode** to reboot into fastboot
5. Wait for "Fastboot device detected" (device must be in fastboot mode)
6. Flash components in order: **Update Bootloader** → **Update Kernel** → **Update File System**
7. Click **Reboot** when done

### Build standalone executable (optional)

```bash
pyinstaller --onefile --windowed main.py
```

The executable will be in `dist/main`.

## Project Structure

```
factory_tool/
├── main.py          # Application entry, main window with tab widget
├── info.py          # Info tab — version query via ADB
├── update.py        # Update tab — bootloader/kernel/filesystem flashing
├── test.py          # Test tab — dual mode, SDCard, reset tests
├── requirements.txt
└── README.md
```

## License

Internal/factory use.
