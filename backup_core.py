import os
from datetime import datetime
from config import BACKUP_ROOT
from adb import run_adb_command, get_connected_device

EXTRA_BACKUP_EXTENSIONS = [
    ".csv",
    ".dxf",
    ".dwg",
    ".ttm",
    ".job",
    ".jxl",
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
]

def scan_and_pull_extra_directories(
    device,
    backup_path,
    selected_folders,
    log_callback,
    is_cancelled
):
    log_callback("\nBuscando archivos adicionales (.csv, .dxf, .ttm)...")

    result = run_adb_command(
        ["-s", device, "shell", "ls", "-R", "/sdcard"],
        capture_output=True
    )

    if not result:
        log_callback("No se pudo escanear almacenamiento.")
        return True

    current_dir = ""
    directories_to_pull = set()

    for line in result.splitlines():
        if is_cancelled():
            return False

        line = line.strip()
        if not line:
            continue

        # Detect directory headers from ls -R
        if line.endswith(":"):
            current_dir = line[:-1]
            continue

        for ext in EXTRA_BACKUP_EXTENSIONS:
            if line.lower().endswith(ext):
                full_dir = current_dir

                # Skip if already included in selected folders
                if any(full_dir.startswith(folder) for folder in selected_folders):
                    break

                if not full_dir.startswith("/"):
                    break

                directories_to_pull.add(full_dir)
                break

    if not directories_to_pull:
        log_callback("No se encontraron directorios adicionales.")
        return True

    extras_root = os.path.join(backup_path, "Directorios extra")
    os.makedirs(extras_root, exist_ok=True)

    for remote_dir in sorted(directories_to_pull):

        if is_cancelled():
            return False

        log_callback(f"Respaldando directorio adicional: {remote_dir}")

        run_adb_command(
            ["-s", device, "pull", remote_dir, extras_root],
            log_callback=log_callback,
            is_cancelled=is_cancelled
        )

    return True

def create_backup_directory(model, serial, ot, technician, android_version):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    folder_name = f"{model}_{serial}_OT{ot}_{timestamp}"
    backup_path = os.path.join(BACKUP_ROOT, folder_name)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    os.makedirs(backup_path, exist_ok=True)

    file_path = os.path.join(backup_path, "backup_info.txt")
    with open(file_path, "w") as f:
        f.write(f"Modelo: {model}\n")
        f.write(f"Serial: {serial}\n")
        f.write(f"Android: {android_version}\n")
        f.write(f"OT: {ot}\n")
        f.write(f"Técnico: {technician}\n")
        f.write(f"Fecha: {timestamp}\n")

    return backup_path


def pull_folder(device, remote_path, local_path, log, is_cancelled):
    log(f"Respaldando {remote_path}...")

    # Use find to detect files (not directories)
    result = run_adb_command(
        ["-s", device, "shell", f"find \"{remote_path}\" -type f"],
        capture_output=True
    )

    files = [
        line.strip()
        for line in result.splitlines()
        if line.strip()
    ]

    if not files:
        log(f"Saltando {remote_path} (carpeta vacía o inexistente)")
        return True

    # Pull folder (ADB handles recursion)
    run_adb_command(
        ["-s", device, "pull", remote_path, local_path],
        log_callback=log,
        is_cancelled=is_cancelled
    )

    if is_cancelled():
        log(f"Respaldo de {remote_path} cancelado.")
        return False

    connected_device = get_connected_device()
    if connected_device != device:
        log(f"Respaldo de {remote_path} interrumpido: dispositivo desconectado.")
        return False

    return True


def run_backup(
    device,
    model,
    serial,
    ot,
    technician,
    log_callback,
    is_cancelled,
    android_version,
    selected_folders,
    deep_scan
):
    try:
        log_callback("\nComenzando Respaldo.")

        backup_path = create_backup_directory(
            model,
            serial,
            ot,
            technician,
            android_version,
        )

        log_callback(f"Directorio de respaldo creado: {backup_path}\n")

        for folder in selected_folders:

            if is_cancelled():
                log_callback("Respaldo cancelado por el usuario.")
                return False

            success = pull_folder(
                device,
                folder,
                backup_path,
                log_callback,
                is_cancelled
            )

            if not success:
                return False

            # log_callback(f"\nRespaldando: {folder}")
        # Deep scan
        if deep_scan and not is_cancelled():
            success = scan_and_pull_extra_directories(
                device,
                backup_path,
                selected_folders,
                log_callback,
                is_cancelled
            )

            if not success:
                return False

        return True

    except Exception as e:
        log_callback(f"ERROR: {str(e)}")
        return False
