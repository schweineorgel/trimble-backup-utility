import subprocess
import time
import sys
import os

from PyQt6.QtGui import (
    QFont, QPixmap, QIcon
)
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QLabel,
    QPlainTextEdit, QLineEdit, QMessageBox,
    QSplitter, QGraphicsOpacityEffect, QStackedLayout,
    QCheckBox, QDialog, QGroupBox
)
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal,
    QPropertyAnimation, QT_VERSION_STR)
from adb import (
    get_adb_version,
    get_connected_device,
    get_device_info
)
from config import TRIMBLE_MODELS, SPECTRA_MODELS, DEVICE_PROFILES
from backup_worker import BackupWorker

BASE_MARGIN = 12
BASE_SPACING = 10


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        adb_version = get_adb_version()

        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.CustomizeWindowHint |
            Qt.WindowType.WindowTitleHint |
            Qt.WindowType.WindowCloseButtonHint
        )

        self.setWindowTitle("Info")
        self.setWindowIcon(QIcon(resource_path("assets/info.ico")))
        self.setMinimumWidth(380)

        layout = QVBoxLayout()
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)
        self.setLayout(layout)

        app_icon = resource_path("assets/trimble-backup-utility.png")
        pyqt_icon = resource_path("assets/pyqt.png")
        adb_icon = resource_path("assets/adb.png")

        # Horizontal row: app + PyQt
        row = QHBoxLayout()

        left = QLabel(
            f"""
            <div style='text-align: center;'>
                <img src='{app_icon}' width='100'><br>
                <b>Trimble Backup Utility</b><br>
                <span style='color: #555;'>Versión 1.0.0</span>
            </div>
            """
        )
        left.setWordWrap(True)
        left.setOpenExternalLinks(True)

        right = QLabel(
            f"""
            <div style='text-align: center;'>
                <img src='{pyqt_icon}' width='100'><br>
                <b>PyQt</b><br>
                <span style='color: #555;'>Versión {QT_VERSION_STR}</span>
            </div>
            """
        )
        right.setWordWrap(True)
        right.setOpenExternalLinks(True)

        row.addWidget(left)
        row.addWidget(right)

        layout.addLayout(row)

        # Footer / credits
        footer = QLabel(
            f"""
            
            <div style='text-align: center; margin-top: 10px;'>
                <img src="{adb_icon}" height="16" width="16"> {adb_version}<br>
                Programado con Python {sys.version.split()[0]}<br>
                Creado por Javier Salas | 
                <a href = https://github.com/schweineorgel/trimble-backup-utility>GitHub</a>
            </div>
            """
        )
        footer.setWordWrap(True)
        footer.setOpenExternalLinks(True)

        layout.addWidget(footer)

        close_button = QPushButton("Cerrar")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)

        self.adjustSize()
        self.setFixedSize(self.size())


class AdbWatcher(QThread):
    device_connected = pyqtSignal(str)
    device_disconnected = pyqtSignal(str)

    def __init__(self, adb_path=None):
        super().__init__()

        if adb_path is None:
            adb_path = resource_path("adb/adb.exe")

        self.adb_path = adb_path
        self.running = True
        self.current_device = None  # track currently connected device
        self.process = None

    def run(self):
        self.process = subprocess.Popen(
            [self.adb_path, "track-devices"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        while self.running:
            line = self.process.stdout.readline()
            if not line:
                time.sleep(0.05)
                continue

            line = line.strip()
            if not line:
                continue

            if len(line) > 4:
                line = line[4:]  # Empieza con 4 numeros, eliminar para obtener serial

            # No hay dispositivos conectados
            if line == "0000":
                if self.current_device is not None:
                    self.device_disconnected.emit(self.current_device)
                    self.current_device = None
                continue

            parts = line.split()
            if len(parts) != 2:
                continue

            serial, status = parts

            # Device connected
            if status == "device" and serial != self.current_device:
                self.current_device = serial
                self.device_connected.emit(serial)

            # Device offline → treat as disconnected
            elif status == "offline" and self.current_device == serial:
                self.device_disconnected.emit(self.current_device)
                self.current_device = None

    def stop(self):
        self.running = False

        if self.process:
            self.process.terminate()
            self.process.wait()

        self.quit()
        self.wait()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.backup_active = False
        self.last_detected_device = None  # Track last device seen
        self.device_compatible = None  # Track if last device was compatible
        self.user_cancelled = False
        self.closing_after_cancel = False

        self.setWindowTitle("Trimble Backup Utility v1.0.0")
        self.setWindowIcon(QIcon(resource_path("assets/trimble-backup-utility.ico")))
        # self.resize(600, 480)
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)

        self._build_ui()

    def _build_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(BASE_MARGIN, BASE_MARGIN, BASE_MARGIN, BASE_MARGIN)
        main_layout.setSpacing(BASE_SPACING)
        central_widget.setLayout(main_layout)

        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(10)

        self.device_status_label = QLabel("Dispositivo: Desconectado")

        status_layout.addWidget(self.device_status_label)
        status_layout.addStretch()
        self.about_button = QPushButton("Acerca de")
        status_layout.addWidget(self.about_button)

        main_layout.addLayout(status_layout)

        # Inputs layout
        input_group = QGroupBox("Datos del respaldo")
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(10, 6, 10, 6)
        input_layout.setSpacing(10)

        self.ot_input = QLineEdit()
        self.ot_input.setPlaceholderText("Número OT")

        self.tech_input = QLineEdit()
        self.tech_input.setPlaceholderText("Técnico")

        input_layout.addWidget(self.ot_input)
        input_layout.addWidget(self.tech_input)

        input_group.setLayout(input_layout)
        main_layout.addWidget(input_group)

        self.ot_input.textChanged.connect(self.update_backup_button_state)
        self.tech_input.textChanged.connect(self.update_backup_button_state)

        # -------------------------
        # Device Info Box (Left)
        # -------------------------
        self.device_info_box = QPlainTextEdit()
        self.device_info_box.setReadOnly(True)

        # -------------------------
        # Log Box (Right)
        # -------------------------
        self.log_box = QPlainTextEdit()
        self.log_box.setReadOnly(True)

        # -------------------------
        # Left Container
        # -------------------------
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)

        # -------------------------
        # Image Container
        # -------------------------
        self.image_container = QWidget()
        self.image_container.setMinimumHeight(260)
        self.image_container.setStyleSheet("""
            border: 0.5px solid #dcdfe3;
            border-radius: 8px;
        """)

        image_layout = QStackedLayout(self.image_container)
        image_layout.setContentsMargins(0, 0, 0, 0)

        self.placeholder_label = QLabel()
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.placeholder_label.setPixmap(
            QPixmap(resource_path("assets/disconnected.png"))
        )

        self.device_image_label = QLabel()
        self.device_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        image_layout.addWidget(self.placeholder_label)  # index 0
        image_layout.addWidget(self.device_image_label)  # index 1

        self.image_stack = image_layout

        left_layout.addWidget(self.device_info_box)     # info
        left_layout.addWidget(self.image_container)   # image

        self.image_stack.setCurrentIndex(0)

        self.image_opacity_effect = QGraphicsOpacityEffect()
        self.device_image_label.setGraphicsEffect(self.image_opacity_effect)
        self.image_opacity_effect.setOpacity(0)

        self.image_animation = QPropertyAnimation(
            self.image_opacity_effect,
            b"opacity"
        )
        self.image_animation.setDuration(200)

        # -------------------------
        # Right Container
        # -------------------------
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)

        right_layout.addWidget(self.log_box)
        self.backup_button = QPushButton("Empezar Respaldo")
        self.cancel_button = QPushButton("Cancelar")

        self.cancel_button.setEnabled(False)

        # Check boxes
        options_group = QGroupBox("Opciones de respaldo")
        options_layout = QVBoxLayout()
        options_group.setLayout(options_layout)

        self.folder_container_layout = options_layout
        right_layout.addWidget(options_group)

        self.folder_checks = []
        self.extra_files_check = None

        button_row = QHBoxLayout()
        button_row.addWidget(self.backup_button)
        button_row.addWidget(self.cancel_button)

        right_layout.addLayout(button_row)

        # -------------------------
        # Splitter
        # -------------------------
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_container)
        splitter.addWidget(right_container)
        # splitter.setSizes([200, 550])

        left_container.setMinimumWidth(260)  # minimum width
        left_container.setMaximumWidth(260)  # maximum width

        left_layout.setContentsMargins(0, 0, 3, 0)
        left_layout.setSpacing(10)

        right_layout.setContentsMargins(3, 0, 0, 0)
        right_layout.setSpacing(10)

        main_layout.addWidget(splitter, stretch=1)

        self.current_device = None
        self.current_serial = None
        self.current_model = None

        self.backup_button.setEnabled(False)

        mono = QFont("Consolas", 12)
        self.log_box.setFont(mono)
        self.device_info_box.setFont(mono)

        # Connections
        self.backup_button.clicked.connect(self.start_backup)
        self.cancel_button.clicked.connect(self.cancel_backup)
        self.about_button.clicked.connect(self.show_about)

        self.adb_watcher = AdbWatcher()
        self.adb_watcher.device_connected.connect(self.on_device_connected)
        self.adb_watcher.device_disconnected.connect(self.on_device_disconnected)
        self.adb_watcher.start()

    def try_start_backup(self):
        if self.backup_button.isEnabled():
            self.start_backup()

    def show_about(self):
        dialog = AboutDialog(self)
        dialog.exec()

    def build_folder_options(self, device_family):
        # Clear old checkboxes
        while self.folder_container_layout.count():
            item = self.folder_container_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self.folder_checks.clear()

        profile = DEVICE_PROFILES.get(device_family)
        if not profile:
            return

        for full_path, checked in profile["folders"]:
            checkbox = QCheckBox(full_path.split("/")[-1])
            checkbox.setChecked(checked)

            # Store real device path
            checkbox.full_path = full_path

            self.folder_container_layout.addWidget(checkbox)
            self.folder_checks.append(checkbox)

        # Extra project file scan option
        self.extra_files_check = QCheckBox(
            "Buscar archivos adicionales de proyecto (.csv, .dxf, .ttm)"
        )
        self.extra_files_check.setChecked(False)

        self.folder_container_layout.addWidget(self.extra_files_check)

    # -------------------------
    # Image animation
    # -------------------------

    def fade_in_image(self):
        self.image_stack.setCurrentIndex(1)
        self.image_animation.stop()
        self.image_animation.setStartValue(0)
        self.image_animation.setEndValue(1)
        self.image_animation.start()

    # -------------------------
    # Close
    # -------------------------

    def closeEvent(self, event):

        if self.backup_active:
            event.ignore()

            confirmed = self.cancel_backup()

            if confirmed:
                self.closing_after_cancel = True
            else:
                self.closing_after_cancel = False

            return

        if hasattr(self, "adb_watcher"):
            self.adb_watcher.stop()

        event.accept()

    # -------------------------
    # Handlers
    # -------------------------

    def on_device_connected(self, serial):
        self.log(f"Dispositivo conectado: {serial}")
        self.handle_detect()  # get device info

    def on_device_disconnected(self, serial):

        self.log(f"Dispositivo desconectado: {serial}")
        self.device_status_label.setText("Dispositivo: Desconectado")
        self.device_info_box.clear()
        self.current_device = None
        self.current_model = None
        self.current_serial = None
        self.last_detected_device = None
        self.update_backup_button_state()

        self.device_image_label.clear()
        self.image_stack.setCurrentIndex(0)

        while self.folder_container_layout.count():
            item = self.folder_container_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self.folder_checks.clear()
        self.extra_files_check = None
        self.device_compatible = None

        if self.backup_active and hasattr(self, "worker") and not self.user_cancelled:
            QMessageBox.warning(
                self,
                "Dispositivo desconectado",
                "El dispositivo fue desconectado durante el respaldo."
                " El proceso se detendrá automaticamente."
            )

    def update_backup_button_state(self):
        device_ready = self.current_device is not None
        ot_ready = bool(self.ot_input.text().strip())
        tech_ready = bool(self.tech_input.text().strip())

        self.backup_button.setEnabled(device_ready and ot_ready and tech_ready)

    def cancel_backup(self):

        if not hasattr(self, "worker"):
            return False

        reply = QMessageBox.question(
            self,
            "Confirmar Cancelación",
            "¿Estás seguro que deseas cancelar el respaldo?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.worker.cancel()
            self.user_cancelled = True
            self.cancel_button.setEnabled(False)
            return True

        return False

    def handle_detect(self):

        device = get_connected_device()

        if not device:
            self.log("Ningún dispositivo detectado.")
            self.update_backup_button_state()
            return

        if device == self.last_detected_device and self.device_compatible:
            return

        model, serial, android_version = get_device_info(device)

        device_family = None

        if any(model.startswith(prefix) for prefix in TRIMBLE_MODELS):
            device_family = "trimble"
        elif any(model.startswith(prefix) for prefix in SPECTRA_MODELS):
            device_family = "spectra"

        if not device_family:
            self.log(f"Dispositivo no compatible.")

            self.current_device = None
            self.current_serial = None
            self.current_model = None
            self.backup_button.setEnabled(False)
            self.update_backup_button_state()

            self.device_status_label.setText("Dispositivo: No compatible")

            unknown_path = resource_path("assets/unknown.png")
            if os.path.exists(unknown_path):
                self.device_image_label.setPixmap(QPixmap(unknown_path))
                self.fade_in_image()
            else:
                self.device_image_label.clear()

            self.last_detected_device = device
            return

        # self.log(f"Dispositivo detectado: {device}")
        self.show_device_info(model, serial, android_version)

        self.current_device = device
        self.current_serial = serial
        self.current_model = model
        self.current_android_version = android_version

        self.device_status_label.setText(f"Dispositivo: {device}")
        self.update_backup_button_state()

        self.last_detected_device = device
        self.device_compatible = True

        self.build_folder_options(device_family)

    # -------------------------
    # Logging
    # -------------------------

    def log(self, message: str):
        self.log_box.appendPlainText(message)
        self.log_box.verticalScrollBar().setValue(
            self.log_box.verticalScrollBar().maximum()
        )

    def show_device_info(self, model, serial, android_version):
        self.device_info_box.clear()
        self.device_info_box.appendPlainText(f"Modelo: {model}")
        self.device_info_box.appendPlainText(f"Serial: {serial}")
        self.device_info_box.appendPlainText(f"Android: {android_version}")

        # Load image
        from config import MODEL_IMAGES

        image_path = MODEL_IMAGES.get(model)

        if image_path:
            self.device_image_label.setPixmap(QPixmap(resource_path(image_path)))
        else:
            self.device_image_label.clear()

        self.fade_in_image()

    def set_ui_enabled(self, enabled: bool):
        self.ot_input.setEnabled(enabled)
        self.tech_input.setEnabled(enabled)

        if enabled:
            self.update_backup_button_state()
        else:
            self.backup_button.setEnabled(False)

    def start_backup(self):
        self.backup_active = True
        self.set_ui_enabled(False)
        self.cancel_button.setEnabled(True)

        if not self.current_device:
            self.log("No hay dispositivo.")
            return

        ot = self.ot_input.text().strip()
        technician = self.tech_input.text().strip()
        android_version = self.current_android_version

        self.backup_button.setEnabled(False)
        # self.log("Respaldando...")
        selected_folders = [
            cb.full_path
            for cb in self.folder_checks
            if cb.isChecked()
        ]

        deep_scan = self.extra_files_check.isChecked() if self.extra_files_check else False

        self.thread = QThread()
        self.worker = BackupWorker(
            self.current_device,
            self.current_model,
            self.current_serial,
            ot,
            technician,
            android_version,
            selected_folders,
            deep_scan
        )

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.log_signal.connect(self.append_log)
        self.worker.finished.connect(self.on_backup_finished)

        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def append_log(self, message):
        self.log(message)

    def restore(self):
        self.backup_button.setEnabled(True)
        self.set_ui_enabled(True)
        self.cancel_button.setEnabled(False)

    def on_backup_finished(self, success):
        self.backup_active = False
        self.restore()
        self.user_cancelled = False

        if success:
            self.log("Respaldo completado exitosamente.")

        if self.closing_after_cancel:
            self.closing_after_cancel = False
            self.close()
