import subprocess
import time
from config import ADB_PATH
import os
import sys


def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def run_adb_command(args, log_callback=None, is_cancelled=lambda: False, capture_output=False):

    if capture_output:
        result = subprocess.run(
            [ADB_PATH] + args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=os.path.dirname(ADB_PATH)
        )
        return result.stdout

    process = subprocess.Popen(
        [ADB_PATH] + args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    output_lines = []

    while True:
        if is_cancelled():
            process.terminate()
            time.sleep(0.5)
            if process.poll() is None:
                process.kill()
            return "Command cancelled."

        line = process.stdout.readline()
        if not line:
            break

        line = line.strip()
        output_lines.append(line)

        if log_callback:
            log_callback(line)

    process.wait()
    return "\n".join(output_lines)


def get_adb_version():
    try:
        result = subprocess.run(
            [resource_path("adb/adb.exe"), "version"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            first_line = result.stdout.splitlines()[0]
            return first_line.strip()
        else:
            return "No disponible"
    except Exception:
        return "No disponible"


def adb_exists():
    import os
    return os.path.exists(ADB_PATH)


def get_connected_device():
    output = run_adb_command(["devices"])
    lines = output.splitlines()

    devices = [
        line.split()[0]
        for line in lines[1:]
        if line.strip().endswith("device")
    ]

    if not devices:
        return None

    return devices[0]


def get_device_info(device):
    model = run_adb_command(
        ["-s", device, "shell", "getprop", "ro.product.model"]
    )
    serial = run_adb_command(
        ["-s", device, "shell", "getprop", "sys.qc.sn"]
    )
    android_version = run_adb_command(
        ["-s", device, "shell", "getprop", "ro.build.version.release"]
    )

    return model, serial, android_version
