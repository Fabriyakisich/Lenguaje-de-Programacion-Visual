#include <Arduino.h>

// Definición de los pines de conexión del motor
const int motorPin1 = 8;
const int motorPin2 = 9;
const int motorPin3 = 10;
const int motorPin4 = 11;
char value = 0; // Variable para almacenar el valor leído desde el puerto serial

// Definición de los pindes de habilitación
const int enablePinA = 13;  // abrir puerta ( '1' para abrir)
const int puertaCerradaPin = 12; // cerrar puerta ( '0' para cerrar)
int abierto = 0; // Variable para rastrear el estado de la puerta // 0 cerrada, 1 abierta

// Número de pasos por revolución (aproximadamente 4096 para este motor)
const int pasosPorRevolucion = 4096;

// Variable para elegir la dirección
// Puede ser "1" para sentido horario (clockwise) o "-1" para sentido antihorario (counterclockwise)
int direccion = 1;  // 1 = horario, -1 = antihorario

// Declaración de funciones
void girarMotor(int grados);  // Función para girar el motor
void pasoHorario();           // Función para un paso en sentido horario
void pasoAntihorario();       // Función para un paso en sentido antihorario

void setup() {
   // Iniciar comunicación serial a 9600 baudios
  Serial.begin(9600);
  pinMode(enablePinA, OUTPUT);
  pinMode(puertaCerradaPin, INPUT);
  // Configuración de los pines como salida
  pinMode(motorPin1, OUTPUT);
  pinMode(motorPin2, OUTPUT);
  pinMode(motorPin3, OUTPUT);
  pinMode(motorPin4, OUTPUT);
}

void loop() {
  //girarMotor(90);  // Girar el motor 90 grados en la dirección establecida
  // Verificar si hay datos disponibles en el puerto serial
  if (Serial.available() > 0) {
    // Leer el valor enviado por serial
    value = Serial.read();  // Leer un byte (carácter)
    Serial.print(value);  // Enviar de vuelta el valor leído para confirmación
    Serial.print(abierto);
  }

    // Si el valor es '1', prender el LED
    if ((value == '1') and (abierto == 0)) {
      Serial.println("Abriendo puerta...");
      digitalWrite(enablePinA, HIGH);  // Encender el LED
      direccion = -1;           // Establecer dirección antihoraria
      girarMotor(90);
      delay(1000);  // Pausa de 1 segundo antes de repetir el proceso
      abierto = 1;
    } else {
      digitalWrite(enablePinA, LOW);   // Apagar el LED
    }
  if ((digitalRead(puertaCerradaPin) == HIGH) and (abierto == 1)) {
    direccion = 1;            // Establecer dirección horaria
    girarMotor(90);
    delay(1000);  // Pausa de 1 segundo antes de repetir el proceso
    abierto = 0;
  }
  
}

void girarMotor(int grados) {
  // Calcular el número de pasos necesarios para mover el motor 180°
  int pasosParaGirar = map(grados, 0, 360, 0, pasosPorRevolucion / 2);

  // Realizar el giro
  for (int i = 0; i < pasosParaGirar/4; i++) {
    // Enviar la secuencia de pasos para el motor
    if (direccion == 1) {
      // Sentido horario
      pasoHorario();
    } else {
      // Sentido antihorario
      pasoAntihorario();
    }
  }
}

void pasoHorario() {
  // Secuencia de pasos para el sentido horario
  digitalWrite(motorPin1, HIGH);
  digitalWrite(motorPin2, LOW);
  digitalWrite(motorPin3, LOW);
  digitalWrite(motorPin4, LOW);
  delay(10);

  digitalWrite(motorPin1, LOW);
  digitalWrite(motorPin2, HIGH);
  digitalWrite(motorPin3, LOW);
  digitalWrite(motorPin4, LOW);
  delay(10);

  digitalWrite(motorPin1, LOW);
  digitalWrite(motorPin2, LOW);
  digitalWrite(motorPin3, HIGH);
  digitalWrite(motorPin4, LOW);
  delay(10);

  digitalWrite(motorPin1, LOW);
  digitalWrite(motorPin2, LOW);
  digitalWrite(motorPin3, LOW);
  digitalWrite(motorPin4, HIGH);
  delay(10);
}

void pasoAntihorario() {
  // Secuencia de pasos para el sentido antihorario
  digitalWrite(motorPin1, LOW);
  digitalWrite(motorPin2, LOW);
  digitalWrite(motorPin3, LOW);
  digitalWrite(motorPin4, HIGH);
  delay(10);

  digitalWrite(motorPin1, LOW);
  digitalWrite(motorPin2, LOW);
  digitalWrite(motorPin3, HIGH);
  digitalWrite(motorPin4, LOW);
  delay(10);

  digitalWrite(motorPin1, LOW);
  digitalWrite(motorPin2, HIGH);
  digitalWrite(motorPin3, LOW);
  digitalWrite(motorPin4, LOW);
  delay(10);

  digitalWrite(motorPin1, HIGH);
  digitalWrite(motorPin2, LOW);
  digitalWrite(motorPin3, LOW);
  digitalWrite(motorPin4, LOW);
  delay(10);
}
