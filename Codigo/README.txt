TODO SE PONE EN LA TERMINAL
0. pip install opencv-contrib-python
1. Enrolar a la primera persona, ej: python acceso_face_multi.py --enroll "Fabrizzio" --samples 40
2. Para poner mas personas se hace lo mismo que el paso 1
3. Entrenar el modelo con python acceso_face_multi.py --train
4. Se definen las personas autorizadas con python acceso_face_multi.py --allow Fabrizzio Judith Bianchini
5. Se debe poner el mismo nombre que se utilizo en el paso 1, en el paso 4 se separan los nombres para poner los distintos accesos
5. Correr el programa acceso_face_multi.py