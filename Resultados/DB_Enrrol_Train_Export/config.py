import os

# Proyecto raíz (este archivo está en la raíz del proyecto)
PROJECT_ROOT = os.path.dirname(__file__)

# Directorios principales
GUI_DB_DIR = os.path.join(PROJECT_ROOT, 'GUI_DataBase')
FRT_DIR = os.path.join(PROJECT_ROOT, 'FRT')

# Rutas útiles
DB_PATH = os.path.join(GUI_DB_DIR, 'personas.db')
FACES_DIR = os.path.join(GUI_DB_DIR, 'faces')
MODEL_DIR = os.path.join(FRT_DIR, 'model')
MODEL_PATH = os.path.join(MODEL_DIR, 'model_lbph.yml')
LABELS_PATH = os.path.join(MODEL_DIR, 'labels.json')

# Asegurar que las carpetas existan
os.makedirs(GUI_DB_DIR, exist_ok=True)
os.makedirs(FACES_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)
