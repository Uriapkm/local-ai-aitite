# 📋 PLAN DE PRODUCCIÓN - Abuelo IA para Bazzite

## Estado Actual del Proyecto

El código tiene una **base arquitectónica sólida** pero **NO está listo para producción** en la casa de tu abuelo. Funcionaría parcialmente pero con fallos críticos que lo harían inutilizable en el día a día.

---

## 🔴 PROBLEMAS CRÍTICOS (Impiden uso en producción)

### 1. **YouTube NO está implementado** ⚠️
- **Archivo:** `src/agent/abuelo_agent.py` línea 322-336
- **Problema:** `_tool_youtube_search()` solo imprime un mensaje y retorna `True`
- **Impacto:** Una de las funciones principales NO funciona
- **Solución requerida:** Implementar con Selenium + PyAutoGUI

### 2. **Parsing del LLM es muy frágil** ⚠️
- **Archivo:** `src/utils/ollama_client.py` línea 328-358
- **Problema:** Busca strings simples ("IR_SEND", "YOUTUBE") en texto libre
- **Impacto:** Falsos positivos/negativos constantes, acciones incorrectas
- **Solución requerida:** Forzar JSON estructurado en respuestas del LLM

### 3. **Audio blocking congela el sistema** ⚠️
- **Archivo:** `src/agent/abuelo_agent.py` línea 369-397 (`_play_audio_file`)
- **Problema:** `sd.wait()` bloquea todo mientras habla la IA
- **Impacto:** No se puede interrumpir, no responde a botón durante playback
- **Solución requerida:** Mover audio a thread no-bloqueante con capacidad de interrupción

### 4. **gpiozero en requirements.txt es incorrecto** ⚠️
- **Archivo:** `requirements.txt` línea 37
- **Problema:** `gpiozero` es para Raspberry Pi GPIO, no aplica en PC con Bazzite
- **Impacto:** Instalación falla o depende de librerías inútiles
- **Solución:** Eliminar de requirements

### 5. **Sin monitoring ni auto-recovery real** ⚠️
- **Archivo:** `config/settings.yaml` línea 95
- **Problema:** `auto_restart_on_error: true` está en config pero NO implementado
- **Impacto:** Si se cuelga, requiere intervención manual
- **Solución:** Implementar watchdog real o mejorar servicio systemd

### 6. **pyaudio puede fallar en Bazzite** ⚠️
- **Archivo:** `requirements.txt` línea 20
- **Problema:** PyAudio requiere compilación y dependencias de sistema específicas
- **Impacto:** Instalación puede fallar en Bazzite (OS inmutable)
- **Solución:** Usar `sounddevice` (ya usado en el código) o asegurar instalación correcta

---

## 🟡 PROBLEMAS SECUNDARIOS (Reducen fiabilidad)

### 7. Visión por colores es poco fiable
- **Archivo:** `src/vision/tv_state_detector.py` línea 207-246
- **Problema:** Detecta apps por histograma de color (YouTube = rojo)
- **Impacto:** Falsos positivos con contenido rojo, no detecta Netflix
- **Solución:** Usar Gemma 4 multimodal para análisis de screenshot

### 8. Logging rotativo NO implementado
- **Archivo:** `config/settings.yaml` línea 92-93
- **Problema:** Hay `log_file` pero no hay configuración de rotación
- **Impacto:** Logs pueden llenar disco con el tiempo
- **Solución:** Implementar `logging.handlers.RotatingFileHandler`

### 9. Dependencia de Arduino crítica sin fallback completo
- **Archivo:** `src/agent/abuelo_agent.py` línea 111-112
- **Problema:** Si Arduino falla, el sistema continúa pero sin control IR
- **Impacto:** Funcionalidad principal (control TV) perdida silenciosamente
- **Solución:** Alertas visibles + modo teclado/voz alternativo

### 10. Sin health checks de servicios externos
- **Archivos:** Varios
- **Problema:** No verifica si Ollama, Piper, Whisper están operativos tras inicio
- **Impacto:** Fallos en cascada no detectados
- **Solución:** Health checks periódicos + reintentos automáticos

---

## ✅ LO QUE SÍ FUNCIONA (Base sólida)

| Componente | Estado | Notas |
|------------|--------|-------|
| Transcripción (Whisper) | ✅ Bien | `faster-whisper` correcto, VAD implementado |
| Síntesis voz (Piper) | ✅ Bien | Subprocess estable, voces configuradas |
| Memoria SQLite | ✅ Bien | `MemoryManager` bien implementado |
| Configuración YAML | ✅ Bien | `ConfigManager` con validación |
| Control IR básico | ✅ Bien | Serial Arduino correcto |
| Sistema de herramientas | ✅ Bien | Arquitectura extensible |
| Button-triggered recording | ✅ Bien | Thread separado para Arduino |

---

## 🛠️ PLAN DE ACCIÓN (2-3 semanas)

### **FASE 1: Crítico (Semana 1)**

#### Día 1-2: YouTube funcional
```python
# Implementar en src/agent/abuelo_agent.py
def _tool_youtube_search(self, query: str) -> bool:
    """Busca y reproduce video en YouTube usando Selenium + PyAutoGUI"""
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    import pyautogui
    
    # 1. Abrir Brave con perfil kiosk
    options = webdriver.ChromeOptions()
    options.binary_location = "/usr/bin/brave"
    options.add_argument("--kiosk")
    options.add_argument("--no-first-run")
    
    driver = webdriver.Chrome(options=options)
    
    # 2. Navegar a YouTube
    url = f"https://www.youtube.com/results?search_query={quote_plus(query)}"
    driver.get(url)
    
    # 3. Esperar carga y hacer click en primer resultado
    time.sleep(3)
    pyautogui.press('tab', presses=2)  # Navegar al primer video
    pyautogui.press('enter')
    
    # 4. Pantalla completa
    pyautogui.press('f')
    
    return True
```
**Dependencies to add:**
```
selenium>=4.15.0
pyautogui>=0.9.54
python-xlib>=0.33  # Requerido por PyAutoGUI en Linux
```

#### Día 3: LLM con JSON forzado
```python
# Modificar src/utils/ollama_client.py
def generate(self, prompt, ..., response_format="json"):
    payload = {
        "model": self.model,
        "messages": messages,
        "format": "json",  # ← Forzar JSON
        "options": {...}
    }
    
# Modificar system prompt para exigir JSON:
system_prompt = """...
Responde SIEMPRE en formato JSON:
{
    "action": "REPLY|IR_SEND|YOUTUBE_SEARCH|SWITCH_HDMI",
    "parameters": {"command": "...", "query": "..."},
    "text": "Respuesta en español para el usuario"
}
"""
```

#### Día 4: Audio no-bloqueante
```python
# Crear src/audio/audio_player.py
class NonBlockingAudioPlayer:
    def __init__(self):
        self.current_stream = None
        self.is_playing = False
        self._stop_flag = False
        
    def play(self, file_path, allow_interrupt=True):
        self._stop_flag = False
        thread = threading.Thread(
            target=self._play_thread,
            args=(file_path,),
            daemon=True
        )
        thread.start()
        
    def _play_thread(self, file_path):
        import sounddevice as sd
        import wave
        
        with wave.open(file_path, 'rb') as wav:
            frames = wav.readframes(wav.getnframes())
            audio_data = np.frombuffer(frames, dtype=np.int16)
            
            stream = sd.Stream(
                samplerate=wav.getframerate(),
                channels=wav.getnchannels(),
                callback=self._audio_callback
            )
            stream.start()
            
            while not self._stop_flag and self.is_playing:
                time.sleep(0.1)
                
    def stop(self):
        self._stop_flag = True
        self.is_playing = False
```

#### Día 5: Testing intensivo en Bazzite
- Probar instalación limpia
- Verificar permisos de audio (PipeWire vs ALSA)
- Testear con micrófono USB real
- Validar latencia end-to-end

---

### **FASE 2: Fiabilidad (Semana 2)**

#### Día 6-7: Monitoring y auto-recovery
```bash
# Mejorar /etc/systemd/system/abuelo-ia.service
[Service]
Type=simple
Restart=on-failure
RestartSec=10
WatchdogSec=30  # ← Watchdog integrado
NotifyAccess=all

# Añadir health check en el código
def health_check():
    checks = {
        "ollama": check_ollama(),
        "piper": check_piper(),
        "arduino": check_arduino(),
        "audio_in": check_mic(),
        "audio_out": check_speakers()
    }
    if not all(checks.values()):
        logging.critical(f"Health check failed: {checks}")
        sys.exit(1)  # Systemd reiniciará
```

#### Día 8: Logging rotativo
```python
# En src/utils/logger.py
import logging.handlers

handler = logging.handlers.RotatingFileHandler(
    log_file,
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
```

#### Día 9: Visión con Gemma 4 multimodal
```python
# Reemplazar detección por colores con LLM
def detect_app_with_gemma(self, frame):
    image_path = self.save_frame(frame)
    
    prompt = """Analiza esta imagen de una TV y dime:
    1. ¿Está encendida? (sí/no)
    2. ¿Qué app se ve? (YouTube/Netflix/Prime/TV normal/desconocido)
    3. ¿Hay menú visible? (sí/no)
    
    Responde en JSON."""
    
    response = self.llm.generate_with_image(prompt, image_path)
    return parse_json(response)
```

#### Día 10: Fallback modes
- Implementar control por teclado (atajos globales)
- Añadir comandos de voz directos ("enciende TV", "abre YouTube")
- Crear modo "solo TTS" si IR falla

---

### **FASE 3: Producción (Semana 3)**

#### Día 11-12: Script de instalación robusto
```bash
# Mejorar scripts/install.sh

# 1. Verificar Bazzite
if ! grep -q "Bazzite" /etc/os-release; then
    echo "⚠️ Este script es para Bazzite OS"
    exit 1
fi

# 2. Check de requisitos hardware
check_microphone() { ... }
check_camera() { ... }
check_audio_output() { ... }

# 3. Instalar Flatpak dependencies (Bazzite usa flatpak)
flatpak install flathub com.brave.Browser -y
flatpak override --user --device=all com.brave.Browser

# 4. Configurar PipeWire para baja latencia
# 5. Tests automáticos post-instalación
```

#### Día 13: Documentación de troubleshooting
Crear `docs/TROUBLESHOOTING.md`:
- Cómo resetear si se cuelga
- Cómo cambiar volumen manualmente
- Cómo verificar estado de servicios
- Códigos de error comunes

#### Día 14: Testing con usuario real (tu abuelo)
- Observar uso sin intervenir
- Recoger feedback
- Ajustar personalidad/velocidad

---

## 📦 REQUIREMENTS.TXT ACTUALIZADO

```txt
# CORE
langgraph>=0.2.0
pydantic>=2.5.0
pydantic-settings>=2.1.0

# LLM
ollama>=0.1.0

# AUDIO
faster-whisper>=1.0.0
sounddevice>=0.4.6  # ← Reemplaza pyaudio
webrtcvad>=2.0.10

# TTS (subprocess, sin librería)

# VISION
opencv-python-headless>=4.9.0
pillow>=10.0.0

# HARDWARE
pyserial>=3.5
# gpiozero ELIMINADO (no aplica en PC)

# WEB - YouTube
selenium>=4.15.0
webdriver-manager>=4.0.0
pyautogui>=0.9.54
python-xlib>=0.33  # Linux requirement
yt-dlp>=2024.0.0
requests>=2.31.0

# MEMORIA
sqlite-utils>=3.36

# UTILIDADES
python-dotenv>=1.0.0
rich>=13.0.0
tqdm>=4.66.0
schedule>=1.2.0

# TESTS
pytest>=7.4.0
pytest-asyncio>=0.21.0
```

---

## 🔧 CONFIGURACIÓN ESPECÍFICA PARA BAZZITE

### 1. Audio (PipeWire)
Bazzite usa PipeWire por defecto. Configurar:
```bash
# ~/.config/pipewire/pipewire.conf.d/low-latency.conf
context.properties = {
    default.clock.rate = 48000
    default.clock.quantum = 256
    default.clock.min-quantum = 128
}
```

### 2. Permisos de Flatpak (Brave)
```bash
flatpak override --user \
    --socket=wayland \
    --socket=x11 \
    --device=all \
    com.brave.Browser
```

### 3. Servicio systemd mejorado
```ini
[Unit]
Description=Abuelo IA Assistant
After=network.target sound.target pipewire.service
Wants=pipewire.service

[Service]
Type=notify
User=tu_usuario
WorkingDirectory=/home/tu_usuario/abuelo-ia
Environment="PATH=/home/tu_usuario/abuelo-ia/venv/bin:%H/.local/bin:/usr/bin"
Environment="XDG_RUNTIME_DIR=/run/user/1000"
ExecStart=/home/tu_usuario/abuelo-ia/venv/bin/python -m src.agent.abuelo_agent
Restart=on-failure
RestartSec=10
WatchdogSec=30

# Logs
StandardOutput=journal
StandardError=journal
SyslogIdentifier=abuelo-ia

[Install]
WantedBy=multi-user.target
```

---

## 🎯 CHECKLIST PRE-PRODUCCIÓN

- [ ] YouTube funciona con Selenium + PyAutoGUI
- [ ] LLM devuelve JSON estructurado 100% de las veces
- [ ] Audio se puede interrumpir pulsando botón
- [ ] gpiozero eliminado de requirements
- [ ] Health checks implementados
- [ ] Logging rotativo configurado
- [ ] Script install.sh probado en Bazzite limpio
- [ ] Servicio systemd con watchdog
- [ ] Documentación de troubleshooting
- [ ] Backup automático de memoria SQLite
- [ ] Testado con tu abuelo durante 1 semana

---

## ⏱️ ESTIMACIÓN REALISTA

| Fase | Duración | Riesgo |
|------|----------|--------|
| Fase 1 (Crítico) | 5 días | Alto (YouTube complejo) |
| Fase 2 (Fiabilidad) | 5 días | Medio |
| Fase 3 (Producción) | 4 días | Bajo |
| **Testing real** | **7 días** | **Crítico** |
| **TOTAL** | **~3 semanas** | |

---

## 💡 RECOMENDACIÓN FINAL

**No instales esto en casa de tu abuelo todavía.** 

El proyecto tiene potencial pero necesita:
1. **Mínimo 2 semanas** de desarrollo intensivo
2. **1 semana** de testing con usuario real
3. **Buffer de 1 semana** para bugs inesperados

**Alternativa temporal:** 
- Usa el sistema actual SOLO para conversación y control IR básico
- YouTube hazlo manualmente hasta que esté automatizado
- Monitoriza logs diariamente para detectar fallos

Cuando todas las casillas del checklist estén marcadas, será seguro para producción.
