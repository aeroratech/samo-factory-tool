# Factory Test Tool

Desktop GUI tool (PySide6) for SAMO (`qrb5165-rb5`) factory operations over `adb` and `fastboot`.

## Overview

The app has 3 visible tabs:

- `Info`: Read camera/gimbal version files from target device.
- `Update`: Flash bootloader, kernel, and filesystem images.
- `config`: Change device configuration, including the background image.

The `TEST` tab still exists in the application but is hidden from the tab bar.

## Requirements

- Python `3.7+`
- `adb` in `PATH`
- `fastboot` in `PATH`
- GUI-capable host (Linux/Windows/macOS)

Python dependencies:

```bash
pip install -r requirements.txt
```

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Sanity check tools:

```bash
adb version
fastboot --version
```

## Update Package Layout

When selecting an update folder in the `Update` tab, it must include:

- `abl.elf`
- `qti-ubuntu-robotics-image-qrb5165-rb5-boot.img`
- `qti-ubuntu-robotics-image-qrb5165-rb5-sysfs.ext4`

## Tab Behavior

### Info Tab

- `Version` runs:
  - `adb shell cat /etc/aerora-version`
  - `adb shell cat /etc/gimbal-version`
- `Clear` clears the log.

### Update Tab

1. Click `Select Update Folder`.
2. Click `Entry update mode` (runs `adb root`, waits for the device, then `adb reboot bootloader`).
3. Tool waits and checks `fastboot devices`.
4. Click `Update` to run full chain:
   - `fastboot flash abl_a abl.elf`
   - `fastboot flash abl_b abl.elf`
   - `fastboot --slot all flash boot ...boot.img`
   - `fastboot --slot all flash system ...sysfs.ext4`
5. Click `Reboot` (runs `fastboot reboot`) after successful flash.

Notes:

- `Update` is disabled until a fastboot device is detected.
- `Reboot` is enabled after full update success (and can also be enabled after fastboot detection).

### config Tab

- On startup, the tab reads `/etc/systemd/system/mav_client.service` over `adb` and selects the matching camera type.
- Camera type and background image are unified in the camera type setting.
- `ACSL SAMO` sets `CAM_BRAND=ACSL`, `CAM_MODEL=SAMO`, and `background-image=/usr/share/weston/background_logo_acsl.png`.
- `AERORA D64TR` sets `CAM_BRAND=AERORA`, `CAM_MODEL=D64TR`, and `background-image=/usr/share/weston/background_logo_aeroratech.png`.
- `Apply Camera Type` updates `/etc/systemd/system/mav_client.service`, updates `/etc/xdg/weston/weston.ini`, runs `adb shell sync`, and prompts for reboot.
- `USB` connection uses `ExecStart=/usr/bin/mav_client -l -u udp://127.0.0.1:14570`.
- `Ethernet` uses `udp://192.168.144.100:14550 --connection_type ethernet`.
- `WLAN` uses `udp://192.168.251.2:14550 --connection_type wlan`.
- `Standalone mode` appends `--autopilot` to the connection command.
- `Autopilot mode` uses the connection command without `--autopilot`.
- `WLAN` shows an aerial-required warning.
- `Apply Connection Type` backs up `mav_client.service`, updates `ExecStart`, runs `systemctl daemon-reload`, restarts `mav_client.service`, and runs `adb shell sync`.
- `Refresh` rereads current camera type and connection type config from the device.
- `ADB Reboot` runs `adb reboot`.

### TEST Tab

- Device status (`Online`/`Offline`) is monitored in background via `adb get-state`.
- `Dual Mode Test` updates `CAM_DIS_MODE` to `"3"` in `/data/camera/cam_param.bin`, then reboots the device.
- `SDCard Test` checks mount state (`/mnt/sdcard`) and runs write/read/remove test.
- `Reset` removes `/data/camera/cam_param.bin`, syncs, then reboots.

## Build Executable

```bash
pyinstaller --onefile --windowed main.py
```

Output is generated under `dist/`.

## Project Files

- `main.py`: Main window and tab container.
- `info.py`: Device version read UI/logic.
- `update.py`: Full update workflow and fastboot logging.
- `config.py`: Device configuration UI/logic.
- `test.py`: Factory test actions and ADB online monitor thread.

## Troubleshooting

- Device not visible in app:
  - Run `adb devices` and accept device authorization prompt.
  - Confirm USB cable/port and power.
- `Update` button stays disabled:
  - Confirm device is in bootloader mode and visible in `fastboot devices`.
- Flash failures:
  - Verify exact filenames in selected update folder.
  - Re-enter bootloader and retry.
- Linux USB permission issues:
  - Configure proper udev rules for your device vendor and reload udev.

## License

Internal factory use only.
