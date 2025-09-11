## Proyecto de Reconocimiento Facial

Por medio de OpenCv y el algoritmo LBPH podemos enrolar personas, entrenar el modelo y reconocer rostros.

## Requisitos

- Python 3.7 o superior

Las siguientes librerías de Python:
- numpy==2.2.6
- opencv-contrib-python==4.12.0.88
- opencv-python==4.12.0.88

El archivo requirements.txt incluye las dependencias citadas anteriormente.

## Uso
1. Abra la terminal en la ruta en la cual se encuentra este README.

1. Enrolar una persona
2. Ejecute el comando: python enrolar_persona.py
3. Ingrese el nombre de la persona. Luego, la cámara se abrirá y comenzará a capturar imágenes. El número de imágenes que se capturarán por persona es 40, aunque es modificable en el codigo.
4. Ejecute el comando: python entrenar_modelo.py - Este comando procesará todas las imágenes capturadas y entrenará el modelo LBPH. Después de entrenar el modelo, se guardará en el archivo model_lbph.yml y las etiquetas de las personas se guardarán en labels.json.
5. Ejecute el comando: python reconocimiento.py - Este script abrirá la cámara, detectará las caras y realizará el reconocimiento facial. Si la persona es reconocida, se mostrará su nombre y si es autorizada o no, dependiendo de las configuraciones.

## Notas
- Si deseas borrar las imágenes de una persona previamente registrada, puedes hacerlo eliminando la carpeta correspondiente dentro de data/.