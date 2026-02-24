# Trimble Backup Utility

Trimble Backup Utility es una aplicación ligera de escritorio para Windows diseñada para simplificar las operaciones de copia de seguridad de las colectoras de datos Trimble y Spectra basados ​​en Android, utilizando ADB (Android Debug Bridge).

La herramienta está diseñada para entornos de servicio técnico, laboratorios de reparación e instalaciones de gestión de equipos donde se requieren flujos de trabajo fiables de extracción de datos y mantenimiento de dispositivos.

Proporciona una interfaz gráfica clara para automatizar la extracción de archivos y organizar las copias de seguridad de forma estructurada y controlada.

---

## Características

- Detección automática de dispositivos mediante ADB
- Carpetas de respaldo estructuradas y con marca de tiempo (Estructura de carpeta: modelo_serial_OT_fecha)
- Extracción organizada del almacenamiento interno
- Sistema de registro integrado
- Interfaz de usuario sencilla e intuitiva
- Ligero y portátil

---

## Vista previa de la aplicación

![Application Screenshot](docs/acercade.png)

---

## Requisitos

- Windows 10/11
- Depuración USB habilitada en el dispositivo
- Recolector Trimble o Spectra basado en Android
- Conexión USB

---

## Dispositivos compatibles

### Trimble

- TSC5  
- TSC510  
- TSC710  
- TCU5  
- TDC6  
- TDC600  
- TDC100  

### Spectra

- MobileMapper 6  
- MobileMapper 60  
- MobileMapper 5  
- Ranger 5  

---

## Instalación

1. Descarga la última versión desde la sección **Releases**.
2. Ejecuta el archivo ejecutable.
3. Activa la depuración USB en la colectora.
4. Conecta tu dispositivo por USB.
5. Inicia la copia de seguridad, ingresando datos de OT y técnico.

---

## Versionado

Este proyecto sigue el control de versiones semántico:

MAJOR.MINOR.PATCH  
Ejemplo: `v1.0.0`

---

## Limitaciones conocidas

- Solo para Windows
- Requiere activación manual de la depuración USB
- El dispositivo debe autorizar el ordenador al conectarse por primera vez

---

## Licencia

MIT No Attribution

Copyright <2026> <COPYRIGHT JAVIER SALAS>

---

## Autor

Javier Salas
