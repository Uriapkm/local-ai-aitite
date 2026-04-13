# Abuelo Agent - Asistente Multimodal Local

Asistente de voz multimodal para AMD BC250 (16GB GDDR6) con Gemma 4 E4B.

## Requisitos
- **Hardware:** AMD BC250 (Zen 2 + RDNA2), 16GB GDDR6
- **SO:** Bazzite Linux (Fedora Atomic)
- **Modelo:** Gemma 4 E4B (`gemma4:4b-instruct-q4_K_M`)
- **IR:** Arduino Nano por USB serial

## Instalación Rápida

```bash
# 1. Clonar y configurar
git clone <repo> && cd abuelo-agent
cp .env.example .env

# 2. Instalar en Bazzite
./scripts/install_gemma4_bazzite.sh

# 3. Configurar
./scripts/configure.sh

# 4. Ejecutar
python src/agent/abuelo_agent.py
```

## Configuración (`config/settings.yaml`)

```yaml
llm:
  model: gemma4:4b-instruct-q4_K_M
  use_vulkan: true  # RDNA2 optimizado
  context_length: 128000

audio:
  speech_model: systran/faster-whisper-small
  tts_voice: es-MX-JorgeNeural

ir:
  port: /dev/ttyUSB0  # Arduino Nano
```

## Arquitectura

```
src/
├── agent/          # Orquestador principal
├── audio/          # Whisper STT + Edge TTS
├── vision/         # Captura pantalla + análisis multimodal
├── ir/             # Control IR vía Arduino
├── llm/            # Cliente Ollama + Gemma 4
└── utils/          # Health monitor + recovery
```

## Comandos de Voz

- "Pon las noticias" → Cambia canal TV por IR
- "¿Qué ves?" → Analiza pantalla actual
- "Busca [tema] en YouTube" → Abre video
- "Sube el volumen" → Control TV IR

## Notas BC250

- **VRAM:** ~2.6GB modelo + ~2GB OS = ~11GB libres
- **Rendimiento:** 50-60 tokens/s con Vulkan
- **Multimodal:** Nativo en Gemma 4 (sin modelos extra)

## Licencia
MIT
