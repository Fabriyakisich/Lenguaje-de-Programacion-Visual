import cv2
import json
import sqlite3
from pathlib import Path
from typing import Tuple, Optional

try:
    from config import MODEL_PATH, LABELS_PATH, DB_PATH
except Exception:
    # If the script is executed directly from inside FRT/, the project root
    # may not be on sys.path. Add the project root (parent of the package)
    # so we can import `config`.
    import sys
    proj_root = Path(__file__).resolve().parents[1]
    if str(proj_root) not in sys.path:
        sys.path.insert(0, str(proj_root))
    from config import MODEL_PATH, LABELS_PATH, DB_PATH

FACE_SIZE = (200, 200)
THRESHOLD = 60.0


def load_model() -> Tuple[cv2.face_BasicFaceRecognizer, dict]:
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(str(MODEL_PATH))
    label_to_person = {}
    if Path(LABELS_PATH).exists():
        label_to_person = json.loads(Path(LABELS_PATH).read_text(encoding='utf-8'))
        # keys stored as strings in JSON -> convert to int
        label_to_person = {int(k): v for k, v in label_to_person.items()}
    return recognizer, label_to_person


def _person_exists(person_id: str) -> bool:
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM personas WHERE id = ?", (int(person_id),))
        row = cur.fetchone()
        conn.close()
        return row is not None
    except Exception:
        return False


def recognize() -> None:
    recognizer, label_to_person = load_model()

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    if not cap.isOpened():
        raise RuntimeError("No pude abrir la cámara.")

    print("Reconociendo... (q para salir)")

    while True:
        ok, frame = cap.read()
        if not ok:
            print("No pude leer frame.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # detect face
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        if len(faces) > 0:
            x, y, w, h = max(faces, key=lambda r: r[2] * r[3])
            face = gray[y:y+h, x:x+w]
            face_norm = cv2.equalizeHist(cv2.resize(face, FACE_SIZE))

            label, conf = recognizer.predict(face_norm)
            person_id = label_to_person.get(label)
            is_auth = (conf < THRESHOLD) and (person_id is not None) and _person_exists(person_id)

            if is_auth:
                # get name from DB for display
                try:
                    conn = sqlite3.connect(DB_PATH)
                    cur = conn.cursor()
                    cur.execute("SELECT nombre FROM personas WHERE id = ?", (int(person_id),))
                    row = cur.fetchone()
                    conn.close()
                    display_name = row[0] if row else str(person_id)
                except Exception:
                    display_name = str(person_id)
                auth_status = f"{display_name} (Autorizado)"
                color = (0, 255, 0)
            else:
                auth_status = "No autorizado"
                color = (0, 0, 255)

            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(frame, auth_status, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        else:
            cv2.putText(frame, "No autorizado", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        cv2.imshow("Reconocimiento Facial", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    recognize()
import cv2                # Importamos OpenCV, una librería popular para el procesamiento de imágenes y video.
import json               # Importamos la librería 'json' para leer y escribir datos en formato JSON (en este caso, las etiquetas).
import time               # Importamos 'time' para trabajar con funciones relacionadas al tiempo (en este caso, no es necesario en este archivo, pero se podría usar para manejar temporizadores).
from pathlib import Path  # Importamos 'Path' de 'pathlib', que facilita la manipulación de rutas de archivos y directorios.

# Definimos las rutas donde se guardan el modelo entrenado y las etiquetas
MODEL_PATH = Path("model_lbph.yml")  # Ruta donde se almacenará el modelo entrenado.
LABELS_PATH = Path("labels.json")    # Ruta donde se guardarán las etiquetas (ID -> nombre).
FACE_SIZE = (200, 200)               # El tamaño al que se redimensionarán las caras antes de la predicción.
THRESHOLD = 60.0                     # Umbral de confianza. Si la confianza (error) es menor que este valor, se acepta el rostro.

# Función que carga el modelo entrenado y las etiquetas
def load_model():
    # Cargamos el modelo LBPH (Local Binary Pattern Histogram) para el reconocimiento facial.
    recognizer = cv2.face.LBPHFaceRecognizer_create() 
    recognizer.read(str(MODEL_PATH))  # Leemos el modelo entrenado desde el archivo 'model_lbph.yml'.
    
    # Cargamos las etiquetas (ID -> nombre) desde el archivo 'labels.json'.
    label_to_name = json.loads(LABELS_PATH.read_text(encoding="utf-8"))
    
    # Retornamos el reconocedor (modelo) y el diccionario de etiquetas.
    return recognizer, label_to_name

# Función para detectar caras en una imagen en escala de grises
def detect_face(gray):
    # Cargamos el clasificador Haar previamente entrenado para detectar rostros.
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    
    # Detectamos las caras en la imagen usando el clasificador Haar.
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    
    # Si no se detecta ninguna cara, retornamos None.
    if len(faces) == 0:
        return None
    
    # Si se detecta más de una cara, seleccionamos la que tiene mayor área (la más cercana a la cámara).
    x, y, w, h = max(faces, key=lambda r: r[2] * r[3])
    
    # Retornamos la cara recortada y las coordenadas del rectángulo que rodea la cara (x, y, w, h).
    return gray[y:y+h, x:x+w], (x, y, w, h)

# Función principal para realizar el reconocimiento facial
def recognize():
    # Cargamos el modelo entrenado y las etiquetas (ID -> nombre)
    recognizer, label_to_name = load_model()

    # Abrimos la cámara (índice 0 para la cámara de DroidCam, según lo mencionado)
    cap = cv2.VideoCapture(0)  # Usamos el índice 0 (cámara de DroidCam)
    
    # Establecemos las dimensiones del video de la cámara (1280x720 píxeles o cualquier resolución que prefieras)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)  # Resolución en el eje X (ancho)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)  # Resolución en el eje Y (alto)
    
    # Verificamos si la cámara se ha abierto correctamente, si no, lanzamos un error
    if not cap.isOpened():
        raise RuntimeError("No pude abrir la cámara.")  # Si no se puede acceder a la cámara, lanzamos un error.

    print("Reconociendo... (q para salir)")  # Mensaje que informa al usuario que el sistema está listo para reconocer rostros.

    # Variable para saber si la persona está autorizada
    is_authorized = False  # Inicialmente asumimos que no está autorizado

    # Bucle principal donde capturamos fotogramas de la cámara de forma continua
    while True:
        ok, frame = cap.read()  # Leemos un fotograma de la cámara.
        
        # Si no se puede leer el fotograma, mostramos un mensaje de error y salimos
        if not ok:
            print("No pude leer frame.")
            break

        # Convertimos el fotograma a escala de grises, ya que el modelo de reconocimiento funciona con imágenes en blanco y negro
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Llamamos a la función detect_face para detectar si hay alguna cara en la imagen en escala de grises.
        res = detect_face(gray)

        # Si se detecta una cara, procesamos el resultado.
        if res is not None:
            face, (x, y, w, h) = res  # Extraemos la cara y las coordenadas del rectángulo que rodea la cara.
            
            # Normalizamos la cara y la redimensionamos al tamaño definido en FACE_SIZE.
            face_norm = cv2.equalizeHist(cv2.resize(face, FACE_SIZE))
            
            # Usamos el modelo entrenado para hacer la predicción y obtener la etiqueta (ID) y la confianza (error).
            label, conf = recognizer.predict(face_norm)
            
            # Obtenemos el nombre de la persona a partir de la etiqueta (ID) usando 'label_to_name'.
            name = label_to_name.get(str(label), "Desconocido")
            
            # Si la confianza es menor que el umbral, se considera que el rostro es reconocido.
            is_auth = conf < THRESHOLD
            
            # Si el rostro es reconocido y autorizado, mostramos el nombre, si no mostramos "No autorizado"
            if is_auth:
                auth_status = f"{name} (Autorizado)"
                color = (0, 255, 0)  # Verde para autorizado
                is_authorized = True  # La persona está autorizada
                print(is_authorized)
            else:
                auth_status = "No autorizado"
                color = (0, 0, 255)  # Rojo para no autorizado
                is_authorized = False  # La persona no está autorizada

            # Dibujamos un rectángulo alrededor de la cara detectada.
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            
            # Escribimos el texto (nombre y estado de autorización) sobre la imagen.
            cv2.putText(frame, auth_status, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        else:
            # Si no se detecta ninguna cara, mostramos "No autorizado"
            cv2.putText(frame, "No autorizado", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            is_authorized = False  # La persona no está autorizada si no se detecta cara

        # Mostramos el fotograma con la cara detectada y el nombre en la ventana de OpenCV.
        cv2.imshow("Reconocimiento Facial", frame)

        # Si se presiona la tecla 'q', salimos del bucle de reconocimiento
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # Aquí es donde puedes enviar la variable `is_authorized` al microcontrolador
        # Por ejemplo, si estás usando un puerto serial, podrías hacer algo como:
        # if is_authorized:
        #     serial_port.write(b'1')  # Mandar señal para abrir la puerta
        # else:
        #     serial_port.write(b'0')  # Mandar señal para no abrir la puerta

    # Liberamos la cámara y cerramos todas las ventanas de OpenCV al finalizar.
    cap.release()
    cv2.destroyAllWindows()

# Punto de entrada del código: cuando se ejecuta el archivo.
if __name__ == "__main__":
    recognize()  # Llamamos a la función de reconocimiento facial para iniciar el proceso.
