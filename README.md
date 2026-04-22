[![Windows](https://badgen.net/badge/icon/windows?icon=windows&label)](https://microsoft.com/windows/)
![Status](https://img.shields.io/badge/status-stable-green)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

# Descargar
[![Descargar última versión](https://img.shields.io/badge/Descargar-Última%20versión-blue?style=for-the-badge&logo=github)](https://github.com/schweineorgel/trimble-backup-utility/releases/latest)

## Requisitos

- Windows 10/11
- Depuración USB habilitada en el dispositivo
- Colectora Trimble o Spectra basada en Android
- Conexión USB

---

# Trimble Backup Utility

`Nota: Desarrollado para soporte técnico interno en entornos de gestión de equipos geoespaciales.`

Trimble Backup Utility es una aplicación ligera de escritorio para Windows diseñada para simplificar las operaciones de copia de seguridad de las colectoras de datos Trimble y Spectra basadas ​​en Android, utilizando ADB (Android Debug Bridge).

La herramienta está diseñada para entornos de servicio técnico, laboratorios de reparación e instalaciones de gestión de equipos donde se requieren flujos de trabajo fiables de extracción de datos y mantenimiento de dispositivos.

Proporciona una interfaz gráfica clara para automatizar la extracción de archivos y organizar las copias de seguridad de forma estructurada y controlada.

## Características

- Detección automática y dinámica de extensiones de archivo para respaldo
- Soporte para archivos geoespaciales y de proyecto (DXF, DWG, JXL, T02, etc.)
- Copia estructurada con preservación de rutas
- Compatible con colectoras basadas en Android de Trimble Inc. y Spectra Precision
- Flujo de trabajo optimizado para entornos de servicio técnico

---

## Vista previa de la aplicación

<p align="center">
  <img src="docs/poc.png" alt="Application Screenshot" width="60%"/>
</p>

### Búsqueda adicional de archivos de proyecto

La opción de búsqueda adicional de archivos de proyecto permite localizar archivos de forma dinámica mediante filtrado por sufijo (extensión). El sistema escanea el almacenamiento del dispositivo y respalda automáticamente los archivos que coincidan con las siguientes extensiones:

#### Extensiones de archivos respaldados
```
.csv   .dxf   .dwg   .ttm   .job   .jxl
.t02   .t04   .dat   .rnx   .obs   .nav
.shp   .dbf   .prj   .kml   .kmz   .txt
.asc   .xml
```

---

## Dispositivos compatibles

### Trimble

| Dispositivo | Probado | Notas |
|-------------|---------|-------|
| TSC5        | Sí      |  |
| TSC510      | Sí |  |
| TSC710      | No      |  |
| TCU5        | No      |  |
| TDC6        | Sí |  |
| TDC600      | Sí      | Android 8: no se puede obtener el S/N físico vía ADB en algunos firmwares, por lo que puede requerir ingreso manual del serial en la herramienta. |
| TDC100      | No      |  |

### Spectra

| Dispositivo     | Probado |
|-----------------|---------|
| MobileMapper 6  | No      |
| MobileMapper 60 | No      |
| MobileMapper 5  | No      |
| Ranger 5        | No      |

---

## Versionado

Este proyecto sigue el control de versiones semántico:

MAJOR.MINOR.PATCH  
Ejemplo: `v1.0.0`

---

## Licencia

Este proyecto está licenciado bajo la Licencia MIT.  
Consulta el archivo [LICENSE](LICENSE) para más detalles.

---

## Autor

Javier Salas Bocaz
