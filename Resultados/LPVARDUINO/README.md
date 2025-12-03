Control de Motor Paso a Paso para Sistema de Apertura de Puerta

Este proyecto implementa el control de un motor paso a paso 28BYJ-48 con su módulo de potencia ULN2003 para manejar la apertura y cierre de una puerta. El sistema recibe comandos mediante comunicación Serial y utiliza un sensor digital para detectar cuándo la puerta está cerrada.

El archivo principal del proyecto es:
main.cpp

Funcionalidad General

El programa permite:

    - Abrir la puerta cuando se recibe el comando '1' por Serial.

    - Cerrar la puerta automáticamente cuando el sensor detecta que se ha cerrado físicamente.

    - Controlar el motor paso a paso en ambas direcciones (horario y antihorario).

    - Evitar comandos repetidos gracias a una variable de estado llamada abierto.

Estructura del archivo:

main.cpp
├── setup()                 # Configura Serial y pines
├── loop()                  # Lógica principal: abrir/cerrar puerta
├── girarMotor(grados)      # Traduce grados a pasos y ejecuta el giro
├── pasoHorario()           # Secuencia de pasos para girar en sentido horario
└── pasoAntihorario()       # Secuencia de pasos para girar en sentido antihorario

Pines Utilizados:
| Pin Arduino  | Función                             |
| ------------ | ----------------------------------- |
| 8, 9, 10, 11 | Bobinas del motor paso a paso       |
| 13           | Señal de habilitación para apertura |
| 12           | Sensor digital de puerta cerrada    |
| RX/TX        | Comunicación Serial                 |


