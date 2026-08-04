from datetime import datetime

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTextEdit,
    QRadioButton,
    QButtonGroup,
    QGroupBox,
    QDialog,
    QLabel,
    QDialogButtonBox,
    QStyle,
)
from PySide6.QtCore import QProcess, Qt
from PySide6.QtGui import QTextCursor


class ConfigTab(QWidget):
    def __init__(self):
        super().__init__()

        self.process = None
        self.camera_type_init_process = None
        self.connection_type_init_process = None
        self.reboot_process = None
        self.command_queue = []
        self.current_index = 0
        self.camera_type_options = {
            "ACSL SAMO": {
                "brand": "ACSL",
                "model": "SAMO",
                "background": "/usr/share/weston/background_logo_acsl.png",
            },
            "AERORA D64TR": {
                "brand": "AERORA",
                "model": "D64TR",
                "background": "/usr/share/weston/background_logo_aeroratech.png",
            },
        }
        self.connection_type_options = [
            "USB",
            "Ethernet",
            "WLAN",
        ]
        self.autopilot_options = [
            "Standalone mode",
            "Autopilot mode",
        ]

        self.init_ui()
        self.read_current_camera_type()
        self.read_current_connection_type()

    def init_ui(self):
        main_layout = QVBoxLayout()

        camera_type_layout = QVBoxLayout()
        camera_type_layout.setSpacing(12)
        self.camera_type_button_group = QButtonGroup(self)
        self.camera_type_radio_buttons = {}

        for index, camera_type in enumerate(self.camera_type_options.keys()):
            radio_button = QRadioButton(f"{index + 1} {camera_type}")
            radio_button.setMinimumHeight(30)
            radio_button.setStyleSheet("font-size: 15px;")
            self.camera_type_button_group.addButton(radio_button, index)
            self.camera_type_radio_buttons[camera_type] = radio_button
            camera_type_layout.addWidget(radio_button)

        self.camera_type_radio_buttons["ACSL SAMO"].setChecked(True)

        self.btn_apply_camera_type = QPushButton("Apply Camera Type")
        self.btn_apply_camera_type.setMinimumHeight(45)
        self.btn_apply_camera_type.setStyleSheet("""
            QPushButton {
                font-size: 15px;
                font-weight: bold;
            }
        """)
        self.btn_apply_camera_type.clicked.connect(self.change_camera_type)

        camera_type_group = QGroupBox("Camera Type")
        camera_type_group_layout = QVBoxLayout()
        camera_type_group_layout.addLayout(camera_type_layout)
        camera_type_group_layout.addSpacing(10)
        camera_type_group_layout.addWidget(self.btn_apply_camera_type)
        camera_type_group.setLayout(camera_type_group_layout)

        connection_type_layout = QHBoxLayout()
        connection_type_layout.setSpacing(12)
        self.connection_type_button_group = QButtonGroup(self)
        self.connection_type_radio_buttons = {}

        for index, connection_type in enumerate(self.connection_type_options):
            radio_button = QRadioButton(connection_type)
            radio_button.setMinimumHeight(30)
            radio_button.setStyleSheet("font-size: 15px;")
            self.connection_type_button_group.addButton(radio_button, index)
            self.connection_type_radio_buttons[connection_type] = radio_button
            connection_type_layout.addWidget(radio_button)

        self.connection_type_radio_buttons["USB"].setChecked(True)

        autopilot_layout = QHBoxLayout()
        autopilot_layout.setSpacing(12)
        self.autopilot_button_group = QButtonGroup(self)
        self.autopilot_radio_buttons = {}

        for index, option_name in enumerate(self.autopilot_options):
            radio_button = QRadioButton(option_name)
            radio_button.setMinimumHeight(30)
            radio_button.setStyleSheet("font-size: 15px;")
            self.autopilot_button_group.addButton(radio_button, index)
            self.autopilot_radio_buttons[option_name] = radio_button
            autopilot_layout.addWidget(radio_button)

        self.autopilot_radio_buttons["Standalone mode"].setChecked(True)

        self.btn_apply_connection_type = QPushButton("Apply Connection Type")
        self.btn_apply_connection_type.setMinimumHeight(45)
        self.btn_apply_connection_type.setStyleSheet("""
            QPushButton {
                font-size: 15px;
                font-weight: bold;
            }
        """)
        self.btn_apply_connection_type.clicked.connect(self.change_connection_type)

        connection_type_group = QGroupBox("Connection Type")
        connection_type_group_layout = QVBoxLayout()
        connection_type_group_layout.addLayout(connection_type_layout)
        connection_type_group.setLayout(connection_type_group_layout)

        autopilot_group = QGroupBox("Autopilot")
        autopilot_group_layout = QVBoxLayout()
        autopilot_group_layout.addLayout(autopilot_layout)
        autopilot_group.setLayout(autopilot_group_layout)

        connection_settings_layout = QHBoxLayout()
        connection_settings_layout.setSpacing(10)
        connection_settings_layout.addWidget(connection_type_group)
        connection_settings_layout.addWidget(autopilot_group)

        connection_settings_group = QGroupBox("Connection Settings")
        connection_settings_group_layout = QVBoxLayout()
        connection_settings_group_layout.addLayout(connection_settings_layout)
        connection_settings_group_layout.addSpacing(10)
        connection_settings_group_layout.addWidget(self.btn_apply_connection_type)
        connection_settings_group.setLayout(connection_settings_group_layout)

        self.btn_refresh = QPushButton("Refresh")
        self.btn_refresh.setMinimumHeight(45)
        self.btn_refresh.setStyleSheet("""
            QPushButton {
                font-size: 15px;
                font-weight: bold;
            }
        """)
        self.btn_refresh.clicked.connect(self.refresh_current_config)

        self.btn_reboot = QPushButton("ADB Reboot")
        self.btn_reboot.setMinimumHeight(45)
        self.btn_reboot.setStyleSheet("""
            QPushButton {
                font-size: 15px;
                font-weight: bold;
            }
        """)
        self.btn_reboot.clicked.connect(self.reboot_device)

        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(10)
        bottom_layout.addWidget(self.btn_refresh)
        bottom_layout.addWidget(self.btn_reboot)

        self.config_text_edit = QTextEdit()
        self.config_text_edit.setReadOnly(True)
        self.config_text_edit.setStyleSheet("""
            QTextEdit {
                font-size: 14px;
                font-family: Consolas;
            }
        """)

        main_layout.addWidget(camera_type_group)
        main_layout.addSpacing(10)
        main_layout.addWidget(connection_settings_group)
        main_layout.addSpacing(10)
        main_layout.addWidget(self.config_text_edit)
        main_layout.addSpacing(10)
        main_layout.addLayout(bottom_layout)

        self.setLayout(main_layout)

    def refresh_current_config(self):
        self.config_text_edit.clear()
        self.read_current_camera_type()
        self.read_current_connection_type()

    def read_current_camera_type(self):
        self.append_config_log("Reading current camera type config...")
        self.camera_type_init_process = QProcess(self)
        self.camera_type_init_process.readyReadStandardOutput.connect(
            self.handle_camera_type_init_stdout
        )
        self.camera_type_init_process.readyReadStandardError.connect(
            self.handle_camera_type_init_stderr
        )
        self.camera_type_init_process.finished.connect(
            self.on_read_current_camera_type_finished
        )
        self.camera_type_init_process.start(
            "adb",
            [
                "shell",
                "sed -n 's|^Environment=CAM_BRAND=||p;s|^Environment=CAM_MODEL=||p' /etc/systemd/system/mav_client.service",
            ],
        )

    def handle_camera_type_init_stdout(self):
        data = self.camera_type_init_process.readAllStandardOutput()
        text = bytes(data).decode("utf-8", errors="ignore").strip()
        if not text:
            return

        values = [line.strip() for line in text.splitlines() if line.strip()]
        if len(values) < 2:
            self.append_config_log(
                f"Current camera type config: {text}",
                show_time=False,
            )
            return

        brand = values[0]
        model = values[1]
        for camera_type, config in self.camera_type_options.items():
            if brand == config["brand"] and model == config["model"]:
                self.camera_type_radio_buttons[camera_type].setChecked(True)
                self.append_config_log(
                    f"Current camera type: {camera_type}",
                    show_time=False,
                )
                return

        self.append_config_log(
            f"Current camera type: {brand} {model}",
            show_time=False,
        )

    def handle_camera_type_init_stderr(self):
        data = self.camera_type_init_process.readAllStandardError()
        text = bytes(data).decode("utf-8", errors="ignore").strip()
        if text:
            self.append_config_log(text, show_time=False)

    def on_read_current_camera_type_finished(self, exitCode, exitStatus):
        if exitCode != 0:
            self.append_config_log("Unable to read current camera type config.")

    def read_current_connection_type(self):
        self.append_config_log("Reading current connection type config...")
        self.connection_type_init_process = QProcess(self)
        self.connection_type_init_process.readyReadStandardOutput.connect(
            self.handle_connection_type_init_stdout
        )
        self.connection_type_init_process.readyReadStandardError.connect(
            self.handle_connection_type_init_stderr
        )
        self.connection_type_init_process.finished.connect(
            self.on_read_current_connection_type_finished
        )
        self.connection_type_init_process.start(
            "adb",
            [
                "shell",
                "sed -n 's|^ExecStart=||p' /etc/systemd/system/mav_client.service",
            ],
        )

    def handle_connection_type_init_stdout(self):
        data = self.connection_type_init_process.readAllStandardOutput()
        text = bytes(data).decode("utf-8", errors="ignore").strip()
        if not text:
            return

        exec_start = text.splitlines()[0].strip()
        has_autopilot = "--autopilot" in exec_start

        if "--connection_type ethernet" in exec_start:
            connection_type = "ethernet"
        elif "--connection_type wlan" in exec_start:
            connection_type = "wlan"
        else:
            connection_type = "usb"

        for option_name, radio_button in self.connection_type_radio_buttons.items():
            if option_name.lower() == connection_type:
                radio_button.setChecked(True)
                self.append_config_log(
                    f"Current connection type: {option_name}",
                    show_time=False,
                )
                break
        else:
            self.append_config_log(
                f"Current connection type: {connection_type}",
                show_time=False,
            )

        if has_autopilot:
            self.autopilot_radio_buttons["Autopilot mode"].setChecked(True)
            self.append_config_log("Current autopilot mode: Autopilot mode", show_time=False)
        else:
            self.autopilot_radio_buttons["Standalone mode"].setChecked(True)
            self.append_config_log("Current autopilot mode: Standalone mode", show_time=False)


    def handle_connection_type_init_stderr(self):
        data = self.connection_type_init_process.readAllStandardError()
        text = bytes(data).decode("utf-8", errors="ignore").strip()
        if text:
            self.append_config_log(text, show_time=False)

    def on_read_current_connection_type_finished(self, exitCode, exitStatus):
        if exitCode != 0:
            self.append_config_log("Unable to read current connection type config.")

    def change_camera_type(self):
        camera_type = self.selected_camera_type()
        camera_config = self.camera_type_options[camera_type]

        brand_config_cmd = (
            "sed -i 's|^Environment=CAM_BRAND=.*|"
            f"Environment=CAM_BRAND={camera_config['brand']}|"
            "' /etc/systemd/system/mav_client.service"
        )
        model_config_cmd = (
            "sed -i 's|^Environment=CAM_MODEL=.*|"
            f"Environment=CAM_MODEL={camera_config['model']}|"
            "' /etc/systemd/system/mav_client.service"
        )
        weston_config_cmd = (
            "sed -i 's|^background-image=.*|"
            f"background-image={camera_config['background']}|"
            "' /etc/xdg/weston/weston.ini"
        )
        self.command_queue = [
            {
                "title": "Updating camera brand config...",
                "cmd": ["adb", "shell", brand_config_cmd],
            },
            {
                "title": "Updating camera model config...",
                "cmd": ["adb", "shell", model_config_cmd],
            },
            {
                "title": "Updating weston background image config...",
                "cmd": ["adb", "shell", weston_config_cmd],
            },
            {
                "title": "Syncing file system...",
                "cmd": ["adb", "shell", "sync"],
            },
        ]
        self.current_index = 0
        self.set_apply_buttons_enabled(False)
        self.run_next_command(
            "Camera type config update complete. Please reboot device.",
        )

    def change_connection_type(self):
        connection_type = self.selected_connection_type()
        if connection_type == "WLAN":
            self.show_wlan_aerial_alert()

        exec_start = self.connection_type_exec_start(connection_type)
        service_config_cmd = (
            "cp /etc/systemd/system/mav_client.service "
            "/etc/systemd/system/mav_client.service.bak && "
            "sed -i 's|^ExecStart=.*|"
            f"ExecStart={exec_start}|"
            "' /etc/systemd/system/mav_client.service && "
            "systemctl daemon-reload && "
            "systemctl restart mav_client.service"
        )
        self.command_queue = [
            {
                "title": "Updating connection type config...",
                "cmd": ["adb", "shell", service_config_cmd],
            },
            {
                "title": "Syncing file system...",
                "cmd": ["adb", "shell", "sync"],
            },
        ]
        self.current_index = 0
        self.set_apply_buttons_enabled(False)
        self.run_next_command(
            "Connection type config update complete.",
        )

    def connection_type_exec_start(self, connection_type):
        autopilot_arg = " --autopilot" if self.is_autopilot_enabled() else ""

        if connection_type == "Ethernet":
            return (
                "/usr/bin/mav_client -u udp://192.168.144.100:14550 "
                f"--connection_type ethernet{autopilot_arg}"
            )

        if connection_type == "WLAN":
            return (
                "/usr/bin/mav_client -u udp://192.168.251.2:14550 "
                f"--connection_type wlan{autopilot_arg}"
            )

        return (
            "/usr/bin/mav_client -l -u udp://127.0.0.1:14570"
            f"{autopilot_arg}"
        )

    def show_wlan_aerial_alert(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("WLAN Aerial Required")
        dialog.setModal(True)
        dialog.setWindowFlags(
            Qt.Dialog
            | Qt.CustomizeWindowHint
            | Qt.WindowTitleHint
            | Qt.WindowCloseButtonHint
        )
        dialog.setFixedSize(420, 170)

        icon_label = QLabel()
        icon = self.style().standardIcon(QStyle.SP_MessageBoxWarning)
        icon_label.setPixmap(icon.pixmap(64, 64))
        icon_label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        text_label = QLabel(
            "WLAN connection requires an aerial.\n\n"
            "Please install the aerial before using WLAN."
        )
        text_label.setWordWrap(True)
        text_label.setMinimumWidth(290)
        text_label.setStyleSheet("font-size: 15px;")

        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)
        content_layout.addWidget(icon_label)
        content_layout.addWidget(text_label, 1)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(dialog.accept)

        dialog_layout = QVBoxLayout()
        dialog_layout.setContentsMargins(18, 18, 18, 14)
        dialog_layout.addLayout(content_layout)
        dialog_layout.addStretch()
        dialog_layout.addWidget(button_box)
        dialog.setLayout(dialog_layout)

        dialog.adjustSize()
        if self.window():
            parent_geometry = self.window().frameGeometry()
            dialog_geometry = dialog.frameGeometry()
            dialog_geometry.moveCenter(parent_geometry.center())
            dialog.move(dialog_geometry.topLeft())

        dialog.exec()

    def set_apply_buttons_enabled(self, enabled):
        self.btn_apply_camera_type.setEnabled(enabled)
        self.btn_apply_connection_type.setEnabled(enabled)

    def selected_camera_type(self):
        for camera_type, radio_button in self.camera_type_radio_buttons.items():
            if radio_button.isChecked():
                return camera_type

        return "ACSL SAMO"

    def selected_connection_type(self):
        for connection_type, radio_button in self.connection_type_radio_buttons.items():
            if radio_button.isChecked():
                return connection_type

        return "USB"

    def is_autopilot_enabled(self):
        return self.autopilot_radio_buttons["Autopilot mode"].isChecked()

    def run_next_command(self, success_message):
        if self.current_index >= len(self.command_queue):
            self.append_config_log(success_message)
            self.set_apply_buttons_enabled(True)
            return

        item = self.command_queue[self.current_index]
        self.current_index += 1

        self.append_config_log(item["title"])
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(
            lambda exitCode, exitStatus: self.on_command_finished(
                exitCode,
                exitStatus,
                success_message,
            )
        )
        self.process.start(item["cmd"][0], item["cmd"][1:])

    def on_command_finished(self, exitCode, exitStatus, success_message):
        if exitCode != 0:
            self.append_config_log("ERROR: Command failed.")
            self.command_queue = []
            self.set_apply_buttons_enabled(True)
            return

        self.run_next_command(success_message)

    def handle_stdout(self):
        data = self.process.readAllStandardOutput()
        text = bytes(data).decode("utf-8", errors="ignore").strip()
        if text:
            self.append_config_log(text, show_time=False)

    def handle_stderr(self):
        data = self.process.readAllStandardError()
        text = bytes(data).decode("utf-8", errors="ignore").strip()
        if text:
            self.append_config_log(text, show_time=False)

    def reboot_device(self):
        self.append_config_log("Rebooting device...")
        self.btn_reboot.setEnabled(False)
        self.reboot_process = QProcess(self)
        self.reboot_process.readyReadStandardOutput.connect(
            self.handle_reboot_stdout
        )
        self.reboot_process.readyReadStandardError.connect(
            self.handle_reboot_stderr
        )
        self.reboot_process.finished.connect(
            self.on_reboot_finished
        )
        self.reboot_process.start("adb", ["reboot"])

    def handle_reboot_stdout(self):
        data = self.reboot_process.readAllStandardOutput()
        text = bytes(data).decode("utf-8", errors="ignore").strip()
        if text:
            self.append_config_log(text, show_time=False)

    def handle_reboot_stderr(self):
        data = self.reboot_process.readAllStandardError()
        text = bytes(data).decode("utf-8", errors="ignore").strip()
        if text:
            self.append_config_log(text, show_time=False)

    def on_reboot_finished(self, exitCode, exitStatus):
        if exitCode == 0:
            self.append_config_log("Device rebooting ...")
        else:
            self.append_config_log("Device reboot FAILED.")

        self.btn_reboot.setEnabled(True)

    def append_config_log(self, text, show_time=True):
        if show_time:
            timestamp = datetime.now().strftime("%H:%M:%S")
            final_text = f"[{timestamp}] {text}"
        else:
            final_text = text

        self.config_text_edit.append(final_text)

        cursor = self.config_text_edit.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.config_text_edit.setTextCursor(cursor)
