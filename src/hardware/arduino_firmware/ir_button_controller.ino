/*
 * Firmware para Arduino Nano - Control IR y Botón Físico
 * 
 * Hardware:
 * - LED IR conectado al pin D3 (con resistencia 220Ω)
 * - Botón físico conectado al pin D2 (con resistencia pull-down o usando INPUT_PULLUP)
 * 
 * Protocolo Serial:
 * - Envía "BUTTON_PRESSED" o "BUTTON_RELEASED" al PC
 * - Recibe comandos "IR:COMANDO" para emitir señales IR
 */

#include <Arduino.h>

// Pines
const int PIN_IR_LED = 3;      // Pin PWM para el LED IR
const int PIN_BUTTON = 2;      // Pin para el botón físico

// Estado del botón
bool lastButtonState = LOW;
unsigned long lastDebounceTime = 0;
const unsigned long debounceDelay = 50;  // 50ms para evitar rebotes

// Buffer de entrada serial
String inputBuffer = "";

void setup() {
  // Inicializar serial
  Serial.begin(9600);
  while (!Serial) {
    ; // Esperar conexión serial (necesario para algunos boards)
  }

  // Configurar pines
  pinMode(PIN_IR_LED, OUTPUT);
  pinMode(PIN_BUTTON, INPUT_PULLUP);  // Usar resistencia interna pull-up
  
  // Estado inicial
  digitalWrite(PIN_IR_LED, LOW);
  
  Serial.println("Arduino listo - Sistema IR + Botón");
}

void loop() {
  // 1. Leer estado del botón
  readButton();
  
  // 2. Procesar comandos seriales entrantes
  processSerialCommands();
  
  delay(10);  // Pequeña pausa para estabilidad
}

void readButton() {
  static bool buttonPressedNotified = false;
  
  int reading = digitalRead(PIN_BUTTON);
  
  // Invertir lógica porque usamos INPUT_PULLUP (LOW = pulsado)
  bool currentState = (reading == LOW) ? HIGH : LOW;
  
  // Detectar cambio de estado
  if (currentState != lastButtonState) {
    lastDebounceTime = millis();  // Resetear temporizador de debounce
  }
  
  // Si ha pasado el tiempo de debounce
  if ((millis() - lastDebounceTime) > debounceDelay) {
    // Detectar flanco de subida (pulsación)
    if (currentState == HIGH && !buttonPressedNotified) {
      Serial.println("BUTTON_PRESSED");
      buttonPressedNotified = true;
    }
    
    // Detectar flanco de bajada (soltar)
    if (currentState == LOW && buttonPressedNotified) {
      Serial.println("BUTTON_RELEASED");
      buttonPressedNotified = false;
    }
  }
  
  lastButtonState = currentState;
}

void processSerialCommands() {
  while (Serial.available() > 0) {
    char inChar = (char)Serial.read();
    
    // Si es newline, procesar el comando
    if (inChar == '\n') {
      inputBuffer.trim();
      executeCommand(inputBuffer);
      inputBuffer = "";
    } else {
      inputBuffer += inChar;
    }
  }
}

void executeCommand(String command) {
  // Formato esperado: "IR:COMANDO"
  if (command.startsWith("IR:")) {
    String irCode = command.substring(3);
    irCode.trim();
    
    Serial.print("Ejecutando IR: ");
    Serial.println(irCode);
    
    // Emitir señal IR según el comando
    emitIRSignal(irCode);
  }
}

void emitIRSignal(String code) {
  // Simulación de emisión IR (aquí iría la librería IRremote si se usa)
  // Para este ejemplo, hacemos un parpadeo del LED como feedback
  
  digitalWrite(PIN_IR_LED, HIGH);
  delay(100);
  digitalWrite(PIN_IR_LED, LOW);
  delay(100);
  digitalWrite(PIN_IR_LED, HIGH);
  delay(100);
  digitalWrite(PIN_IR_LED, LOW);
  
  // NOTA: Para producción, usar la librería IRremote para generar
  // las frecuencias correctas (38kHz) y los códigos específicos de tu TV
  // Ejemplo con IRremote:
  // if (code == "POWER") { IrSender.sendNEC(0x04FB55AA, 32); }
  // if (code == "MUTE") { IrSender.sendNEC(0x04FB45BA, 32); }
  // etc.
}
