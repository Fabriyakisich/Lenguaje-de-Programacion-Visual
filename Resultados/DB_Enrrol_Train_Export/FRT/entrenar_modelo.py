# Entrenamiento: usar rutas desde config y mapear label -> person_id
import cv2
import numpy as np
import json
from pathlib import Path
from config import FACES_DIR, MODEL_PATH, LABELS_PATH


def list_people():
    root = Path(FACES_DIR)
    if not root.exists():
        return []
    return sorted([p.name for p in root.iterdir() if p.is_dir()])


def train_model():
    people = list_people()
    if not people:
        print("No hay carpetas en faces/. Enrolá primero.")
        return False

    images, labels = [], []
    person_to_label = {}
    label_to_person = {}
    next_label = 1

    # Si ya existe un labels.json previo, cargar mapping (label -> person_id)
    labels_path = Path(LABELS_PATH)
    if labels_path.exists():
        label_to_person = json.loads(labels_path.read_text(encoding="utf-8"))
        label_to_person = {int(k): v for k, v in label_to_person.items()}
        person_to_label = {v: k for k, v in label_to_person.items()}
        if person_to_label:
            next_label = max(person_to_label.values()) + 1

    from pathlib import Path as _P
    for person_id in people:
        person_dir = _P(FACES_DIR) / person_id
        files = sorted([*person_dir.glob("*.png")])
        if not files:
            continue

        if person_id not in person_to_label:
            person_to_label[person_id] = next_label
            label_to_person[next_label] = person_id
            next_label += 1

        lab = person_to_label[person_id]

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

    Path(MODEL_PATH).parent.mkdir(parents=True, exist_ok=True)
    recognizer.save(str(MODEL_PATH))

    # Guardar label -> person_id (keys como strings en JSON)
    with open(LABELS_PATH, 'w', encoding='utf-8') as fh:
        json.dump({str(k): v for k, v in label_to_person.items()}, fh, ensure_ascii=False, indent=2)

    print(f"[OK] Modelo guardado en {MODEL_PATH}")
    print(f"[OK] Labels guardados en {LABELS_PATH}")
    return True


if __name__ == "__main__":
    trained = train_model()
    if not trained:
        raise SystemExit(1)
