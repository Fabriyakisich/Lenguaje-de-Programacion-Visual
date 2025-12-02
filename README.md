# Sistema de Reconocimiento Facial FRT

**Integrantes:**
- Arréllaga, Fernando -> 
- Bianchini, Fabrizzio ->favrisebastian10@gmail.com
- Jacquet, Judith -> judithjacquetb@gmail.com
- Yakisich, Fabrizzio -> fabriyakisich@gmail.com

Descripcion del Proyecto: El proyecto se basa en el desarrollo de un detector facial que abra puertas para cierto personal autorizado que esta guardada en la base de datos (imagenes). Implementa un sistema completo de reconocimiento facial dividido en dos partes principales:

1. **Aplicación local**: enrolamiento, almacenamiento y entrenamiento del modelo.  
2. **Servidor FastAPI**: exporta el modelo entrenado, la base de datos y las imágenes para que otra computadora pueda sincronizar todo mediante un cliente externo.

La arquitectura permite que una sola PC haga el trabajo pesado y las demás solo descarguen el modelo entrenado.

---

## 🧱 Estructura del Proyecto

```
Export_Results_API/
    README.md
    server.py           → Servidor FastAPI para exportar modelo, DB y fotos

FRT/
    model/
        labels.json
        model_lbph.yml  → Modelo entrenado LBPH
    enrolar_persona.py  → Captura de imágenes con OpenCV
    entrenar_modelo.py  → Entrenamiento del modelo LBPH

GUI_DataBase/
    faces/              → Imágenes organizadas por ID
    Data_Base.py        → Base SQLite con gestión de personas
    GUI_DB.py           → Interfaz Tkinter (gestión, enrolamiento, entrenamiento)
    personas.db         → Base de datos SQLite

config.py               → Rutas centralizadas
client.py               → Cliente externo para sincronización
README.md               → Este archivo
requirements.txt        → Dependencias del proyecto
```

---

# 🖥️ 1. Aplicación Local (Tkinter + SQLite + OpenCV)

La base de datos, su gestion y el enrolamiento corre en la PC “servidor”.

---

## ✔️ 1.1 Gestión de Personas (GUI_DB.py)

Interfaz creada con Tkinter que permite:

- Agregar personas (nombre, cédula, cargo)  
- Editar y eliminar registros  
- Buscar personas  
- Ver la tabla completa mediante ttk.Treeview  

Toda la información se guarda en **SQLite (personas.db)**, administrada desde `Data_Base.py`.

---

## ✔️ 1.2 Enrolamiento de Personas (enrolar_persona.py)

El sistema captura entre **40 fotos** usando OpenCV.

- Detecta la cara con Haar Cascades  
- Normaliza la imagen (200×200 px)  
- Guarda las fotos en:

```
faces/<person_id>/
    ejemplo_XXXX.png
```

---

## ✔️ 1.3 Entrenamiento del Modelo (entrenar_modelo.py)

Se entrena un modelo **LBPH** (Local Binary Patterns Histograms).

Genera:

```
FRT/model/model_lbph.yml      → Modelo entrenado
FRT/model/labels.json         → Mapeo label → id
```

---

# 🌐 2. Servidor FastAPI (server.py)

Permite exportar modelo, DB y fotos a otra PC mediante HTTP.

Ejecutar:

```bash
python Export_Results_API/server.py --host 0.0.0.0 --port 9000
```

### Endpoints:

| Endpoint | Descripción |
|---------|-------------|
| `/api/personas` | Devuelve nombre, cédula y cargo |
| `/api/labels` | Devuelve el mapeo label → id |
| `/api/model` | Descarga `model_lbph.yml` |
| `/api/faces_all` | Descarga todas las fotos en un ZIP |
| `/api/health` | Verifica que el servidor está activo |

---

# 🔗 3. Cliente Externo (client.py)

El cliente se ejecuta en otra computadora para sincronizar todo:

```bash
python client.py --server-ip 192.168.1.23 --port 9000
```

El cliente realiza:

1. Verificación del servidor  
2. Limpieza de la carpeta `data/`  
3. Descarga:
   - `db_personas.json`
   - `labels.json`
   - `model_lbph.yml`
4. (Opcional) descarga de fotos  
5. Deja todo listo para reconocimiento

El cliente **no entrena**, solo usa el modelo entrenado para el reconocimiento.

---

# 🛠️ 4. Tecnologías Utilizadas

- Python 3  
- FastAPI + Uvicorn  
- Tkinter  
- SQLite3  
- OpenCV  
- Requests  
- JSON / ZIP  

---

# ▶️ 5. Flujo General del Sistema

1. Se agrega una persona  
2. Se realiza el enrolamiento (captura de fotos)  
3. Se entrena el modelo LBPH  
4. El servidor expone modelo y base de datos  
5. El cliente externo descarga todo  
6. La PC cliente queda lista para reconocimiento facial

---

# 📌 5. Instalación

```bash
pip install -r requirements.txt
```

### Ejecutar interfaz:

```bash
python GUI_DataBase/GUI_DB.py
```

### Ejecutar servidor:

```bash
python Export_Results_API/server.py
```

### Ejecutar cliente:

```bash
python client.py --server-ip <IP_DEL_SERVIDOR>
```

---
