# 🤖 MANUAL DE INSTALACIÓN DESDE CERO - BC250 + Bazzite

**Objetivo**: Tener el sistema funcionando en 2-3 horas desde una instalación limpia de Bazzite.

---

## 📋 REQUISITOS PREVIOS

### Hardware necesario:
- ✅ BC250 con Bazzite instalado
- ✅ Arduino Nano/Uno con cable USB
- ✅ Micrófono USB o de 3.5mm
- ✅ Altavoces conectados
- ✅ Cámara USB (opcional, para visión)
- ✅ Conexión a Internet

### Software que instalaremos:
- Python 3.11+
- Ollama (IA local)
- Dependencias del sistema
- Modelos de IA (Whisper + Llama3.2)

---

## 🚀 PASO 1: ACTUALIZAR SISTEMA E INSTALAR HERRAMIENTAS BÁSICAS

```bash
# Actualizar paquetes del sistema
sudo rpm-ostree update

# Reiniciar si hubo actualizaciones
# sudo systemctl reboot

# Instalar herramientas de desarrollo
sudo rpm-ostree install \
    git \
    python3 \
    python3-pip \
    pipx \
    gcc \
    gcc-c++ \
    make \
    cmake \
    portaudio-devel \
    opencv-devel \
    libsndfile-devel \
    libtool \
    autoconf \
    automake \
    wget \
    curl
```

---

## 🔧 PASO 2: CONFIGURAR PYTHON Y VIRTUALENV

```bash
# Crear directorio para el proyecto
mkdir -p ~/roboto-abuelo
cd ~/roboto-abuelo

# Clonar el repositorio (ajusta la URL)
git clone <TU_REPOSITORIO> .
# O copia los archivos manualmente si no hay repo

# Crear entorno virtual
python3 -m venv venv

# Activar entorno
source venv/bin/activate

# Actualizar pip
pip install --upgrade pip setuptools wheel
```

---

## 🦙 PASO 3: INSTALAR OLLAMA Y MODELOS DE IA

```bash
# Instalar Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Iniciar servicio de Ollama
ollama serve &

# Esperar 5 segundos y descargar modelos
sleep 5

# Modelo de lenguaje (recomendado para BC250)
ollama pull llama3.2:3b

# Verificar instalación
ollama list
ollama run llama3.2:3b "Hola, ¿cómo estás?"
# Presiona Ctrl+D para salir
```

**⏱️ Tiempo estimado**: 10-20 minutos (depende de tu internet)

---

## 🔊 PASO 4: CONFIGURAR AUDIO EN BAZZITE (PIPEWIRE)

```bash
# Verificar que PipeWire está activo
systemctl --user status pipewire

# Listar dispositivos de audio disponibles
pw-cli list-objects | grep -E "(Sink|Source)"

# Configurar permisos de audio (si es necesario)
flatpak override --user --socket=pulseaudio --talk-name=org.pulseaudio.Server

# Probar grabación
arecord -l  # Listar dispositivos de captura
arecord -d 3 -f cd test.wav && aplay test.wav
```

**Nota**: Bazzite usa PipeWire por defecto, debería funcionar sin configuración adicional.

---

## 📦 PASO 5: INSTALAR DEPENDENCIAS DE PYTHON

```bash
# Desde el directorio del proyecto con venv activado
pip install -r requirements.txt

# Si hay errores con dependencias nativas:
sudo rpm-ostree install \
    python3-devel \
    portaudio-devel \
    opencv-devel \
    libsndfile-devel

# Reintentar instalación
pip install -r requirements.txt
```

**Dependencias críticas**:
- `speechrecognition` → Reconocimiento de voz
- `pyttsx3` → Síntesis de voz
- `opencv-python` → Visión por computadora
- `pyserial` → Comunicación con Arduino
- `transformers` → Whisper (STT local)

---

## 🔌 PASO 6: CONFIGURARDUINO Y PUERTO SERIAL

```bash
# Conectar Arduino por USB

# Listar puertos seriales disponibles
ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null

# Identificar el puerto correcto
dmesg | grep tty
# Busca algo como: "ttyACM0: USB FTDI Serial Device"

# Agregar usuario al grupo dialout (para acceso serial)
sudo usermod -a -G dialout $USER

# Verificar permisos
ls -l /dev/ttyACM0  # o el puerto que encontraste
```

**Importante**: Anota el puerto (ej: `/dev/ttyACM0`) para la configuración.

---

## ⚙️ PASO 7: CREAR ARCHIVO DE CONFIGURACIÓN

```bash
# Copiar plantilla de configuración
cp .env.example .env

# Editar configuración
nano .env
```

**Configuración mínima requerida**:

```ini
# === CONFIGURACIÓN CRÍTICA ===
ARDUINO_PORT=/dev/ttyACM0
BROWSER=firefox
WHISPER_MODEL=tiny

# === MODELOS DE IA ===
OLLAMA_MODEL=llama3.2:3b
OLLAMA_BASE_URL=http://localhost:11434

# === AUDIO ===
AUDIO_INPUT_DEVICE=default
AUDIO_OUTPUT_DEVICE=default
SPEECH_RATE=150

# === RUTAS ===
PROJECT_ROOT=/home/tu_usuario/roboto-abuelo
LOGS_DIR=/home/tu_usuario/roboto-abuelo/logs
DATA_DIR=/home/tu_usuario/roboto-abuelo/data

# === COMPORTAMIENTO ===
DEBUG_MODE=true
VOICE_ENABLED=true
VISION_ENABLED=false
HEALTH_MONITOR_INTERVAL=60
```

**Reemplaza `tu_usuario` con tu nombre de usuario real**.

---

## 🧪 PASO 8: PROBAR COMPONENTES INDIVIDUALES

### 8.1 Probar comunicación con Arduino
```bash
source venv/bin/activate
python src/hardware/test_arduino.py
# Debería mostrar: "Arduino conectado en /dev/ttyACM0"
```

### 8.2 Probar reconocimiento de voz
```bash
python src/audio/test_stt.py
# Di algo en el micrófono, debería transcribirlo
```

### 8.3 Probar síntesis de voz
```bash
python src/audio/test_tts.py
# Deberías escuchar: "Hola, soy tu asistente"
```

### 8.4 Probar Ollama
```bash
python src/ai/test_ollama.py
# Debería responder: "¡Hola! Estoy funcionando correctamente"
```

### 8.5 Probar health monitor
```bash
python src/utils/test_health_monitor.py
# Debería mostrar estado del sistema
```

---

## 🎯 PASO 9: EJECUTAR SISTEMA COMPLETO

```bash
# Asegúrate de estar en el directorio correcto
cd ~/roboto-abuelo
source venv/bin/activate

# Ejecutar el sistema principal
python main.py

# O con logging detallado
python main.py --debug --verbose
```

**Primeras pruebas**:
1. Di: "Hola" → Debería responder
2. Di: "¿Qué hora es?" → Debería decir la hora
3. Di: "Abre YouTube" → Debería abrir navegador (si está configurado)
4. Di: "Sube el volumen" → Debería mover el servo (si Arduino conectado)

---

## 🐛 SOLUCIÓN DE PROBLEMAS COMUNES

### ❌ Error: "No module named 'serial'"
```bash
pip install pyserial
```

### ❌ Error: "Permission denied: /dev/ttyACM0"
```bash
sudo usermod -a -G dialout $USER
# Cierra sesión y vuelve a entrar
```

### ❌ Error: "Ollama no responde"
```bash
# Verificar servicio
systemctl status ollama

# Reiniciar servicio
ollama serve &
```

### ❌ Error: "No audio devices found"
```bash
# Verificar dispositivos
pw-cli list-objects

# Probar con dispositivo específico
export AUDIO_INPUT_DEVICE=alsa_input.usb-tu_microfono
```

### ❌ Error: "Whisper model not found"
```bash
# Descargar modelo manualmente
python src/audio/download_whisper_models.py
```

### ❌ Error en Bazzite/Wayland con PyAutoGUI
```bash
# Instalar dependencias adicionales
sudo rpm-ostree install xdotool wmctrl

# Usar modo alternativo (si está disponible)
export USE_KEYBOARD_CONTROL=true
```

---

## ✅ CHECKLIST FINAL

Antes de considerar el sistema "funcionando":

- [ ] Ollama responde a consultas básicas
- [ ] El micrófono captura audio correctamente
- [ ] La síntesis de voz se escucha clara
- [ ] Arduino responde a comandos básicos
- [ ] El health monitor reporta estado OK
- [ ] Los logs se generan sin errores
- [ ] El sistema maneja errores gracefulmente
- [ ] Tu abuelo puede decir "Hola" y recibir respuesta

---

## 📞 PRÓXIMOS PASOS

Una vez funcionando:

1. **Personalizar respuestas**: Editar `src/ai/personality.yaml`
2. **Añadir comandos personalizados**: Modificar `src/core/command_registry.py`
3. **Configurar arranque automático**: Crear systemd service
4. **Mejorar estabilidad**: Implementar reintentos y timeouts
5. **Documentar uso**: Crear guía simple para tu abuelo

---

## ⏱️ TIEMPO ESTIMADO TOTAL

| Paso | Tiempo |
|------|--------|
| Actualizar sistema | 10-20 min |
| Instalar Python deps | 5-10 min |
| Instalar Ollama + modelos | 15-30 min |
| Configurar audio | 5 min |
| Configurar Arduino | 5-10 min |
| Crear .env | 5 min |
| Probar componentes | 15-20 min |
| **TOTAL** | **60-105 min** |

---

## 💡 CONSEJOS PARA TU ABUELO

Crea un archivo `INSTRUCCIONES_ABUELO.txt`:

```
PARA USAR EL ROBOT:

1. Enciende el ordenador
2. Espera 1 minuto a que se encienda todo
3. Di claramente: "Hola"
4. Espera la respuesta
5. Pide lo que necesites:
   - "¿Qué hora es?"
   - "Pon música"
   - "Llama a [nombre]"
   - "Apaga la luz"

SI NO FUNCIONA:
- Habla más claro y cerca del micrófono
- Reinicia el ordenador
- Llama a [tu teléfono]
```

---

**¿Listo para empezar? Ejecuta el PASO 1 y avísame cuando termines.**
