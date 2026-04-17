from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTextEdit,
    QLabel,
    QLineEdit,
    QSizePolicy
)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QColor, QDesktopServices, QTextCharFormat, QTextCursor
from PySide6.QtCore import QProcess
from datetime import datetime
import csv
import os
import re
import sys
import uuid


HARDWARE_ID_NAMESPACE = uuid.UUID("9f8f16f3-5d1c-4d1a-bf7b-0fac70000001")


def get_app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


DEVICE_INFO_CSV = os.path.join(get_app_dir(), "device_info.csv")


def normalize_mac_address(mac):
    return mac.strip().lower()


def calc_hardware_id(mac):
    return uuid.uuid5(HARDWARE_ID_NAMESPACE, normalize_mac_address(mac))


class InfoTab(QWidget):
    def __init__(self):
        super().__init__()

        self.process = None
        self.command_queue = []
        self.current_index = 0
        self.current_command = None
        self.command_output = ""
        self.command_error = ""

        self.init_ui()

    # ================= UI =================
    def init_ui(self):
        main_layout = QVBoxLayout()

        # ===== Top layout (title + buttons) =====
        top_layout = QHBoxLayout()

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.btn_info = QPushButton("Info")
        self.btn_info.setMinimumHeight(32)
        self.btn_info.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.btn_info.clicked.connect(self.show_info)

        button_layout.addWidget(self.btn_info)

        top_layout.addLayout(button_layout)

        # ===== SN input =====
        sn_layout = QHBoxLayout()
        sn_layout.setSpacing(10)

        label_width = 90

        sn_label = QLabel("Device SN:")
        sn_label.setFixedWidth(label_width)
        sn_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.sn_line_edit = QLineEdit()
        self.sn_line_edit.setMinimumHeight(32)
        self.sn_line_edit.setPlaceholderText("Enter device serial number")

        sn_layout.addWidget(sn_label)
        sn_layout.addWidget(self.sn_line_edit)

        # ===== Hardware ID display =====
        hardware_id_layout = QHBoxLayout()
        hardware_id_layout.setSpacing(10)

        hardware_id_label = QLabel("Hardware ID:")
        hardware_id_label.setFixedWidth(label_width)
        hardware_id_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.hardware_id_line_edit = QLineEdit()
        self.hardware_id_line_edit.setMinimumHeight(32)
        self.hardware_id_line_edit.setReadOnly(True)

        hardware_id_layout.addWidget(hardware_id_label)
        hardware_id_layout.addWidget(self.hardware_id_line_edit)

        store_layout = QHBoxLayout()
        self.btn_store = QPushButton("Store")
        self.btn_store.setMinimumHeight(32)
        self.btn_store.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_store.clicked.connect(self.store_current_device_info)
        store_layout.addWidget(self.btn_store)

        # ===== Text Output =====
        self.info_text_edit = QTextEdit()
        self.info_text_edit.setStyleSheet("""
            QTextEdit {
                font-size: 14px;
                font-family: Consolas;
            }
        """)
        self.info_text_edit.setReadOnly(True)

        bottom_layout = QHBoxLayout()
        self.btn_open = QPushButton("Open")
        self.btn_open.clicked.connect(self.open_csv_store_path)
        self.btn_clear = QPushButton("Clear")
        self.btn_clear.clicked.connect(self.clear_info_log)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.btn_open)
        bottom_layout.addWidget(self.btn_clear)

        main_layout.addLayout(top_layout)
        main_layout.addLayout(sn_layout)
        main_layout.addLayout(hardware_id_layout)
        main_layout.addLayout(store_layout)
        main_layout.addWidget(self.info_text_edit)
        main_layout.addLayout(bottom_layout)

        self.setLayout(main_layout)

     # =========================
    # function
    # =========================
    def append_info_text(self, text, show_time=True):
        if show_time:
            timestamp = datetime.now().strftime("%H:%M:%S")
            final_text = f"[{timestamp}] {text}"
        else:
            final_text = text

        self.append_colored_text(final_text)

    def append_warning_text(self, text):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.append_colored_text(f"[{timestamp}] WARNING: {text}", "red")

    def append_colored_text(self, text, color="black"):
        cursor = self.info_text_edit.textCursor()
        cursor.movePosition(QTextCursor.End)

        if not self.info_text_edit.document().isEmpty():
            cursor.insertBlock()

        char_format = QTextCharFormat()
        char_format.setForeground(QColor(color))
        cursor.insertText(text, char_format)

        # auto scroll to the bottom
        cursor.movePosition(QTextCursor.End)
        self.info_text_edit.setTextCursor(cursor)

    def clear_info_log(self):
        """clear the text edit"""
        self.info_text_edit.clear()

    def open_csv_store_path(self):
        path = DEVICE_INFO_CSV if os.path.exists(DEVICE_INFO_CSV) else get_app_dir()
        opened = QDesktopServices.openUrl(QUrl.fromLocalFile(path))
        if not opened:
            self.append_warning_text(f"Could not open path: {path}")

    def show_info(self):
        self.hardware_id_line_edit.clear()

        mac_cmd = (
            "mac=$(cat /sys/class/net/eth0/address 2>/dev/null | tr -d '\\r\\n '); "
            "if [ -n \"$mac\" ] && [ \"$mac\" != \"00:00:00:00:00:00\" ]; then "
            "echo \"eth0 $mac\"; "
            "else "
            "exit 1; "
            "fi"
        )
        self.commands = [
            {
                "title": "Camera Version:",
                "cmd": ["adb", "shell", "cat", "/etc/aerora-version"],
                "type": "text"
            },
            {
                "title": "Gimbal Version:",
                "cmd": ["adb", "shell", "cat", "/etc/gimbal-version"],
                "type": "text"
            },
            {
                "title": "Hardware ID:",
                "cmd": ["adb", "shell", mac_cmd],
                "type": "hardware_id"
            }
        ]

        self.start_command_queue()

    def start_command_queue(self):
        self.current_index = 0
        self.current_command = None
        self.command_output = ""
        self.command_error = ""
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.handle_command_finished)
        self.run_next_command()

    def run_next_command(self):
        if self.current_index < len(self.commands):
            item = self.commands[self.current_index]
            self.current_index += 1
            self.current_command = item
            self.command_output = ""
            self.command_error = ""

            self.append_info_text(item["title"], show_time=True)
            # execute the command
            cmd = item["cmd"]
            self.process.start(cmd[0], cmd[1:])
        else:
            self.append_info_text("Done.")

    def handle_stdout(self):
        data = self.process.readAllStandardOutput()
        self.command_output += bytes(data).decode("utf-8", errors="ignore")

    def handle_stderr(self):
        data = self.process.readAllStandardError()
        self.command_error += bytes(data).decode("utf-8", errors="ignore")

    def handle_command_finished(self):
        if self.current_command:
            command_type = self.current_command.get("type")
            if command_type == "hardware_id":
                self.print_hardware_id()
            else:
                self.print_text_command_output()

        self.run_next_command()

    def print_text_command_output(self):
        output = self.command_output.strip()
        error = self.command_error.strip()

        if output:
            self.append_info_text(output, show_time=False)
            self.append_info_text("--------------------------------", show_time=False)
        if error:
            self.append_info_text(f"ERROR: {error}")

    def print_hardware_id(self):
        output = self.command_output.strip()
        error = self.command_error.strip()

        if error:
            self.append_info_text(f"ERROR: {error}")

        match = re.search(
            r"(?P<iface>\S+)\s+(?P<mac>[0-9a-fA-F]{2}(?::[0-9a-fA-F]{2}){5})",
            output
        )
        if not match:
            self.append_info_text("ERROR: Could not read device MAC address.")
            return

        iface = match.group("iface")
        mac = normalize_mac_address(match.group("mac"))
        hardware_id = calc_hardware_id(mac)
        self.hardware_id_line_edit.setText(str(hardware_id))
        device_sn = self.find_device_sn_by_hardware_id(hardware_id)
        saved_message = "SN loaded from CSV."

        if device_sn:
            self.sn_line_edit.setText(device_sn)
        else:
            self.append_info_text(f"MAC Address ({iface}): {mac}", show_time=False)
            self.append_info_text(f"Hardware ID: {hardware_id}", show_time=False)
            self.append_warning_text(
                "Device SN does not exist in CSV. Please enter device SN and click Store."
            )
            self.append_info_text("--------------------------------", show_time=False)
            return

        self.append_info_text(f"Device SN: {device_sn}", show_time=False)
        self.append_info_text(f"MAC Address ({iface}): {mac}", show_time=False)
        self.append_info_text(f"Hardware ID: {hardware_id}", show_time=False)
        self.append_info_text(saved_message, show_time=False)
        self.append_info_text("--------------------------------", show_time=False)

    def get_device_sn(self):
        return self.sn_line_edit.text().strip()

    def get_hardware_id(self):
        return self.hardware_id_line_edit.text().strip()

    def store_current_device_info(self):
        device_sn = self.get_device_sn()
        hardware_id = self.get_hardware_id()

        if not device_sn:
            self.append_warning_text("Please enter device SN before storing.")
            return

        if not hardware_id:
            self.append_warning_text("Please click Info to read Hardware ID before storing.")
            return

        updated = self.save_device_info(device_sn, hardware_id)
        action = "Updated" if updated else "Stored"

        self.append_info_text(f"Device SN: {device_sn}")
        self.append_info_text(f"Hardware ID: {hardware_id}", show_time=False)
        self.append_info_text(f"{action} to: {DEVICE_INFO_CSV}", show_time=False)
        self.append_info_text("--------------------------------", show_time=False)

    def save_device_info(self, device_sn, hardware_id):
        rows = []
        updated = False

        if os.path.exists(DEVICE_INFO_CSV) and os.path.getsize(DEVICE_INFO_CSV) > 0:
            with open(DEVICE_INFO_CSV, newline="", encoding="utf-8") as csv_file:
                reader = csv.DictReader(csv_file)
                for row in reader:
                    if row.get("hardware_id") == str(hardware_id):
                        row["device_sn"] = device_sn
                        row["hardware_id"] = str(hardware_id)
                        updated = True
                    rows.append({
                        "device_sn": row.get("device_sn", ""),
                        "hardware_id": row.get("hardware_id", "")
                    })

        if not updated:
            rows.append({
                "device_sn": device_sn,
                "hardware_id": str(hardware_id)
            })

        with open(DEVICE_INFO_CSV, "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=["device_sn", "hardware_id"])
            writer.writeheader()
            writer.writerows(rows)

        return updated

    def find_device_sn_by_hardware_id(self, hardware_id):
        if not os.path.exists(DEVICE_INFO_CSV):
            return None

        with open(DEVICE_INFO_CSV, newline="", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                if row.get("hardware_id") == str(hardware_id):
                    return row.get("device_sn", "").strip() or None

        return None
