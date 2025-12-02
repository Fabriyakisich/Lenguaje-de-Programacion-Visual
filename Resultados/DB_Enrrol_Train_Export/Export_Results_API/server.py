"""
Servidor API para exportar modelo, labels, fotos y datos de la BD.
La otra PC descargará todo el contenido en la carpeta 'data/' (limpio cada vez).

Ejecutar en TU PC:
    python Export_Results_API/server.py
    
Luego, desde OTRA PC:
    python Export_Results_API/client.py --server-ip 192.168.X.X --port 8000
"""

import json
import sqlite3
import io
import zipfile
from pathlib import Path
from typing import Dict, Any, List

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Importar configuración centralizada
import sys
proj_root = Path(__file__).resolve().parents[1]
if str(proj_root) not in sys.path:
    sys.path.insert(0, str(proj_root))

from config import DB_PATH, MODEL_PATH, LABELS_PATH, FACES_DIR

app = FastAPI(title="FRT Export API")

# Permitir CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def get_db_data() -> Dict[str, Dict[str, str]]:
    """Obtiene todas las personas de la BD (nombre, cedula, cargo)."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT id, nombre, cedula, cargo FROM personas ORDER BY nombre")
        # Devolver un diccionario con clave = nombre y valor = {cedula, puesto}
        personas = {}
        for row in cur.fetchall():
            name = row["nombre"]
            personas[name] = {
                "cedula": row["cedula"],
                "puesto": row["cargo"],
            }
        conn.close()
        return personas
    except Exception as e:
        print(f"Error leyendo BD: {e}")
        return []


def get_labels_data() -> Dict[str, str]:
    """Obtiene el mapping de labels (label_id -> person_id)."""
    labels_path = Path(LABELS_PATH)
    if not labels_path.exists():
        return {}
    try:
        data = json.loads(labels_path.read_text(encoding="utf-8"))
        # data: label_id -> person_id; convertimos a label_id -> person_name
        mapping = {}
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        for k, person_id in data.items():
            try:
                label = int(k) if isinstance(k, str) and k.isdigit() else k
            except:
                label = k
            # buscar nombre por id
            cur.execute("SELECT nombre FROM personas WHERE id = ?", (int(person_id),))
            row = cur.fetchone()
            if row:
                mapping[str(label)] = row[0]
            else:
                mapping[str(label)] = str(person_id)
        conn.close()
        return mapping
    except:
        return {}


def get_person_id_from_name(person_name: str) -> str:
    """Obtiene el person_id de una persona por su nombre."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT id FROM personas WHERE nombre = ?", (person_name,))
        row = cur.fetchone()
        conn.close()
        return str(row[0]) if row else None
    except:
        return None


def create_person_zip(person_name: str) -> io.BytesIO:
    """Crea un ZIP con todas las fotos de una persona (por nombre)."""
    person_id = get_person_id_from_name(person_name)
    if not person_id:
        raise HTTPException(status_code=404, detail=f"Persona '{person_name}' no encontrada")
    
    person_dir = Path(FACES_DIR) / person_id
    if not person_dir.exists() or not list(person_dir.glob("*.png")):
        raise HTTPException(status_code=404, detail=f"Persona '{person_name}' sin fotos")
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for img_file in sorted(person_dir.glob("*.png")):
            zf.write(img_file, arcname=img_file.name)
    
    zip_buffer.seek(0)
    return zip_buffer


def sanitize_filename(name: str) -> str:
    """Sanea un nombre para uso en filename: reemplaza espacios por '_' y elimina caracteres no aptos."""
    keep = []
    for ch in name:
        # permitir alfanuméricos, guión bajo y guión
        if ch.isalnum() or ch in ('_', '-'):
            keep.append(ch)
        elif ch.isspace():
            keep.append('_')
        # ignorar el resto
    sanitized = ''.join(keep)
    if not sanitized:
        sanitized = 'person'
    return sanitized


@app.get('/api/faces_all')
async def get_all_faces():
    """Devuelve un ZIP con todas las imágenes de todas las personas.

    Los ficheros dentro del ZIP se entregan con nombre saneado: <PERSON_NAME>_<original>.
    Esto permite extraerlas directamente en `data/` sin carpetas por persona.
    """
    root = Path(FACES_DIR)
    if not root.exists():
        raise HTTPException(status_code=404, detail='No hay imágenes disponibles')

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        # recorrer etiquetas para mapear label->person_name (labels.json contiene person_id)
        labels = {}
        labels_path = Path(LABELS_PATH)
        if labels_path.exists():
            try:
                labels = json.loads(labels_path.read_text(encoding='utf-8'))
            except:
                labels = {}

        # Si labels vacío, recorrer carpetas por id y resolver nombre desde BD
        # Para cada carpeta (person_id) agregamos sus imágenes con nombre saneado
        for person_dir in sorted(root.iterdir()):
            if not person_dir.is_dir():
                continue
            person_id = person_dir.name
            # intentar resolver nombre
            person_name = None
            # si labels tiene mapping label->person_id, buscar label key
            for lbl, pid in labels.items():
                if str(pid) == str(person_id):
                    # obtener nombre desde BD
                    try:
                        conn = sqlite3.connect(DB_PATH)
                        cur = conn.cursor()
                        cur.execute('SELECT nombre FROM personas WHERE id = ?', (int(person_id),))
                        row = cur.fetchone()
                        conn.close()
                        if row:
                            person_name = row[0]
                    except:
                        person_name = None
                    break
            if not person_name:
                # fallback: buscar por id en BD
                try:
                    conn = sqlite3.connect(DB_PATH)
                    cur = conn.cursor()
                    cur.execute('SELECT nombre FROM personas WHERE id = ?', (int(person_id),))
                    row = cur.fetchone()
                    conn.close()
                    if row:
                        person_name = row[0]
                except:
                    person_name = None

            safe = sanitize_filename(person_name or person_id)
            for img_file in sorted(person_dir.glob('*.png')):
                arcname = f"{safe}_{img_file.name}"
                zf.write(img_file, arcname=arcname)

    zip_buffer.seek(0)
    return StreamingResponse(iter([zip_buffer.getvalue()]), media_type='application/zip', headers={
        'Content-Disposition': 'attachment; filename=all_faces.zip'
    })


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/api/personas")
async def get_personas() -> Dict[str, Dict[str, str]]:
    """
    Descargar mapa de personas: { "Nombre": { "cedula": "..", "puesto": ".." } }
    """
    personas = get_db_data()
    return personas


@app.get("/api/labels")
async def get_labels() -> Dict[str, str]:
    """
    Descargar el mapping de labels (label_id -> person_id).
    Necesario para el modelo LBPH.
    """
    return get_labels_data()


@app.get("/api/model")
async def get_model():
    """
    Descargar el modelo LBPH entrenado (model_lbph.yml).
    Es un archivo binario YAML.
    """
    if not Path(MODEL_PATH).exists():
        raise HTTPException(status_code=404, detail="Modelo no entrenado aún")
    
    return FileResponse(
        path=MODEL_PATH,
        filename="model_lbph.yml",
        media_type="application/octet-stream"
    )


@app.get("/api/faces/{person_name}")
async def get_faces(person_name: str):
    """
    Descargar todas las fotos de una persona (por nombre) comprimidas en ZIP.
    """
    try:
        zip_buffer = create_person_zip(person_name)
        return StreamingResponse(
            iter([zip_buffer.getvalue()]),
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename={person_name}_faces.zip"}
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    """Health check para verificar que el servidor está activo."""
    return {"status": "ok", "service": "FRT Export API"}


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run FRT Export API server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=9000, help="Port to bind (default: 9000)")
    args = parser.parse_args()

    print("\n" + "="*70)
    print("🚀 SERVIDOR FRT EXPORT API")
    print("="*70)
    print(f"📁 Proyecto: {proj_root}")
    print(f"🗄️  BD: {DB_PATH}")
    print(f"🤖 Modelo: {MODEL_PATH}")
    print(f"📷 Fotos: {FACES_DIR}")
    print("="*70)
    print(f"\n⏳ Iniciando servidor en {args.host}:{args.port}...\n")
    
    try:
        uvicorn.run(
            app,
            host=args.host,
            port=args.port,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\n✋ Servidor detenido.")
