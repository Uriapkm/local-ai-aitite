# ============================================
# GUÍA DE CONFIGURACIÓN - Abuelo IA Assistant
# ============================================

## 📋 Introducción

Este proyecto usa un sistema de configuración en **dos capas**:

1. **Archivo `.env`** (variables de entorno) - Para valores específicos de tu instalación
2. **Archivo `config/settings.yaml`** - Para configuración general del sistema

**Prioridad**: Variables de entorno > YAML > Valores por defecto

---

## 🚀 Primeros Pasos

### 1. Copiar plantilla .env

```bash
cp .env.example .env
```

### 2. Descubrir tu puerto Arduino

```bash
# Conecta el Arduino y ejecuta:
ls /dev/ttyUSB* /dev/ttyACM*
```

El resultado será algo como `/dev/ttyUSB0` o `/dev/ttyACM0`. **Anota este valor**.

### 3. Editar .env

Abre el archivo `.env` y modifica al menos:

```ini
# CRÍTICO: Puerto de tu Arduino
ARDUINO_PORT=/dev/ttyUSB0

# Opcional: Cambiar navegador si no usas Brave
BROWSER=chrome

# Opcional: Cambiar modelo Whisper si tienes poca RAM
WHISPER_MODEL=tiny
```

---

## 🔧 Variables Críticas (DEBES configurar)

### ARDUINO_PORT
- **Qué es**: Puerto USB donde está conectado el Arduino
- **Cómo saberlo**: `ls /dev/ttyUSB* /dev/ttyACM*`
- **Valores típicos**: `/dev/ttyUSB0`, `/dev/ttyACM0`
- **Error común**: Dejar `/dev/ttyUSB0` cuando tu Arduino está en `/dev/ttyACM0`

### BROWSER
- **Qué es**: Navegador para YouTube
- **Opciones**: `brave`, `chrome`, `chromium`, `firefox`
- **Nota Bazzite**: Si usas Flatpak, necesita permisos especiales (ver más abajo)

---

## ⚙️ Variables Opcionales (ajustar según necesidades)

### AUDIO
```ini
# Modelos Whisper (menor = más rápido, mayor = más preciso)
WHISPER_MODEL=tiny      # Muy rápido, menos preciso (4GB RAM)
WHISPER_MODEL=base      # Rápido, bueno para la mayoría (4GB RAM)
WHISPER_MODEL=small     # Equilibrado (6GB RAM) ← RECOMENDADO
WHISPER_MODEL=medium    # Preciso, más lento (8GB RAM)
WHISPER_MODEL=large     # Máxima precisión, lento (10GB+ RAM)

# Voz del asistente
PIPER_VOICE=es_ES-carlfm-medium  # Voz masculina española
PIPER_VOICE=es_ES-davefx-medium  # Voz alternativa
# Ver todas: https://github.com/rhasspy/piper/blob/master/VOICES.md
```

### LLM
```ini
# Modelo de lenguaje (debe estar descargado en Ollama)
OLLAMA_MODEL=gemma4:4b-instruct-q4_K_M  # Recomendado
OLLAMA_MODEL=llama3.2:3b                # Alternativa más ligera
OLLAMA_TEMPERATURE=0.7                  # 0.0=determinista, 1.0=creativo
```

### VISIÓN
```ini
VISION_ENABLED=true          # false para deshabilitar cámara
CAMERA_INDEX=0               # 0=primera cámara, 1=segunda, etc.
CAMERA_WIDTH=1280            # Resolución horizontal
CAMERA_HEIGHT=720            # Resolución vertical
```

---

## 🐧 Configuración Especial para Bazzite OS

### Problema: Navegador Flatpak + PyAutoGUI

En Bazzite, los navegadores suelen ser Flatpaks, que tienen restricciones de seguridad.

### Solución 1: Dar permisos a Flatpak

```bash
# Para Brave
flatpak override --user \
    --socket=wayland \
    --socket=x11 \
    --device=all \
    com.brave.Browser

# Para Firefox
flatpak override --user \
    --socket=wayland \
    --socket=x11 \
    --device=all \
    org.mozilla.firefox
```

### Solución 2: Usar navegador nativo (no Flatpak)

```bash
# Instalar Chrome nativo
sudo dnf install google-chrome-stable

# Luego en .env:
BROWSER=chrome
```

### Solución 3: Forzar backend X11 para PyAutoGUI

```ini
# En .env
PYAUTOGUI_BACKEND=x11
```

---

## 🔍 Comandos Útiles

### Ver puertos USB disponibles
```bash
ls -la /dev/ttyUSB* /dev/ttyACM* 2>/dev/null
```

### Ver cámaras disponibles
```bash
v4l2-ctl --list-devices
# o
ls -la /dev/video*
```

### Verificar Ollama
```bash
ollama list                    # Modelos instalados
ollama pull gemma4:4b-instruct-q4_K_M  # Descargar modelo
```

### Test de configuración
```bash
source venv/bin/activate
python -c "from src.utils.config_manager import Config; c = Config.load_from_yaml(); c.print_summary()"
```

---

## 📁 Estructura de Archivos de Configuración

```
/workspace/
├── .env                 # TU configuración específica (crear desde .env.example)
├── .env.example         # Plantilla con todos los valores posibles
└── config/
    └── settings.yaml    # Configuración general (puedes editar, pero .env tiene prioridad)
```

---

## ❓ Troubleshooting

### "Puerto Arduino inválido"
- Asegúrate de que el Arduino está conectado
- Ejecuta `ls /dev/ttyUSB* /dev/ttyACM*` para ver el puerto correcto
- Añade tu usuario al grupo dialout: `sudo usermod -a -G dialout $USER`
- Reinicia sesión

### "No se encuentra el navegador"
- Verifica qué navegadores tienes: `which brave chrome chromium firefox`
- Actualiza `BROWSER=` en `.env`
- Si usas Flatpak, da permisos (ver sección Bazzite arriba)

### "Modelo Whisper no disponible"
- Los modelos se descargan automáticamente la primera vez
- Requiere conexión a internet
- Espacio necesario: tiny (100MB), base (150MB), small (500MB), medium (1.5GB), large (3GB)

### "Ollama no responde"
- Inicia Ollama: `ollama serve`
- En otra terminal, prueba: `ollama run gemma4:4b-instruct-q4_K_M "hola"`
- Verifica el host en `.env`: `OLLAMA_HOST=http://localhost:11434`

---

## 🎯 Configuración Mínima para Empezar

Si quieres lo más simple posible, solo edita esto en `.env`:

```ini
ARDUINO_PORT=/dev/ttyUSB0    # O el que te salga en ls /dev/ttyUSB*
BROWSER=brave                 # O chrome/firefox
WHISPER_MODEL=small           # O tiny si tienes poca RAM
```

El resto puede quedarse con los valores por defecto.

---

## 📞 Soporte

Si tienes problemas:

1. Revisa los logs: `cat logs/abuelo_agent.log`
2. Ejecuta en modo debug: añade `ENABLE_DEBUG_MODE=true` en `.env`
3. Consulta la documentación en `docs/`
