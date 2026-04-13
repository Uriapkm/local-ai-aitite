# 📘 Manual Completo de Instalación y Puesta en Marcha - Abuelo Agent

## Guía Paso a Paso desde Cero (Hardware + Software)

**Versión:** 1.0  
**Última actualización:** Abril 2025  
**Sistema Operativo:** Bazzite Linux (recomendado) / Fedora / Ubuntu 22.04+

---

## 📑 ÍNDICE

1. [Preparación Previa](#1-preparación-previa)
2. [Instalación del Hardware](#2-instalación-del-hardware)
3. [Programación del Arduino](#3-programación-del-arduino)
4. [Instalación del Sistema Operativo](#4-instalación-del-sistema-operativo)
5. [Instalación del Software Abuelo Agent](#5-instalación-del-software-abuelo-agent)
6. [Configuración del Sistema](#6-configuración-del-sistema)
7. [Descarga de Modelos de IA](#7-descarga-de-modelos-de-ia)
8. [Configuración de Códigos IR](#8-configuración-de-códigos-ir)
9. [Pruebas y Verificación](#9-pruebas-y-verificación)
10. [Uso Diario](#10-uso-diario)
11. [Solución de Problemas](#11-solución-de-problemas)
12. [Mantenimiento](#12-mantenimiento)

---

## 1. PREPARACIÓN PREVIA

### 1.1 Verificar Requisitos

Antes de comenzar, asegúrate de tener:

#### Hardware
- [ ] Computadora con AMD BC250 o equivalente (ver `HARDWARE_RESUMEN_EXHAUSTIVO.md`)
- [ ] Arduino Nano (original o clon)
- [ ] LED infrarrojo 940nm
- [ ] Resistencia 220Ω
- [ ] Botón pulsador
- [ ] Cables jumper
- [ ] Webcam USB (opcional pero recomendado)
- [ ] Cable USB para Arduino

#### Herramientas
- [ ] Cautín y estaño
- [ ] Computadora con acceso a internet
- [ ] Memoria USB de 8GB mínimo (para instalar SO)
- [ ] Destornilladores
- [ ] Multímetro (opcional)

#### Software
- [ ] Cuenta de GitHub (para clonar el repositorio)
- [ ] 30-60 minutos de tiempo libre
- [ ] Paciencia y atención al detalle

### 1.2 Descargar Recursos Necesarios

```bash
# En tu computadora principal (no en la del proyecto aún)
# Descargar:
1. Arduino IDE: https://www.arduino.cc/en/software
2. Imagen de Bazzite: https://bazzite.gg/
3. BalenaEtcher: https://www.balena.io/etcher/ (para crear USB booteable)
```

---

## 2. INSTALACIÓN DEL HARDWARE

### 2.1 Ensamblar Circuito Arduino

#### Paso 1: Preparar componentes
1. Identifica los pines del Arduino Nano
2. Identifica el ánodo (+) y cátodo (-) del LED IR
   - **Ánodo**: pata más larga
   - **Cátodo**: pata más corta o lado plano del LED

#### Paso 2: Soldar LED IR
```
1. Toma la resistencia 220Ω
2. Suelda un extremo al pin D3 del Arduino
3. Suelda el otro extremo al ánodo (+) del LED IR
4. Suelda un cable desde el cátodo (-) del LED al pin GND del Arduino
```

#### Paso 3: Conectar botón físico
```
1. Suelda un cable desde el pin D2 del Arduino a una terminal del botón
2. Suelda otro cable desde la otra terminal del botón a GND
3. No se necesita resistencia externa (usaremos INPUT_PULLUP interno)
```

#### Paso 4: Verificar conexiones
```
✓ Pin D3 → Resistencia 220Ω → LED IR (+) → LED IR (-) → GND
✓ Pin D2 → Botón Terminal 1 → Botón Terminal 2 → GND
✓ Pin 5V → (solo si usas módulo IR externo)
✓ Pin GND → Múltiples conexiones a tierra
```

#### Paso 5: Aislar conexiones
1. Usa cinta termocontraíble en todas las soldaduras expuestas
2. Asegura los cables con silicona caliente o cinta aislante
3. Verifica que no haya cortocircuitos

### 2.2 Montaje Físico

#### Opción A: Protoboard (Recomendado para pruebas)
1. Inserta Arduino Nano en la protoboard
2. Conecta componentes según diagrama
3. Fácil de modificar y depurar

#### Opción B: PCB perforada (Más permanente)
1. Solda componentes directamente a PCB
2. Más robusto y compacto
3. Requiere más habilidad

#### Opción C: Caja personalizada
1. Imprime en 3D una caja o usa una existente
2. Perfora agujeros para LED IR y botón
3. Monta Arduino con tornillos o silicona

### 2.3 Posicionamiento del LED IR

**Importante:** El LED IR debe apuntar directamente al sensor IR del TV.

1. **Ubica el sensor IR del TV**: Generalmente está en la parte inferior central
2. **Posiciona el Arduino**: 
   - Cerca del TV (1-3 metros máximo)
   - LED apuntando directamente al sensor
   - Sin obstáculos en medio
3. **Prueba de alcance**:
   - Desde la posición elegida, apunta con el control remoto del TV
   - Si funciona, el LED IR también debería funcionar

---

## 3. PROGRAMACIÓN DEL ARDUINO

### 3.1 Instalar Arduino IDE

#### En Linux (computadora de desarrollo)
```bash
# Método 1: Desde Snap (Ubuntu/Debian)
sudo snap install arduino --classic

# Método 2: Descarga manual
cd ~/Downloads
wget https://downloads.arduino.cc/arduino-ide/arduino-ide_2.3.2_Linux_64bit.AppImage
chmod +x arduino-ide_*.AppImage
./arduino-ide_*.AppImage
```

#### En Windows
1. Descarga desde https://www.arduino.cc/en/software
2. Ejecuta el instalador
3. Sigue el asistente de instalación

#### En macOS
1. Descarga desde Mac App Store o sitio web
2. Arrastra Arduino IDE a Aplicaciones

### 3.2 Configurar Arduino IDE

1. **Abrir Arduino IDE**
2. **Instalar drivers CH340** (si usas clon chino):
   - Windows: https://sparks.gogo.co.nz/ch340.html
   - Linux: Ya incluidos en kernel moderno
   - macOS: https://github.com/adrianmihalcu/ch340g-ch34g-ch34x-mac-os-x-driver

3. **Verificar conexión**:
   ```
   Herramientas → Puerto → Seleccionar /dev/ttyUSB0 (Linux) o COM3 (Windows)
   Herramientas → Placa → Arduino Nano
   ```

### 3.3 Cargar Firmware

1. **Abrir el sketch**:
   ```
   Archivo → Abrir
   Navegar a: /workspace/src/hardware/arduino_firmware/ir_button_controller.ino
   ```

2. **Verificar código**:
   ```cpp
   // Asegúrate que los pines coincidan con tu hardware
   const int PIN_IR_LED = 3;      // Debe ser D3
   const int PIN_BUTTON = 2;      // Debe ser D2
   ```

3. **Compilar**:
   ```
   Sketch → Verificar Compilar (Ctrl+R)
   ```
   Espera a que diga "Compilación terminada"

4. **Subir al Arduino**:
   ```
   Sketch → Subir (Ctrl+U)
   ```
   - Las luces TX/RX del Arduino parpadearán
   - Espera mensaje "Subida completada"

5. **Verificar funcionamiento**:
   ```
   Herramientas → Monitor Serie
   Velocidad: 9600 baud
   ```
   Deberías ver: `Arduino listo - Sistema IR + Botón`

### 3.4 Probar Firmware

#### Prueba 1: Botón
1. Abre Monitor Serie (9600 baud)
2. Presiona el botón físico
3. Deberías ver: `BUTTON_PRESSED`
4. Suelta el botón
5. Deberías ver: `BUTTON_RELEASED`

#### Prueba 2: LED IR
1. Envía comando desde Monitor Serie: `IR:POWER`
2. El LED IR debería parpadear 3 veces
3. **Nota**: El parpadeo es visible con cámara de celular (la luz IR es invisible al ojo humano)

---

## 4. INSTALACIÓN DEL SISTEMA OPERATIVO

### 4.1 Por qué Bazzite Linux

**Bazzite** es una distribución basada en Fedora optimizada para:
- ✅ Juegos y multimedia
- ✅ Hardware AMD (drivers incluidos)
- ✅ Vulkan (aceleración IA)
- ✅ Actualizaciones atómicas (más estable)
- ✅ Contenedores (mejor aislamiento)

### 4.2 Crear USB Booteable

1. **Descargar imagen ISO**:
   ```bash
   # Ir a https://bazzite.gg/
   # Descargar: Bazzite Desktop (AMD/Intel)
   ```

2. **Crear USB con BalenaEtcher**:
   ```
   1. Insertar USB de 8GB+
   2. Abrir BalenaEtcher
   3. Seleccionar imagen ISO descargada
   4. Seleccionar unidad USB
   5. Click en "Flash!"
   6. Esperar a que termine (10-15 min)
   ```

3. **Verificar USB**:
   - El USB debería llamarse "Bazzite"
   - Tamaño usado: ~4GB

### 4.3 Instalar Bazzite

1. **Bootear desde USB**:
   ```
   1. Insertar USB en la computadora objetivo
   2. Encender y presionar F12/F2/Del (depende de la placa)
   3. Seleccionar USB desde menú de boot
   4. Elegir "Start Bazzite Live"
   ```

2. **Probar modo Live** (opcional pero recomendado):
   ```
   - Verificar que todo funcione (WiFi, audio, video)
   - Conectar Arduino y verificar que sea detectado
   ```

3. **Instalar en disco**:
   ```
   1. Click en icono "Install to Hard Drive"
   2. Seleccionar disco de destino (se borrará todo!)
   3. Configurar usuario y contraseña
   4. Elegir zona horaria
   5. Click en "Install"
   6. Esperar 10-20 minutos
   7. Reiniciar y retirar USB
   ```

4. **Primer boot**:
   ```
   1. Ingresar usuario y contraseña
   2. Actualizar sistema cuando se solicite
   3. Configurar WiFi si es necesario
   ```

### 4.4 Post-Instalación

```bash
# Actualizar sistema
sudo dnf upgrade --refresh -y

# Habilitar repositorios adicionales
sudo dnf install -y fedora-workstation-repositories

# Instalar herramientas básicas
sudo dnf install -y git curl wget vim htop
```

---

## 5. INSTALACIÓN DEL SOFTWARE ABUELO AGENT

### 5.1 Clonar Repositorio

```bash
# Abrir terminal
cd ~

# Clonar repositorio (ajusta la URL si es local)
git clone https://github.com/tu-usuario/abuelo-agent.git
# O si ya tienes los archivos:
# cd /workspace

# Entrar al directorio
cd abuelo-agent
```

### 5.2 Ejecutar Script de Instalación

```bash
# Dar permisos de ejecución
chmod +x scripts/install_gemma4_bazzite.sh

# Ejecutar instalación
./scripts/install_gemma4_bazzite.sh
```

**El script hará automáticamente:**
1. ✅ Actualiza el sistema
2. ✅ Instala dependencias (Python, Ollama, Vulkan, etc.)
3. ✅ Crea entorno virtual Python
4. ✅ Instala paquetes Python requeridos
5. ✅ Descarga modelo Gemma 4
6. ✅ Configura permisos de usuario

### 5.3 Instalación Manual (Alternativa)

Si prefieres instalar paso a paso:

#### Paso 1: Instalar dependencias del sistema
```bash
sudo dnf install -y python3 python3-pip git curl wget \
    portaudio-devel libsndfile-devel ffmpeg \
    vulkan-loader vulkan-tools mesa-vulkan-drivers \
    ollama arduino-core
```

#### Paso 2: Configurar Python
```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno
source venv/bin/activate

# Actualizar pip
pip install --upgrade pip
```

#### Paso 3: Instalar paquetes Python
```bash
# Crear requirements.txt si no existe
cat > requirements.txt << EOF
faster-whisper>=0.10.0
edge-tts>=6.1.0
pyserial>=3.5
pyyaml>=6.0
opencv-python>=4.8.0
numpy>=1.24.0
requests>=2.31.0
selenium>=4.15.0
pyautogui>=0.9.54
EOF

# Instalar paquetes
pip install -r requirements.txt
```

#### Paso 4: Instalar Ollama
```bash
# Descargar e instalar Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Iniciar servicio
sudo systemctl enable ollama
sudo systemctl start ollama
```

---

## 6. CONFIGURACIÓN DEL SISTEMA

### 6.1 Copiar Archivos de Configuración

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Verificar estructura de directorios
mkdir -p data logs
```

### 6.2 Detectar Puerto Arduino

```bash
# Listar dispositivos seriales
ls /dev/ttyUSB* /dev/ttyACM*

# Deberías ver algo como:
# /dev/ttyUSB0  (para Arduino con chip CH340)
# o
# /dev/ttyACM0  (para Arduino original)
```

### 6.3 Editar Configuración

```bash
# Abrir archivo de configuración
nano config/settings.yaml
```

**Configuración recomendada:**

```yaml
# Configuración - Abuelo IA

arduino:
  port: "/dev/ttyUSB0"        # ⚠️ CAMBIAR según tu puerto
  baud_rate: 9600
  button_pin: 2
  ir_led_pin: 3

audio:
  whisper_model: "small"      # small, base, medium
  whisper_language: "es"
  piper_voice: "es_ES-carlfm-medium"

llm:
  model: "gemma4:4b-instruct-q4_K_M"
  context_length: 128000
  temperature: 0.7
  use_vulkan: true            # Importante para AMD

vision:
  enabled: true               # false si no hay cámara
  camera_index: 0

tv:
  brand: "Samsung"            # Tu marca de TV
  pc_hdmi_port: "HDMI1"       # Puerto donde está conectado el PC

youtube:
  browser: "brave"            # brave, chrome, chromium

memory:
  enabled: true
  max_conversation_history: 20

interface:
  show_subtitles: true
  subtitle_font_size: 48

system:
  log_level: "INFO"
  auto_restart_on_error: true
```

### 6.4 Configurar Variables de Entorno

```bash
# Editar .env
nano .env
```

**Contenido recomendado:**

```bash
# Abuelo Agent - Variables de Entorno

# Hardware
ARDUINO_PORT=/dev/ttyUSB0
ARDUINO_BAUD_RATE=9600

# Audio
WHISPER_MODEL=small
WHISPER_LANGUAGE=es
PIPER_VOICE=es_ES-carlfm-medium

# LLM
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=gemma4:4b-instruct-q4_K_M
OLLAMA_CONTEXT_LENGTH=8192

# Visión
VISION_ENABLED=true
CAMERA_INDEX=0

# TV
TV_BRAND=Samsung
TV_PC_HDMI_PORT=HDMI1

# Sistema
BROWSER=brave
LOG_LEVEL=INFO
AUTO_RESTART_ON_ERROR=true
```

### 6.5 Configurar Permisos

```bash
# Agregar usuario al grupo video (para cámara)
sudo usermod -aG video $USER

# Dar permisos sobre puerto serial
sudo setfacl -m u:$USER:rw /dev/ttyUSB0

# Hacer permanente (opcional)
echo 'SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", MODE="0666"' | sudo tee /etc/udev/rules.d/99-arduino.rules

# Recargar reglas udev
sudo udevadm control --reload-rules
sudo udevadm trigger
```

### 6.6 Reiniciar Sesión

```bash
# Cerrar sesión y volver a entrar para aplicar cambios de grupos
# O ejecutar:
newgrp video
```

---

## 7. DESCARGA DE MODELOS DE IA

### 7.1 Descargar Gemma 4

```bash
# Verificar que Ollama esté corriendo
sudo systemctl status ollama

# Descargar modelo Gemma 4
ollama pull gemma4:4b-instruct-q4_K_M

# Tiempo estimado: 5-15 minutos (depende de tu internet)
# Tamaño: ~2.6 GB
```

### 7.2 Verificar Descarga

```bash
# Listar modelos instalados
ollama list

# Deberías ver:
# NAME                           ID              SIZE      MODIFIED
# gemma4:4b-instruct-q4_K_M      abc123...       2.6 GB    Now
```

### 7.3 Probar Modelo

```bash
# Ejecutar prueba rápida
ollama run gemma4:4b-instruct-q4_K_M "Hola, ¿cómo estás?"

# Deberías recibir una respuesta coherente
```

### 7.4 Descargar Voz para TTS (Piper)

```bash
# Crear directorio para voces
mkdir -p ~/.local/share/piper

# Descargar voz en español
cd ~/.local/share/piper
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/carlfm/medium/es_ES-carlfm-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/carlfm/medium/es_ES-carlfm-medium.onnx.json
```

### 7.5 Descargar Whisper (Primera Ejecución)

Whisper se descarga automáticamente la primera vez que se ejecuta. Para pre-descargar:

```bash
# Activar entorno virtual
source venv/bin/activate

# Ejecutar script de prueba que descarga Whisper
python3 -c "from faster_whisper import WhisperModel; model = WhisperModel('small')"
```

---

## 8. CONFIGURACIÓN DE CÓDIGOS IR

### 8.1 Identificar Marca y Modelo de TV

1. Busca la etiqueta trasera del TV
2. Anota marca y modelo exacto
3. Busca manual de usuario online si es necesario

### 8.2 Buscar Códigos IR

#### Método 1: Internet
```bash
# Buscar en Google:
"[Marca TV] IR codes NEC"
"[Marca TV] remote control codes"
"Ejemplo: Samsung UN55NU6900 IR codes"
```

#### Método 2: Base de Datos LIRC
```bash
# Visitar: https://lirc.sourceforge.net/remotes/
# Buscar por marca
# Descargar archivo de códigos
```

#### Método 3: Aprender con Receptor IR
```bash
# Hardware adicional necesario:
# - Módulo receptor IR TSOP38238 ($2 USD)
# - Arduino

# Conexiones:
# TSOP VCC → Arduino 5V
# TSOP GND → Arduino GND
# TSOUT → Arduino D11

# Usar sketch IRrecvDemo de librería IRremote
```

### 8.2 Editar Firmware con Códigos

```cpp
// Abrir: src/hardware/arduino_firmware/ir_button_controller.ino

// Agregar librería IRremote (desde Administrador de Librerías)
#include <IRremote.h>

// Definir códigos para tu TV (ejemplo Samsung)
#define SAMSUNG_POWER     0x04FB55AA
#define SAMSUNG_VOL_UP    0x04FB40BF
#define SAMSUNG_VOL_DOWN  0x04FB20DF
#define SAMSUNG_MUTE      0x04FB45BA
#define SAMSUNG_CH_UP     0x04FB15EA
#define SAMSUNG_CH_DOWN   0x04FB35CA
#define SAMSUNG_HDMI1     0x04FB807F
#define SAMSUNG_HDMI2     0x04FB609F

// Modificar función emitIRSignal()
void emitIRSignal(String code) {
  if (code == "POWER") {
    IrSender.sendNEC(SAMSUNG_POWER, 32);
  } else if (code == "VOL_UP") {
    IrSender.sendNEC(SAMSUNG_VOL_UP, 32);
  }
  // ... agregar más comandos
}
```

### 8.3 Códigos Comunes por Marca

#### Samsung (Protocolo NEC)
```cpp
POWER:    0x04FB55AA
VOL_UP:   0x04FB40BF
VOL_DOWN: 0x04FB20DF
MUTE:     0x04FB45BA
CH_UP:    0x04FB15EA
CH_DOWN:  0x04FB35CA
HDMI1:    0x04FB807F
HDMI2:    0x04FB609F
```

#### LG (Protocolo NEC)
```cpp
POWER:    0x20DF10EF
VOL_UP:   0x20DF40BF
VOL_DOWN: 0x20DFC03F
MUTE:     0x20DF906F
CH_UP:    0x20DF00FF
CH_DOWN:  0x20DF807F
HDMI1:    0x20DFE01F
```

#### Sony (Protocolo SIRC)
```cpp
POWER:    0xA90
VOL_UP:   0x490
VOL_DOWN: 0xC90
MUTE:     0x890
CH_UP:    0x190
CH_DOWN:  0x990
HDMI1:    0xC0B
```

### 8.4 Probar Códigos IR

```bash
# Conectar Arduino y abrir Monitor Serie
# Enviar comandos manualmente:
IR:POWER
IR:VOL_UP
IR:HDMI1

# Verificar que el TV responda
# Si no responde:
# 1. Verificar que LED IR esté funcionando (usar cámara de celular)
# 2. Apuntar directamente al sensor IR del TV
# 3. Probar diferentes códigos
# 4. Acercar Arduino al TV (máximo 3 metros)
```

---

## 9. PRUEBAS Y VERIFICACIÓN

### 9.1 Checklist de Verificación

#### Hardware
- [ ] Arduino enciende (LED power encendido)
- [ ] LED IR parpadea al enviar comandos
- [ ] Botón físico es detectado
- [ ] Cámara web es reconocida
- [ ] Todos los cables están seguros

#### Software
- [ ] Ollama está corriendo
- [ ] Modelo Gemma 4 está instalado
- [ ] Puerto Arduino es accesible
- [ ] Paquetes Python instalados
- [ ] Permisos configurados correctamente

### 9.2 Pruebas Individuales

#### Prueba 1: Arduino
```bash
# Activar entorno
source venv/bin/activate

# Probar conexión
python3 -c "from src.hardware.arduino_controller import ArduinoController; a = ArduinoController(); print('OK' if a.connect() else 'FAIL')"
```

#### Prueba 2: Ollama
```bash
# Verificar servicio
curl http://localhost:11434/api/tags

# Debería listar modelos instalados
```

#### Prueba 3: Whisper
```bash
# Probar transcripción
source venv/bin/activate
python3 -c "from src.audio.audio_processor import AudioProcessor; a = AudioProcessor(); print('Whisper OK')"
```

#### Prueba 4: Cámara
```bash
# Verificar cámara
ls -l /dev/video*
# Debería mostrar /dev/video0
```

### 9.3 Prueba Integral

```bash
# Activar entorno
cd /workspace
source venv/bin/activate

# Ejecutar agente
python3 src/agent/abuelo_agent.py

# Verificar mensajes iniciales:
# ✓ "Conectado a Arduino"
# ✓ "Agente en ejecución"
# ✓ "Esperando pulsación del botón"
```

### 9.4 Prueba de Funcionalidad Completa

1. **Presionar botón físico**
   - Debería decir: "🔘 Botón PULSADO"
   - TV debería mutearse

2. **Hablar claramente**
   - Decir: "Pon las noticias en YouTube"
   - Esperar 3-5 segundos

3. **Verificar respuesta**
   - Debería transcribir tu voz
   - Gemma 4 debería procesar
   - Navegador debería abrir YouTube
   - Video debería reproducirse

4. **Verificar memoria**
   ```bash
   # Revisar base de datos
   sqlite3 data/abuelo_memory.db "SELECT * FROM conversations ORDER BY timestamp DESC LIMIT 5;"
   ```

---

## 10. USO DIARIO

### 10.1 Iniciar el Sistema

```bash
# Método 1: Manual
cd /workspace
source venv/bin/activate
python3 src/agent/abuelo_agent.py

# Método 2: Script de inicio
./scripts/start.sh  # (crear este script opcionalmente)

# Método 3: Auto-inicio al boot
# Ver sección 12.3
```

### 10.2 Comandos de Voz Disponibles

#### Control Básico
- "Enciende la TV" → Power ON
- "Apaga la TV" → Power OFF
- "Sube el volumen" → Volume UP
- "Baja el volumen" → Volume DOWN
- "Silencia la TV" → Mute

#### Cambio de Entrada
- "Cambia a HDMI 1" → Switch HDMI1
- "Pon la computadora" → Switch HDMI1
- "Cambia a Netflix" → Botón Netflix (si disponible)

#### YouTube
- "Busca [canción] en YouTube" → Abre YouTube y busca
- "Pon música relajante" → Busca música relajante
- "Pon las noticias" → Busca noticias recientes

#### Información
- "¿Qué ves?" → Analiza pantalla actual
- "¿Está encendida la TV?" → Verifica estado
- "¿Qué hora es?" → Responde hora actual

### 10.3 Flujo de Uso Normal

```
1. Usuario presiona botón físico
   ↓
2. TV se mutea automáticamente
   ↓
3. Usuario habla claramente
   ↓
4. Usuario suelta botón
   ↓
5. Sistema transcribe audio (Whisper)
   ↓
6. Gemma 4 procesa petición
   ↓
7. Sistema ejecuta acción (IR, YouTube, etc.)
   ↓
8. Sistema responde por voz (TTS)
   ↓
9. TV volume restaurado
   ↓
10. Conversación guardada en memoria
```

### 10.4 Consejos para Mejor Reconocimiento

1. **Hablar claro y pausado**
   - No gritar, hablar normal
   - Articular bien las palabras

2. **Minimizar ruido ambiente**
   - TV muteada mientras hablas
   - Evitar hablar con otras personas

3. **Distancia adecuada**
   - Acercarse al micrófono (30-50 cm)
   - No cubrir el micrófono

4. **Comandos específicos**
   - ✅ "Busca música clásica en YouTube"
   - ❌ "Pon música" (muy vago)

---

## 11. SOLUCIÓN DE PROBLEMAS

### 11.1 Arduino No es Detectado

**Síntoma:** `Error conectando al Arduino: No such file`

**Soluciones:**
```bash
# 1. Verificar conexión física
ls /dev/ttyUSB* /dev/ttyACM*

# 2. Instalar drivers CH340 (clones chinos)
sudo dnf install -y ch341-uart

# 3. Verificar permisos
ls -l /dev/ttyUSB0
# Debería mostrar: crw-rw-rw-

# 4. Agregar usuario al grupo dialout
sudo usermod -aG dialout $USER

# 5. Reiniciar sesión
```

### 11.2 LED IR No Funciona

**Síntoma:** TV no responde a comandos IR

**Soluciones:**
1. **Verificar polaridad del LED**
   - Ánodo (+) va a resistencia
   - Cátodo (-) va a GND

2. **Probar con cámara de celular**
   - Apuntar LED a cámara
   - Enviar comando IR
   - Deberías ver luz violeta en pantalla

3. **Verificar resistencia**
   - Medir con multímetro
   - Debería ser ~220Ω

4. **Acercar al TV**
   - Máximo 3 metros
   - Sin obstáculos

5. **Aumentar corriente** (con precaución)
   - Cambiar resistencia a 150Ω
   - No bajar de 100Ω

### 11.3 Whisper No Transcribe

**Síntoma:** `Error transcribiendo: Model not found`

**Soluciones:**
```bash
# 1. Verificar instalación
source venv/bin/activate
pip list | grep whisper

# 2. Reinstalar
pip uninstall faster-whisper
pip install faster-whisper

# 3. Descargar modelo manualmente
python3 -c "from faster_whisper import WhisperModel; model = WhisperModel('small')"

# 4. Verificar espacio en disco
df -h
# Necesitas ~500MB libres
```

### 11.4 Ollama No Responde

**Síntoma:** `Error consultando LLM: Connection refused`

**Soluciones:**
```bash
# 1. Verificar servicio
sudo systemctl status ollama

# 2. Reiniciar servicio
sudo systemctl restart ollama

# 3. Verificar puerto
netstat -tlnp | grep 11434

# 4. Probar manualmente
curl http://localhost:11434/api/tags

# 5. Reinstalar Ollama
sudo dnf remove ollama
curl -fsSL https://ollama.ai/install.sh | sh
```

### 11.5 Cámara No Funciona

**Síntoma:** `No cameras available`

**Soluciones:**
```bash
# 1. Verificar dispositivo
ls -l /dev/video*

# 2. Verificar permisos
groups $USER
# Debería incluir 'video'

# 3. Agregar al grupo
sudo usermod -aG video $USER

# 4. Probar con otra aplicación
cheese  # o cualquier app de cámara

# 5. Verificar conexión USB
lsusb | grep -i camera
```

### 11.6 YouTube No Abre

**Síntoma:** `Error buscando video`

**Soluciones:**
```bash
# 1. Instalar navegador
sudo dnf install -y brave-browser

# 2. Instalar ChromeDriver
sudo dnf install -y chromedriver

# 3. Verificar Selenium
pip install selenium

# 4. Probar manualmente
python3 -c "from selenium import webdriver; d = webdriver.Chrome(); d.get('https://youtube.com')"
```

### 11.7 Sistema Lento

**Síntoma:** Respuestas tardan >10 segundos

**Soluciones:**
1. **Reducir tamaño de modelo**
   ```bash
   ollama pull gemma4:2b-instruct-q4_K_M
   # Editar config/settings.yaml
   # model: "gemma4:2b-instruct-q4_K_M"
   ```

2. **Cerrar aplicaciones innecesarias**
   ```bash
   htop  # Ver uso de recursos
   # Cerrar navegadores, etc.
   ```

3. **Reducir resolución de cámara**
   ```yaml
   # config/settings.yaml
   vision:
     resolution_width: 640
     resolution_height: 480
   ```

4. **Usar modelo Whisper más pequeño**
   ```yaml
   audio:
     whisper_model: "tiny"  # en lugar de "small"
   ```

### 11.8 Falsos Positivos del Botón

**Síntoma:** Sistema se activa sin presionar botón

**Soluciones:**
```cpp
// En firmware Arduino
const unsigned long debounceDelay = 100;  // Aumentar de 50 a 100ms

// Agregar filtro adicional
if (currentState == HIGH) {
  int readings = 0;
  for (int i = 0; i < 5; i++) {
    if (digitalRead(PIN_BUTTON) == LOW) readings++;
    delay(10);
  }
  if (readings >= 4) {
    // Confirmar pulsación
  }
}
```

---

## 12. MANTENIMIENTO

### 12.1 Actualizaciones Regulares

```bash
# Semanalmente
sudo dnf upgrade --refresh -y

# Mensualmente
source venv/bin/activate
pip install --upgrade -r requirements.txt

# Trimestralmente
ollama pull gemma4:4b-instruct-q4_K_M  # Actualizar modelo
```

### 12.2 Limpieza de Memoria

```bash
# Limpiar conversaciones antiguas (>30 días)
sqlite3 data/abuelo_memory.db "DELETE FROM conversations WHERE timestamp < datetime('now', '-30 days');"

# Compactar base de datos
sqlite3 data/abuelo_memory.db "VACUUM;"

# Limpiar logs antiguos
find logs/ -name "*.log" -mtime +30 -delete
```

### 12.3 Auto-Inicio al Boot

```bash
# Crear servicio systemd
sudo nano /etc/systemd/system/abuelo-agent.service
```

**Contenido:**
```ini
[Unit]
Description=Abuelo Agent Voice Assistant
After=network.target ollama.service

[Service]
Type=simple
User=tu_usuario
WorkingDirectory=/home/tu_usuario/abuelo-agent
ExecStart=/home/tu_usuario/abuelo-agent/venv/bin/python /home/tu_usuario/abuelo-agent/src/agent/abuelo_agent.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Habilitar:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable abuelo-agent
sudo systemctl start abuelo-agent
```

### 12.4 Backup de Configuración

```bash
# Crear script de backup
cat > ~/backup_abuelo.sh << 'EOF'
#!/bin/bash
BACKUP_DIR=~/backups/abuelo_$(date +%Y%m%d)
mkdir -p $BACKUP_DIR
cp -r /workspace/config $BACKUP_DIR/
cp /workspace/.env $BACKUP_DIR/
cp /workspace/data/abuelo_memory.db $BACKUP_DIR/
tar -czf $BACKUP_DIR.tar.gz $BACKUP_DIR
rm -rf $BACKUP_DIR
echo "Backup creado: $BACKUP_DIR.tar.gz"
EOF

chmod +x ~/backup_abuelo.sh

# Ejecutar semanalmente (agregar a crontab)
crontab -e
# Agregar línea:
0 2 * * 0 /home/tu_usuario/backup_abuelo.sh
```

### 12.5 Monitoreo de Salud

```bash
# Crear script de monitoreo
cat > ~/check_abuelo.sh << 'EOF'
#!/bin/bash
echo "=== Abuelo Agent Health Check ==="

# Verificar Ollama
curl -s http://localhost:11434/api/tags > /dev/null && echo "✓ Ollama OK" || echo "✗ Ollama FAIL"

# Verificar Arduino
test -c /dev/ttyUSB0 && echo "✓ Arduino OK" || echo "✗ Arduino FAIL"

# Verificar cámara
test -c /dev/video0 && echo "✓ Cámara OK" || echo "✗ Cámara FAIL"

# Verificar espacio en disco
df -h / | tail -1 | awk '{if ($5+0 > 90) print "✗ Disco LLENO ("$5")"; else print "✓ Disco OK ("$5")"}'

# Verificar RAM libre
free -h | awk '/Mem:/ {if ($7/$2*100 < 20) print "✗ RAM baja ("$7" libre)"; else print "✓ RAM OK ("$7" libre)"}'
EOF

chmod +x ~/check_abuelo.sh
```

---

## 🎉 ¡FELICIDADES!

Has completado la instalación completa de **Abuelo Agent**. 

### Resumen de lo Logrado:
✅ Hardware ensamblado y probado  
✅ Arduino programado  
✅ Sistema operativo instalado  
✅ Software configurado  
✅ Modelos de IA descargados  
✅ Códigos IR configurados  
✅ Sistema probado y funcional  

### Próximos Pasos Sugeridos:
1. **Personalizar** comandos para necesidades específicas
2. **Agregar** más códigos IR para otros dispositivos
3. **Compartir** el proyecto con otros familiares
4. **Contribuir** mejoras al código abierto

### Soporte y Comunidad:
- 📧 Email: soporte@abuelo-agent.dev
- 💬 Discord: https://discord.gg/abuelo-agent
- 📖 Wiki: https://github.com/abuelo-agent/wiki
- 🐛 Issues: https://github.com/abuelo-agent/issues

---

**Documentación creada:** Abril 2025  
**Versión:** 1.0  
**Licencia:** MIT

*"La tecnología debe servir a las personas, no al revés"*
