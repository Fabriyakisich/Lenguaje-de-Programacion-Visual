# app.py (Servidor Flask con Video en Vivo y Reconocimiento)

from flask import Flask, jsonify, Response
import cv2
import subprocess
import json
from pathlib import Path

app = Flask(__name__)

# Rutas de los modelos y etiquetas
MODEL_PATH = Path("model_lbph.yml")
LABELS_PATH = Path("labels.json")
FACE_SIZE = (200, 200)
THRESHOLD = 60.0

# Cargar el modelo y las etiquetas
def load_model():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(str(MODEL_PATH))
    label_to_name = json.loads(LABELS_PATH.read_text(encoding="utf-8"))
    return recognizer, label_to_name

# Abrir la cámara
cap = cv2.VideoCapture(0)

# Función para generar el video en tiempo real
def generate_frames():
    while True:
        success, frame = cap.read()  # Leemos un fotograma de la cámara
        if not success:
            break
        else:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            face, coords = detect_face(gray)

            if face is not None:  # Solo procesamos la cara si se detecta una
                x, y, w, h = coords  # Desempaquetamos las coordenadas
                recognizer, label_to_name = load_model()
                face_norm = cv2.equalizeHist(cv2.resize(face, FACE_SIZE))
                label, conf = recognizer.predict(face_norm)
                name = label_to_name.get(str(label), "Desconocido")
                is_auth = conf < THRESHOLD

                # Emitir el estado de autorización
                if is_auth:
                    auth_status = f"{name} (Autorizado)"
                    color = (0, 255, 0)  # Verde para autorizado
                else:
                    auth_status = "No autorizado"
                    color = (0, 0, 255)  # Rojo para no autorizado
                
                cv2.putText(frame, auth_status, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

            # Codificar el fotograma en JPEG y enviarlo como flujo MJPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# Ruta para transmitir el video en vivo
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Función para detectar las caras en la imagen
def detect_face(gray):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    if len(faces) == 0:
        return None, None  # Si no se detectan caras, devolvemos None
    x, y, w, h = max(faces, key=lambda r: r[2] * r[3])
    return gray[y:y+h, x:x+w], (x, y, w, h)  # Devolvemos la cara recortada y las coordenadas

# Ruta para ejecutar el reconocimiento y determinar si la persona está autorizada
@app.route('/reconocimiento', methods=['POST'])
def reconocimiento():
    try:
        result = subprocess.run(['python', 'reconocimiento.py'], capture_output=True, text=True)

        # Si la salida contiene 'True', la persona está autorizada
        if "True" in result.stdout:
            return jsonify({"authorized": True, "message": "Acceso permitido"}), 200
        else:
            return jsonify({"authorized": False, "message": "Acceso denegado"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)  # Ejecuta el servidor en el puerto 5000
