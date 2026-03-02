# Factory Test Tool

A simple Qt-based desktop tool for testing and updating SAMO (qrb5165-rb5) devices.  
It talks to the device over ADB / fastboot and provides three basic functions:
- Show device version info
- Update bootloader / kernel / file system
- Run factory tests (dual mode, SD card, reset)

## Usage

```bash
# Go to project folder
cd factory_tool

# (Optional) create and activate venv
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start GUI
python main.py
```

You need:
- ADB and fastboot installed and in your `PATH`
- Device connected by USB and visible in `adb devices`

## License

Internal / factory use only. Do not redistribute without permission.
