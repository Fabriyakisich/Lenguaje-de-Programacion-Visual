import cv2                # Importamos OpenCV para trabajar con imágenes y video.
import numpy as np        # Importamos NumPy, una librería para trabajar con arrays y matrices de datos.
import os                 # Importamos 'os' para interactuar con el sistema de archivos (crear directorios, etc.).
import json               # Importamos 'json' para leer y escribir archivos JSON (por ejemplo, las etiquetas).
from pathlib import Path  # Importamos 'Path' de 'pathlib' para trabajar de manera más cómoda con rutas de archivos.

# Definimos las rutas donde se guardarán el modelo y las etiquetas
MODEL_PATH = Path("model_lbph.yml")  # Ruta donde se guardará el modelo entrenado.
LABELS_PATH = Path("labels.json")    # Ruta donde se guardarán las etiquetas (asociación ID -> nombre).
DATA_ROOT = Path("data")             # Carpeta donde se almacenan las imágenes de las personas.

# Esta función devuelve una lista de todas las carpetas en 'data/', que corresponden a las personas.
def list_people():
    return sorted([p.name for p in DATA_ROOT.iterdir() if p.is_dir()])  # Devuelve la lista de personas (subdirectorios en 'data').

# Esta función entrena el modelo con las imágenes capturadas de todas las personas en 'data/'.
def train_model():
    people = list_people()  # Obtenemos la lista de personas (subdirectorios en 'data/')
    
    # Si no hay personas (no hay carpetas en 'data'), mostramos un mensaje y salimos de la función.
    if not people:
        print("No hay carpetas en data/. Enrolá primero.")  # Mensaje de error si no hay personas.
        return False

    # Inicializamos listas para almacenar las imágenes y etiquetas.
    images, labels = [], []
    name_to_label = {}  # Diccionario que asocia nombres de personas a etiquetas numéricas.
    label_to_name = {}  # Diccionario que asocia etiquetas numéricas a nombres de personas.
    next_label = 1  # Inicializamos el siguiente valor de etiqueta (empieza en 1).

    # Cargamos las etiquetas previamente entrenadas si existen (es decir, si 'labels.json' existe).
    if LABELS_PATH.exists():
        label_to_name = json.loads(LABELS_PATH.read_text(encoding="utf-8"))  # Cargamos las etiquetas del archivo 'labels.json'.
        
        # Aseguramos que las etiquetas sean enteros, ya que pueden haberse guardado como cadenas de texto.
        name_to_label = {name: int(label) for label, name in label_to_name.items()}  
        
        # Si ya existen etiquetas, asignamos una nueva etiqueta mayor a la última utilizada.
        if name_to_label:
            next_label = max(name_to_label.values()) + 1  # Calculamos la siguiente etiqueta disponible.

    # Recorremos todas las personas (carpetas en 'data/') y procesamos sus imágenes.
    for name in people:
        person_dir = DATA_ROOT / name  # Ruta de la carpeta de la persona.
        files = sorted([*person_dir.glob("*.png")])  # Obtenemos todas las imágenes (archivos .png) de esa persona.
        if not files:
            continue  # Si no hay imágenes para esa persona, pasamos a la siguiente.

        # Si la persona aún no tiene una etiqueta asignada, la asignamos y la agregamos a 'label_to_name'.
        if name not in name_to_label:
            name_to_label[name] = next_label
            label_to_name[next_label] = name
            next_label += 1  # Incrementamos la etiqueta para la siguiente persona.
        
        lab = name_to_label[name]  # Obtenemos la etiqueta correspondiente para esta persona.

        # Cargamos las imágenes de la persona y las añadimos a las listas 'images' y 'labels'.
        for f in files:
            img = cv2.imread(str(f), cv2.IMREAD_GRAYSCALE)  # Leemos la imagen en escala de grises.
            if img is None:
                continue  # Si no se pudo leer la imagen, pasamos a la siguiente.
            images.append(img)  # Añadimos la imagen a la lista de imágenes.
            labels.append(lab)   # Añadimos la etiqueta correspondiente a la lista de etiquetas.

    # Si no hay imágenes para entrenar (la lista está vacía), mostramos un mensaje y salimos.
    if not images:
        print("No hay imágenes para entrenar.")  # Mensaje de error si no hay imágenes.
        return False

    # Entrenamos el modelo con las imágenes y etiquetas.
    recognizer = cv2.face.LBPHFaceRecognizer_create()  # Creamos un reconocedor LBPH (Local Binary Pattern Histogram).
    recognizer.train(images, np.array(labels))  # Entrenamos el modelo con las imágenes y etiquetas.
    
    # Guardamos el modelo entrenado en 'model_lbph.yml'.
    recognizer.save(str(MODEL_PATH))
    
    # Guardamos las etiquetas en 'labels.json'.
    LABELS_PATH.write_text(json.dumps(label_to_name, ensure_ascii=False, indent=2), encoding="utf-8")

    # Mensaje de éxito cuando se completa el entrenamiento y se guardan los archivos.
    print(f"[OK] Modelo guardado en {MODEL_PATH}")
    print(f"[OK] Labels guardados en {LABELS_PATH}")
    
    return True  # Indicamos que el entrenamiento se completó correctamente.

# Punto de entrada del código: cuando se ejecuta el archivo.
if __name__ == "__main__":
    trained = train_model()  # Llamamos a la función de entrenamiento.
    if not trained:  # Si algo salió mal en el entrenamiento, terminamos el programa.
        raise SystemExit(1)
