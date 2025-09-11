import cv2, os, time, argparse, glob, json
import numpy as np
from pathlib import Path

# ------------------------ Config ------------------------
DATA_ROOT = Path("data")            # dentro de aquí van data/<persona>/
MODEL_PATH = Path("model_lbph.yml") # modelo entrenado
LABELS_PATH = Path("labels.json")   # mapea label -> nombre
ALLOW_PATH = Path("authorized.txt") # lista de nombres autorizados (uno por línea)
FACE_SIZE = (200, 200)
SAMPLES = 40
THRESHOLD = 60.0  # LBPH: menor = más parecido (ajustar 45-75)


# --------------------- CLI ---------------------
p = argparse.ArgumentParser()
p.add_argument("--enroll", type=str, default=None, help="Captura muestras para la persona dada (ej: --enroll Juan)")
p.add_argument("--samples", type=int, default=SAMPLES, help=f"Cantidad de muestras a capturar (default {SAMPLES})")
p.add_argument("--train", action="store_true", help="Entrena el modelo con todas las carpetas en data/*")
p.add_argument("--allow", nargs="*", help="Define lista de personas autorizadas (sobrescribe authorized.txt)")
p.add_argument("--reset_person", action="store_true", help="Borra muestras previas de la persona indicada en --enroll")
args = p.parse_args()

# --------------------- Detector ---------------------
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

def detect_face(gray):
    faces = face_cascade.detectMultiScale(gray, 1.2, 5, minSize=(60,60))
    if len(faces) == 0:
        return None
    x,y,w,h = max(faces, key=lambda r: r[2]*r[3])
    return gray[y:y+h, x:x+w], (x,y,w,h)

def ensure_dir(d: Path):
    d.mkdir(parents=True, exist_ok=True)

def load_authorized_set():
    if not ALLOW_PATH.exists():
        return set()
    names = [line.strip() for line in ALLOW_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    return set(names)

def save_authorized_set(names):
    ALLOW_PATH.write_text("\n".join(sorted(set(names))), encoding="utf-8")

def list_people():
    ensure_dir(DATA_ROOT)
    return sorted([p.name for p in DATA_ROOT.iterdir() if p.is_dir()])

# --------------------- ENROLL ---------------------
def enroll_person(person_name: str, n_samples: int, reset: bool):
    person_dir = DATA_ROOT / person_name
    ensure_dir(person_dir)
    if reset:
        for f in person_dir.glob("*.png"):
            f.unlink()

    cap = cv2.VideoCapture(0)  # en Windows: cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    if not cap.isOpened():
        raise RuntimeError("No pude abrir la cámara.")

    count = 0
    taken = 0
    print(f"Enrolando a {person_name}… mirá a la cámara. (q = salir)")

    while taken < n_samples:
        ok, frame = cap.read()
        if not ok:
            print("No pude leer frame de la cámara.")
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        res = detect_face(gray)

        if res is not None:
            face, rect = res
            face_norm = cv2.equalizeHist(cv2.resize(face, FACE_SIZE))
            cv2.imshow(f"Enrolando {person_name}", face_norm)

            # guardar una cada 3 iteraciones para tener variación
            if count % 3 == 0:
                fname = person_dir / f"{person_name}_{int(time.time())}_{taken:03d}.png"
                cv2.imwrite(str(fname), face_norm)
                taken += 1
                print(f"[+] ({taken}/{n_samples}) {fname.name}")
        else:
            cv2.imshow(f"Enrolando {person_name}", frame)

        count += 1
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Cancelado por el usuario.")
            break

    cap.release()
    cv2.destroyAllWindows()
    print(f"[OK] Enrolamiento de {person_name} terminado con {taken} muestras.")

# --------------------- TRAIN ---------------------
def train_all():
    people = list_people()
    if not people:
        print("No hay carpetas en data/. Enrolá primero con --enroll NOMBRE.")
        return False

    images, labels = [], []
    name_to_label = {}
    label_to_name = {}
    next_label = 1

    for name in people:
        person_dir = DATA_ROOT / name
        files = sorted([*person_dir.glob("*.png")])
        if not files:
            continue
        if name not in name_to_label:
            name_to_label[name] = next_label
            label_to_name[next_label] = name
            next_label += 1
        lab = name_to_label[name]

        for f in files:
            img = cv2.imread(str(f), cv2.IMREAD_GRAYSCALE)
            if img is None:
                continue
            images.append(img)
            labels.append(lab)

    if not images:
        print("No hay imágenes para entrenar.")
        return False

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.train(images, np.array(labels))
    recognizer.save(str(MODEL_PATH))
    LABELS_PATH.write_text(json.dumps(label_to_name, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[OK] Modelo guardado en {MODEL_PATH}")
    print(f"[OK] Labels guardados en {LABELS_PATH}")
    print("Personas incluidas:", ", ".join(people))
    return True

# --------------------- RECOGNIZE ---------------------
def recognize_loop():
    if not MODEL_PATH.exists() or not LABELS_PATH.exists():
        raise RuntimeError("Falta el modelo o labels. Corré --train primero.")

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(str(MODEL_PATH))
    label_to_name = json.loads(LABELS_PATH.read_text(encoding="utf-8"))
    authorized = load_authorized_set()

    cap = cv2.VideoCapture(0)  # en Windows: cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    if not cap.isOpened():
        raise RuntimeError("No pude abrir la cámara.")

    print("Reconociendo… (q = salir)")
    last_msg_until = 0
    last_text = "Esperando…"

    while True:
        ok, frame = cap.read()
        if not ok:
            print("No pude leer frame.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        res = detect_face(gray)

        if res is not None:
            face, (x,y,w,h) = res
            face_norm = cv2.equalizeHist(cv2.resize(face, FACE_SIZE))
            label, conf = recognizer.predict(face_norm)
            name = label_to_name.get(str(label), "Desconocido")

            is_auth = (name in authorized) and (conf < THRESHOLD)
            now = time.time()
            if now > last_msg_until:
                last_text = (f"ACCESO ACEPTADO: {name}" if is_auth
                             else f"ACCESO RECHAZADO: {name} (conf:{conf:.1f})")
                last_msg_until = now + 2.0

            color = (0,255,0) if "ACEPTADO" in last_text else (0,0,255)
            cv2.rectangle(frame, (x,y), (x+w,y+h), color, 2)
            cv2.putText(frame, last_text, (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        else:
            cv2.putText(frame, "Buscando rostro…", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)

        cv2.imshow("Acceso por rostro (multiusuario)", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# --------------------- MAIN ---------------------
if __name__ == "__main__":
    ensure_dir(DATA_ROOT)

    if args.allow is not None:
        save_authorized_set(args.allow)
        print(f"[OK] Autorizados: {', '.join(load_authorized_set())}")

    if args.enroll:
        enroll_person(args.enroll, args.samples, args.reset_person)

    if args.train:
        trained = train_all()
        if not trained:
            raise SystemExit(1)

    if not args.enroll and not args.train and args.allow is None:
        # correr reconocimiento
        recognize_loop()
