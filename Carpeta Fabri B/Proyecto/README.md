# Proyecto FRT + GUI_DataBase

Este repositorio contiene dos partes principales que ya están funcionando localmente:

- `GUI_DataBase/`: interfaz gráfica (Tkinter) y la base de datos SQLite (`GUI_DataBase/personas.db`).
- `FRT/`: scripts para reconocimiento facial (LBPH): enrolar, entrenar y reconocer.

Este README explica cómo usar el contenido del directorio.

Resumen de lo que hay
- `config.py` (en la raíz): centraliza rutas usadas por el proyecto. Rutas importantes:
  - `GUI_Data_DIR` / `GUI_DataBase` (carpeta de la GUI)
  - `GUI_DataBase/faces/` : aquí se guardan las imágenes por `person_id`.
  - `FRT/model/` : aquí se guarda el modelo entrenado (`model_lbph.yml`) y `labels.json`.

- Instalacion de Dependencias

```bash
pip install -r requirements.txt
```

Cómo usar (ejecución local)

- Ejecutar la GUI (CRUD personas):
  ```bash
  python GUI_DataBase/GUI_DB.py
  ```
  La GUI reserva `person_id`, permite enrolar (captura cámaras locales), entrena y guarda la persona en la BD.

- Enrolar desde scripts (cámara local):
  ```bash
  python FRT/enrolar_persona.py
  ```
  Esto abre la cámara y guarda imágenes en `GUI_DataBase/faces/{person_id}`.

- Entrenar el modelo con las imágenes existentes:
  ```bash
  python FRT/entrenar_modelo.py
  ```
  Resultado: `FRT/model/model_lbph.yml` y `FRT/model/labels.json`.

- Ejecutar reconocimiento local:
  ```bash
  python FRT/reconocimiento.py
  ```
  Abre la cámara, detecta rostros y devuelve la predicción basada en el modelo entrenado.

Notas prácticas
- Si querés eliminar las imágenes de una persona, borra `GUI_DataBase/faces/{person_id}` (pero no olvides sincronizar con la BD si corresponde).
- `requirements.txt` en la raíz contiene las versiones usadas.

---
Actualizado: NOV-2025
