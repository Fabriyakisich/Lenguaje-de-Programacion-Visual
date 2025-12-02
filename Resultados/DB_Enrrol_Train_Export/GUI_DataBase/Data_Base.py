import sqlite3
import os

# Ruta centralizada: cámbiala cuando muevas el proyecto
BASE_DIR = r"C:\Users\favri\Documents\Fabrizzio Bianchini\Facultad\Mecatronica\LPV\Proyecto\GUI_DataBase"
DB_PATH = os.path.join(BASE_DIR, 'personas.db')


def crear_base_de_datos():
    """Crea la base de datos y la tabla `personas` si no existen."""
    ruta = BASE_DIR
    db_path = DB_PATH

    if not os.path.exists(db_path):
        if not os.path.exists(ruta):
            os.makedirs(ruta)

        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        # Crear la tabla para almacenar personas y sus características
        c.execute('''
            CREATE TABLE IF NOT EXISTS personas (
                id INTEGER PRIMARY KEY,
                nombre TEXT,
                cedula TEXT,
                ultima_hora_ingreso TEXT,
                cargo TEXT
            )
        ''')

        conn.commit()
        conn.close()
        print(f"Base de datos creada en: {db_path}")
    else:
        # Si ya existe la base de datos, comprobar si la tabla fue creada con AUTOINCREMENT
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        try:
            c.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='personas'")
            row = c.fetchone()
            if row and row[0] and 'AUTOINCREMENT' in row[0].upper():
                # Necesitamos migrar la tabla para quitar AUTOINCREMENT y conservar datos
                print('Migrando tabla personas para eliminar AUTOINCREMENT...')
                c.execute('BEGIN')
                # Crear tabla temporal sin AUTOINCREMENT
                c.execute('''
                    CREATE TABLE IF NOT EXISTS personas_new (
                        id INTEGER PRIMARY KEY,
                        nombre TEXT,
                        cedula TEXT,
                        ultima_hora_ingreso TEXT,
                        cargo TEXT
                    )
                ''')
                # Copiar datos existentes
                c.execute('''INSERT OR IGNORE INTO personas_new (id, nombre, cedula, ultima_hora_ingreso, cargo)
                             SELECT id, nombre, cedula, ultima_hora_ingreso, cargo FROM personas''')
                # Eliminar tabla antigua y renombrar
                c.execute('DROP TABLE personas')
                c.execute('ALTER TABLE personas_new RENAME TO personas')
                # Limpiar secuencia (si existe)
                try:
                    c.execute("DELETE FROM sqlite_sequence WHERE name='personas'")
                except Exception:
                    pass
                conn.commit()
                print('Migración completada.')
        except Exception as e:
            print('Error comprobando/migrando la base de datos:', e)
        finally:
            conn.close()
        print(f"El archivo de la base de datos ya existe en: {db_path}")

def mostrar_personas():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT * FROM personas")
    personas = c.fetchall()

    conn.close()
    return personas


def obtener_siguiente_id():
    """Calcula el siguiente id disponible (sin insertar en la base).
    Útil para reservar un id antes de realizar enrolamiento/entrenamiento.
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id FROM personas ORDER BY id")
    filas = c.fetchall()
    conn.close()
    ids = [r[0] for r in filas]

    nuevo_id = 1
    for existing in ids:
        if existing == nuevo_id:
            nuevo_id += 1
        elif existing > nuevo_id:
            break
    return nuevo_id


def insertar_persona_con_id(person_id, nombre, cedula, cargo):
    """Inserta una persona usando un `person_id` ya decidido por el caller.
    Devuelve el id insertado.
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT INTO personas (id, nombre, cedula, ultima_hora_ingreso, cargo)
                 VALUES (?, ?, ?, ?, ?)''', (person_id, nombre, cedula, None, cargo))
    conn.commit()
    conn.close()
    return person_id

def insertar_persona(nombre, cedula, cargo):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Intentar usar el ID más bajo disponible (reutilizar huecos de eliminaciones)
    # Obtenemos todos los IDs existentes ordenados y buscamos el primer hueco
    c.execute("SELECT id FROM personas ORDER BY id")
    filas = c.fetchall()
    ids = [r[0] for r in filas]

    nuevo_id = 1
    for existing in ids:
        if existing == nuevo_id:
            nuevo_id += 1
        elif existing > nuevo_id:
            # encontramos un hueco: existing > nuevo_id
            break

    # Insertar especificando el id calculado
    c.execute('''INSERT INTO personas (id, nombre, cedula, ultima_hora_ingreso, cargo)
                 VALUES (?, ?, ?, ?, ?)''', (nuevo_id, nombre, cedula, None, cargo))

    conn.commit()
    conn.close()
    return nuevo_id

def editar_persona(id, nombre=None, cedula=None, hora_ingreso=None, cargo=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    if nombre:
        c.execute("UPDATE personas SET nombre = ? WHERE id = ?", (nombre, id))
    if cedula:
        c.execute("UPDATE personas SET cedula = ? WHERE id = ?", (cedula, id))
    if hora_ingreso:
        c.execute("UPDATE personas SET ultima_hora_ingreso = ? WHERE id = ?", (hora_ingreso, id))
    if cargo:
        c.execute("UPDATE personas SET cargo = ? WHERE id = ?", (cargo, id))

    conn.commit()
    conn.close()

def eliminar_persona(id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("DELETE FROM personas WHERE id = ?", (id,))

    conn.commit()
    conn.close()

def buscar_personas(termino):
    """Buscar personas por nombre, cédula o cargo usando LIKE (case-insensitive)."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    like_term = f"%{termino}%"
    c.execute("SELECT * FROM personas WHERE nombre LIKE ? OR cedula LIKE ? OR cargo LIKE ?", (like_term, like_term, like_term))
    resultados = c.fetchall()

    conn.close()
    return resultados

def persona_existe(nombre, cedula, exclude_id=None):
    """Devuelve True si ya existe una persona con el mismo nombre+cedula o la misma cédula.
    Si `exclude_id` se proporciona, ignora esa fila (útil al editar).
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Reglas: si existe el mismo nombre -> existe (no permitir duplicados por nombre).
    # También no permitir cédulas duplicadas. El cargo puede repetirse sin problema.
    if exclude_id is None:
        c.execute("SELECT id FROM personas WHERE nombre = ? OR cedula = ?", (nombre, cedula))
    else:
        c.execute("SELECT id FROM personas WHERE (nombre = ? OR cedula = ?) AND id != ?", (nombre, cedula, exclude_id))

    row = c.fetchone()
    conn.close()
    return row is not None

# crear_base_de_datos()