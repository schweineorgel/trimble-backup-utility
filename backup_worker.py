from PyQt6.QtCore import QObject, pyqtSignal
from backup_core import run_backup
from adb import run_adb_command


class BackupWorker(QObject):
    finished = pyqtSignal(bool)
    log_signal = pyqtSignal(str)

    def __init__(self, device, model, serial, ot, technician, android_version, selected_folders, deep_scan):
        super().__init__()
        self._is_cancelled = False
        self.device = device
        self.model = model
        self.serial = serial
        self.ot = ot
        self.technician = technician
        self.android_version = android_version
        self.selected_folders = selected_folders
        self.deep_scan = deep_scan

    def cancel(self):
        if not self._is_cancelled:
            self._is_cancelled = True
            self.log_signal.emit("Cancelando respaldo...")
            run_adb_command(["disconnect", self.device])  # Break ADB transfers

    def is_cancelled(self):
        return self._is_cancelled

    def run(self):
        try:
            success = run_backup(
                self.device,  # adb
                self.model,  # folder
                self.serial,
                self.ot,
                self.technician,
                self.log_signal.emit,
                lambda: self._is_cancelled,
                self.android_version,
                self.selected_folders,
                self.deep_scan
            )
            self.finished.emit(success)
        except Exception as e:
            self.log_signal.emit(f"CRITICAL ERROR: {e}")
            self.finished.emit(False)