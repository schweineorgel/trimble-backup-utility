import os
from datetime import datetime
from config import BACKUP_ROOT
from adb import run_adb_command, get_connected_device


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
        # Deep CSV scan
        if deep_scan and not is_cancelled():
            log_callback("\nBuscando archivos .csv adicionales...")

            result = run_adb_command(
                ["-s", device, "shell", "ls", "-R", "/sdcard"],
                capture_output=True
            )

            # log_callback("DEBUG RAW FIND OUTPUT:")
            # log_callback(repr(result))

            current_dir = ""
            csv_files = []

            if result:
                for line in result.splitlines():
                    line = line.strip()

                    if not line:
                        continue

                    if line.endswith(":"):
                        current_dir = line[:-1]
                        continue

                    if line.lower().endswith(".csv"):
                        full_path = f"{current_dir}/{line}"
                        csv_files.append(full_path)
            # log_callback(f"CSV encontrados: {len(csv_files)}")
            csv_to_backup = []

            for csv_file in csv_files:
                if any(csv_file.startswith(folder) for folder in selected_folders):
                    continue
                if not csv_file.startswith("/"):
                    continue
                csv_to_backup.append(csv_file)

            if not csv_to_backup:
                log_callback("No se encontraron archivos .csv adicionales")
            else:
                csv_folder = os.path.join(backup_path, "csv")
                os.makedirs(csv_folder, exist_ok=True)

                for csv_file in csv_to_backup:

                    if is_cancelled():
                        return False

                    log_callback(f"Respaldando .csv: {csv_file}")

                    run_adb_command(
                        ["-s", device, "pull", csv_file, csv_folder],
                        log_callback=log_callback,
                        is_cancelled=is_cancelled
                    )

        return True

    except Exception as e:
        log_callback(f"ERROR: {str(e)}")
        return False
