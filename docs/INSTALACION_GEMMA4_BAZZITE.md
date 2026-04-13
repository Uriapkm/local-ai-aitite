# 🚀 Guía de Instalación: Abuelo IA con Gemma 4 Multimodal

## Hardware Objetivo: AMD BC250 (Bazzite)

Esta guía está optimizada específicamente para la **AMD BC250** ("Ariel", el chip de PS5 en formato desktop) con:
- CPU: Zen 2 (8 núcleos)
- GPU: RDNA 2 "Cyan Skillfish" 
- Memoria: 16GB GDDR6 compartida
- Sistema: Bazzite (Fedora immutable + Steam Deck experience)

---

## ⚡ Instalación Rápida (Recomendada)

```bash
# Clonar repositorio
git clone <tu-repo>
cd abuelo-ia

# Ejecutar script de instalación automática
chmod +x scripts/install_gemma4_bazzite.sh
./scripts/install_gemma4_bazzite.sh
```

El script automático realiza todos los pasos descritos abajo y configura Vulkan automáticamente.

---

## 📋 Instalación Manual Paso a Paso

### Paso 1: Actualizar Sistema

```bash
sudo dnf upgrade --refresh -y
```

### Paso 2: Instalar Dependencias del Sistema

```bash
sudo dnf install -y \
    python3 python3-pip python3-devel python3-venv \
    git curl wget gcc gcc-c++ make cmake \
    portaudio-devel libsndfile-devel ffmpeg \
    libxcb vulkan-loader vulkan-tools \
    mesa-vulkan-drivers mesa-dri-drivers libdrm \
    rocm-hip-sdk rocm-opencl-sdk ollama
```

**Paquetes críticos para BC250:**
- `vulkan-loader`, `mesa-vulkan-drivers`: Para aceleración GPU vía Vulkan
- `rocm-*`: Soporte alternativo ROCm (fallback si Vulkan falla)
- `ollama`: Motor de inferencia local

### Paso 3: Configurar Entorno Python

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Paso 4: Configurar Ollama + Gemma 4

```bash
# Iniciar Ollama (si no corre como servicio)
ollama serve &

# Descargar Gemma 4 optimizado para BC250
ollama pull gemma4:4b-instruct-q4_K_M
```

**¿Por qué esta versión específica?**
- `4b-instruct`: Optimizado para seguir instrucciones (perfecto para control por voz)
- `q4_K_M`: Quantización K-quants media - equilibrio perfecto entre calidad y velocidad
- Tamaño en VRAM: ~2.6GB (deja 10+ GB libres para audio, visión y navegador)

**Alternativas si hay problemas:**
```bash
# Si gemma4 no está disponible aún
ollama pull gemma2:9b

# Si necesitas más velocidad (menos calidad)
ollama pull gemma2:2b
```

### Paso 5: Configurar Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```bash
cat > .env << EOF
# ============================================
# Configuración Abuelo IA - AMD BC250
# ============================================

# Hardware Arduino (AJUSTAR SEGÚN TU SISTEMA)
ARDUINO_PORT=/dev/ttyACM0

# LLM - Gemma 4 Multimodal
OLLAMA_MODEL=gemma4:4b-instruct-q4_K_M
OLLAMA_OLLAMA_HOST=http://localhost:11434
OLLAMA_USE_VULKAN=true

# Audio
AUDIO_WHISPER_MODEL=small
AUDIO_WHISPER_DEVICE=cpu
AUDIO_PIPER_VOICE=es_ES-carlfm-medium

# Visión
VISION_ENABLED=true
VISION_CAMERA_INDEX=0

# Navegador
YOUTUBE_BROWSER=brave

# Vulkan optimizations for RDNA2
export VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/radeon_icd.x86_64.json
export RADV_PERFTEST=sam,nggc
export MESA_GL_VERSION_OVERRIDE=4.6
EOF
```

### Paso 6: Crear Directorios

```bash
mkdir -p data/piper_voices logs captures
```

### Paso 7: Verificar Instalación

```bash
# Verificar que Gemma está disponible
ollama list | grep gemma

# Verificar puerto Arduino
ls /dev/ttyACM*

# Probar dependencias Python
source venv/bin/activate
python -c "import speechrecognition, pyaudio; print('✅ OK')"
```

---

## 🔧 Configuración Específica para BC250

### Optimizaciones Vulkan para RDNA2

La BC250 usa arquitectura RDNA 2, que tiene mejor soporte para Vulkan que para ROCm en ciertos escenarios. El proyecto configura automáticamente:

```bash
# Variables de entorno para Vulkan (en .env)
export VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/radeon_icd.x86_64.json
export RADV_PERFTEST=sam,nggc
export MESA_GL_VERSION_OVERRIDE=4.6
```

**Explicación:**
- `VK_ICD_FILENAMES`: Apunta al driver Vulkan de AMD (RADV)
- `RADV_PERFTEST=sam,nggc`: Habilita optimizaciones específicas para RDNA2
- `MESA_GL_VERSION_OVERRIDE=4.6`: Asegura compatibilidad OpenGL 4.6

### ¿Vulkan o ROCm?

| Característica | Vulkan (Recomendado) | ROCm |
|---------------|---------------------|------|
| Velocidad (tokens/s) | ~50-60 t/s | ~45-55 t/s |
| Estabilidad | ✅ Muy estable | ⚠️ Puede requerir tweaks |
| Consumo VRAM | Menor | Ligeramente mayor |
| Configuración | Automática | Manual a veces |
| Soporte Wayland | ✅ Nativo | ⚠️ Problemas ocasionales |

**Conclusión:** Usa Vulkan por defecto (`OLLAMA_USE_VULKAN=true`). Cambia a ROCm solo si experimentas problemas gráficos.

---

## 🎯 Verificación de Rendimiento

Una vez instalado, verifica el rendimiento:

```bash
source venv/bin/activate
python tests/benchmark_gemma4.py
```

**Rendimiento esperado en BC250:**
- **Tokens/segundo:** 50-60 t/s (texto), 45-55 t/s (multimodal)
- **VRAM usada:** ~2.6GB (modelo) + ~1GB (buffer sistema) = ~3.6GB total
- **RAM libre restante:** ~10-11GB para Whisper, navegador, etc.
- **Latencia primera respuesta:** <1 segundo para comandos simples

---

## 🐛 Solución de Problemas Comunes

### Problema: "Gemma 4 no encontrado en Ollama"

**Solución:**
```bash
# Verificar modelos disponibles
ollama list

# Si no aparece, descargar manualmente
ollama pull gemma4:4b-instruct-q4_K_M

# Si aún falla, usar fallback
ollama pull gemma2:9b
# Y actualizar .env:
# OLLAMA_MODEL=gemma2:9b
```

### Problema: "Lentitud extrema (<20 tokens/s)"

**Causas posibles:**
1. No se está usando aceleración GPU
2. Modelo demasiado grande para VRAM disponible

**Soluciones:**
```bash
# Verificar que Vulkan está activo
vulkaninfo | head -20

# Si no hay aceleración GPU, forzar uso de Vulkan
export VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/radeon_icd.x86_64.json

# Si el problema persiste, usar modelo más pequeño
ollama pull gemma2:2b
# Actualizar .env: OLLAMA_MODEL=gemma2:2b
```

### Problema: "Arduino no detectado"

```bash
# Listar puertos seriales
ls /dev/ttyACM*
ls /dev/ttyUSB*

# Si no aparece nada:
# 1. Verificar conexión USB
# 2. Probar otro cable/puerto
# 3. En Bazzite, puede necesitar permisos:
sudo usermod -a -G dialout $USER
# (requiere logout/login)
```

### Problema: "Audio no funciona"

```bash
# Verificar dispositivos de audio en Bazzite (PipeWire)
pactl info
pactl list sources short

# Si no hay micrófono, verificar configuraciones de sistema
# Bazzite usa PipeWire por defecto, no PulseAudio
```

---

## 📊 Comparativa de Modelos para BC250

| Modelo | VRAM | Tokens/s | Calidad Agente | Multimodal | Recomendado |
|--------|------|----------|---------------|------------|-------------|
| **Gemma 4 4B** | 2.6GB | 50-60 | ⭐⭐⭐⭐⭐ | ✅ Nativa | **SÍ (principal)** |
| Gemma 2 9B | 5.2GB | 35-45 | ⭐⭐⭐⭐ | ❌ | No (mucha VRAM) |
| Gemma 2 2B | 1.4GB | 70-80 | ⭐⭐⭐ | ❌ | Sí (fallback rápido) |
| Phi-3 Mini | 2.4GB | 35-45 | ⭐⭐⭐ | ⚠️ Adapter | No (menos capaz) |
| Llama 3.2 3B | 2.0GB | 55-65 | ⭐⭐⭐⭐ | ❌ | Alternativa válida |

---

## ✅ Checklist Final

Antes de declarar la instalación completada:

- [ ] Ollama corriendo (`ollama list` muestra Gemma)
- [ ] Gemma 4 descargado (`gemma4:4b-instruct-q4_K_M`)
- [ ] Archivo `.env` creado con configuración correcta
- [ ] Puerto Arduino detectado (`/dev/ttyACM0` o similar)
- [ ] Dependencias Python instaladas (`pip list` muestra todos los paquetes)
- [ ] Vulkan funcionando (`vulkaninfo` sin errores)
- [ ] Micrófono detectado (`pactl list sources`)
- [ ] Navegador instalado (`brave --version` o `google-chrome --version`)

---

## 🚀 Primer Uso

```bash
# Activar entorno
source venv/bin/activate

# Ejecutar agente
python src/main.py
```

**Flujo esperado:**
1. El agente inicia y carga configuración
2. Conecta con Arduino (o modo simulación si no detectado)
3. Inicia Ollama client con Gemma 4
4. Espera pulsación del botón físico
5. Al pulsar: graba audio → transcribe → consulta Gemma → ejecuta acción → responde

---

## 📖 Documentación Adicional

- `docs/GUIA_CONFIGURACION.md`: Guía detallada de configuración
- `config/settings.yaml`: Todos los parámetros ajustables
- `src/utils/config_manager.py`: Sistema de configuración tipado

---

## 🆘 Soporte

Si encuentras problemas específicos de BC250/Bazzite:
1. Revisa logs en `logs/abuelo_agent.log`
2. Verifica que Vulkan esté activo: `glxinfo | grep "OpenGL renderer"`
3. Consulta issues del repositorio o crea uno nuevo con:
   - Output de `ollama list`
   - Output de `vulkaninfo | head -30`
   - Logs relevantes

---

**¡Listo! Tu asistente IA con Gemma 4 debería funcionar óptimamente en la BC250.** 🎉
