import cv2                # Importamos OpenCV, una librería para el procesamiento de imágenes y video
import os                 # Importamos 'os', que nos permite interactuar con el sistema de archivos (carpetas, archivos, etc.)
import time               # Importamos 'time', utilizado para gestionar el tiempo (por ejemplo, para nombres de archivos únicos)
from pathlib import Path  # Importamos 'Path' de 'pathlib' para trabajar de manera más cómoda con rutas de archivos y directorios

FACE_SIZE = (200, 200)    # Definimos el tamaño de las caras que usaremos para el modelo (200x200 píxeles)
SAMPLES = 40              # Definimos el número de fotos que tomaremos por persona (40 por persona)
DATA_ROOT = Path("data")  # Carpeta donde se guardarán las fotos de las personas. 'Path' permite manejar directorios de manera más eficiente.

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

def enroll_person(person_name: str, n_samples: int):
    # Creamos un directorio para la persona (si no existe) donde se almacenarán las fotos capturadas.
    person_dir = DATA_ROOT / person_name
    person_dir.mkdir(parents=True, exist_ok=True)  # 'mkdir' crea la carpeta y 'exist_ok=True' asegura que no falle si ya existe.

    # Abrimos la cámara (índice 0 se refiere a la cámara predeterminada)
    cap = cv2.VideoCapture(0)
    
    # Establecemos las dimensiones del video (ancho y alto) de la cámara
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Ancho de la imagen en píxeles (640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480) # Alto de la imagen en píxeles (480)

    # Si la cámara no se puede abrir, lanzamos un error
    if not cap.isOpened():
        raise RuntimeError("No pude abrir la cámara.")  # Si no se abre correctamente, se muestra un error.

    count = 0  # Variable para contar los fotogramas leídos de la cámara
    taken = 0  # Variable para contar las fotos capturadas de la persona
    print(f"Enrolando a {person_name}... (q para salir)")  # Mensaje que muestra que está empezando a enrolar a la persona.

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
                # Creamos un nombre único para cada imagen utilizando el tiempo actual y el contador 'taken'
                fname = person_dir / f"{person_name}_{int(time.time())}_{taken:03d}.png"
                cv2.imwrite(str(fname), face_norm)  # Guardamos la imagen en el directorio correspondiente
                taken += 1  # Aumentamos el contador de fotos tomadas
                print(f"[+] Imagen {taken}/{n_samples}: {fname.name}")  # Mostramos el progreso de las fotos capturadas

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
    print(f"[OK] Enrolamiento de {person_name} terminado con {taken} muestras.")  # Mensaje final cuando se termina el enrolamiento.

# Punto de entrada del código: cuando se ejecuta el archivo
if __name__ == "__main__":
    person_name = input("Nombre de la persona: ")  # Pedimos el nombre de la persona que será enrolada
    enroll_person(person_name, 40)  # Llamamos a la función 'enroll_person' pasando el nombre de la persona y el número de muestras (40)
