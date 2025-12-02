import cv2                # OpenCV para procesamiento de imágenes y video
import os
import time
from pathlib import Path
from typing import Optional, Callable, Tuple

from config import FACES_DIR

FACE_SIZE = (200, 200)    # Tamaño de la cara para normalizar
SAMPLES = 40              # Número por defecto de fotos por persona



# Esta función detecta las caras dentro de una imagen en escala de grises
def detect_face(gray):
    # Cargamos el clasificador en cascada de Haar para detectar caras. Este clasificador ya está entrenado por OpenCV.
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    
    # Usamos el clasificador para detectar las caras en la imagen en escala de grises. 
    # '1.3' es un factor de escala y '5' es el número mínimo de vecinos para validar una cara.
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    
    # Si no detecta ninguna cara, retornamos 'None'
    if len(faces) == 0:
        return None
    
    # Si detecta más de una cara, selecciona la que tiene el área más grande (la cara más cercana)
    x, y, w, h = max(faces, key=lambda r: r[2] * r[3])
    
    # Retorna la cara recortada de la imagen y las coordenadas de la cara detectada (x, y, w, h)
    return gray[y:y+h, x:x+w], (x, y, w, h)

def enroll_person(person_id: str, person_name: Optional[str], n_samples: int = SAMPLES,
                  out_root: Optional[Path] = None,
                  progress_cb: Optional[Callable[[int, str], None]] = None) -> Tuple[bool, str, int]:
    """Enrolar una persona usando la cámara.

    Args:
        person_id: identificador de la persona (se usa para nombrar la carpeta)
        person_name: nombre (opcional) para usar en los nombres de archivo
        n_samples: número de muestras a capturar
        out_root: carpeta raíz donde guardar fotos (por defecto FACES_DIR)
        progress_cb: callback opcional progress_cb(percent:int, message:str)

    Returns:
        (ok: bool, message: str)
    """

    if out_root is None:
        out_root = Path(FACES_DIR)

    person_dir = Path(out_root) / str(person_id)
    person_dir.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(0)
    
    # Establecemos las dimensiones del video (ancho y alto) de la cámara
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)  # Ancho de la imagen en píxeles (1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720) # Alto de la imagen en píxeles (720)

    # Si la cámara no se puede abrir, lanzamos un error
    if not cap.isOpened():
        raise RuntimeError("No pude abrir la cámara.")  # Si no se abre correctamente, se muestra un error.

    count = 0  # Variable para contar los fotogramas leídos de la cámara
    taken = 0  # Variable para contar las fotos capturadas de la persona
    print(f"Enrolando id={person_id} name={person_name}... (q para salir)")

    # Mientras no se haya alcanzado el número de muestras definido (n_samples)
    while taken < n_samples:
        ok, frame = cap.read()  # Leemos un fotograma de la cámara. 'ok' es un valor booleano que indica si la lectura fue exitosa.
        
        # Si no se puede leer el fotograma, terminamos el proceso
        if not ok:
            print("No pude leer frame de la cámara.")  # Mensaje de error
            break  # Rompe el bucle si no se pudo leer el fotograma.

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Convertimos el fotograma a escala de grises para facilitar la detección de caras.
        res = detect_face(gray)  # Llamamos a la función 'detect_face' para detectar la cara en la imagen en escala de grises.
        
        # Si detectamos una cara (es decir, la función 'detect_face' no devolvió None)
        if res is not None:
            face, _ = res  # Extraemos la cara de la imagen, el segundo valor es ignorado aquí
            face_norm = cv2.equalizeHist(cv2.resize(face, FACE_SIZE))  # Normalizamos el histograma de la cara y la redimensionamos al tamaño especificado en FACE_SIZE.
            
            # Mostramos la cara normalizada en una ventana de OpenCV
            cv2.imshow(f"Enrolando {person_name}", face_norm)

            # Guardamos una imagen cada 3 iteraciones para obtener una variedad de fotos
            if count % 3 == 0:
                # Crear nombre usando id y opcionalmente el nombre
                base = person_name if person_name else str(person_id)
                fname = person_dir / f"{base}_{int(time.time())}_{taken:03d}.png"
                cv2.imwrite(str(fname), face_norm)
                taken += 1  # Aumentamos el contador de fotos tomadas
                print(f"[+] Imagen {taken}/{n_samples}: {fname.name}")
                if progress_cb:
                    try:
                        pct = int(taken * 100 / n_samples)
                        progress_cb(pct, f"Capturadas {taken}/{n_samples}")
                    except Exception:
                        pass

        # Si no se detecta ninguna cara, mostramos el fotograma original de la cámara
        else:
            cv2.imshow(f"Enrolando {person_name}", frame)

        count += 1  # Aumentamos el contador de fotogramas leídos

        # Si se presiona la tecla 'q', salimos del bucle
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Cancelado por el usuario.")  # Mensaje de cancelación
            break

    # Liberamos la cámara y cerramos todas las ventanas de OpenCV al finalizar
    cap.release()
    cv2.destroyAllWindows()
    msg = f"Enrolamiento id={person_id} terminado con {taken} muestras."
    print(f"[OK] {msg}")
    return True, msg, taken

# Punto de entrada del código: cuando se ejecuta el archivo
if __name__ == "__main__":
    person_name = input("Nombre de la persona: ")
    person_id = input("ID de la persona (ej: 1): ")
    ok, msg, taken = enroll_person(person_id, person_name, 40)
    if not ok:
        print("Error:", msg)
    else:
        print(msg)
