import os
import sys


def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

APP_VER = '1.1.1'
VERSION_URL = "https://raw.githubusercontent.com/schweineorgel/trimble-backup-utility/refs/heads/main/meta/version.json"


# Full dir
BLOCKED_DIRECTORIES = [
    "/sdcard/Android",
    "/sdcard/DCIM/.thumbnails",
    "/sdcard/LOST.DIR"
]

ADB_PATH = resource_path("adb/adb.exe")
BACKUP_ROOT = "backups"

TRIMBLE_MODELS = [
    # Trimble
    "TSC5", "TSC510", "TSC710",
    "TCU5", "TDC6", "TDC600",
    "TDC100"
]

SPECTRA_MODELS = [
    # Spectra
    "MobileMapper6", "MobileMapper60",
    "MobileMapper50", "Ranger5"
]

MODEL_IMAGES = {
    # Trimble
    "TSC5": "assets/tsc5.png",
    "TSC510": "assets/tsc510.png",
    "TSC710": "assets/tsc710.png",
    "TCU5": "assets/tcu5.png",
    "TDC6": "assets/tdc6.png",
    "TDC600": "assets/tdc600.png",
    "TDC100": "assets/tdc100.png",
    # Spectra
    "MobileMapper6": "assets/mobilemapper6.png",
    "MobileMapper60": "assets/mobilemapper60.png",
    "MobileMapper50": "assets/mobilemapper50.png",
    "Ranger5": "assets/ranger5.png",
}

DEVICE_PROFILES = {
    "trimble": {
        "folders": [
            ("/sdcard/Trimble Data", True),
            ("/sdcard/Documents", False),
            ("/sdcard/Download", False),
            ("/sdcard/Pictures/Screenshots", False),
        ]
    },
    "spectra": {
        "folders": [
            ("/sdcard/Documents", True),
            ("/sdcard/Download", True),
            ("/sdcard/Pictures/Screenshots", False),
        ]
    }
}

EXTRA_BACKUP_EXTENSIONS = [
    ".csv",
    ".dxf",
    ".dwg",
    ".ttm",
    ".job",
    ".t01",
    ".t02",
    ".t04",
    ".dat",
    ".rnx",
    ".obs",
    ".nav",
    ".shp",
    ".dbf",
    ".prj",
    ".kml",
    ".kmz",
    ".txt",
    ".asc",
    ".xml",
    ".log",
    ".rw5",
    ".shx",
    ".jps",
    ".g3",
    ".raw",
    ".dc",
    ".bin",
    ".rtcm",
    ".crd"

]