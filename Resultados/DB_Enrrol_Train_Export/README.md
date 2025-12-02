# Proyecto de Reconocimiento Facial (FRT) + GUI de Personas + Export API

Este proyecto junta tres cosas:

- `GUI_DataBase/`: interfaz gráfica en Tkinter + base de datos SQLite (`personas.db`).
- `FRT/`: scripts de reconocimiento facial (LBPH) para enrolar y entrenar.
- `Export_Results_API/`: pequeño servidor FastAPI para exportar el modelo, labels y datos a otra PC en la red.

La idea general es:

1. Desde la **GUI** cargo/gestiono personas.
2. La GUI llama a los scripts de FRT para **enrolar** y **entrenar** el modelo.
3. Apartir de otra PC (servidor), usamos la **API de export** para mandarle modelo + labels + datos para el reconocimiento.

---

## 📁 Estructura del proyecto

```text
Proyecto/
├── config.py                  # Rutas centralizadas (BD, modelo, faces, etc.)
├── requirements.txt           # Dependencias de Python
├── README.md                  

├── GUI_DataBase/
│   ├── GUI_DB.py              # Tkinter GUI: agg/borrar/modificación + enrolar + entrenar
│   ├── Data_Base.py           # Funciones para manejar la BD SQLite
│   ├── personas.db            # Base de datos de personas
│   └── faces/
│       ├── 1/                 # Carpeta con ~40 fotos de la persona ID=1
│       └── 2/                 # Carpeta con ~40 fotos de la persona ID=2
│       └── ...                # etc.

├── FRT/
│   ├── enrolar_persona.py     # Captura fotos de una persona
│   ├── entrenar_modelo.py     # Entrena el modelo LBPH con las imágenes de faces/
│   └── model/
│       ├── model_lbph.yml     # Modelo LBPH entrenado
│       └── labels.json        # Mapping: label -> person_id

└── Export_Results_API/
    ├── server.py              # Servidor FastAPI que expone modelo, labels, personas y fotos
    └── README.md              # Detalle del flujo de exportación/sync
