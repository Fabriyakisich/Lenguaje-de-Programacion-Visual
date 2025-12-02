# Export Results API — Compartir modelo FRT a otra PC

Este módulo permite que **otra PC en la red** descargue:

- modelo LBPH (`model_lbph.yml`)
- labels (`labels.json`)
- datos de personas (desde la BD)
- las fotos de las caras

Siempre se baja todo a una carpeta `data/` **limpia** (se borra antes de cada sync).

---

## Instalación

Desde la raíz del proyecto:

```bash
pip install -r ../requirements.txt
```
Para iniciar el servidor, desde Export_Results_API

```Python
python server.py --port 9000
```

Se debe visualizar un mensaje en la terminal como sigue:
🚀 SERVIDOR FRT EXPORT API
...
⏳ Iniciando servidor en 0.0.0.0:9000...
.
.
.
INFO:     Uvicorn running on http://0.0.0.0:9000

Para apagar el servidor, se presiona Ctrl + C dos veces
