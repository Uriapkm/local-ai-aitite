# Abuelo IA - Asistente Local Inteligente

Asistente de IA local diseñado para ayudar a mi abuelo en su día a día, proporcionando compañía, entretenimiento y control del entorno del salón.

## 🎯 Objetivo

Crear un compañero inteligente que:
- Responda a comandos de voz de forma natural y paciente
- Controle la TV mediante infrarrojos (encender, apagar, menú, apps)
- Navegue por YouTube en el PC para mostrar contenido bajo demanda
- "Vea" lo que hay en la TV mediante cámara para tomar decisiones contextuales
- Recuerdo preferencias y historial de contenidos vistos
- Funcione 100% local, sin nube, respetando la privacidad

## 🖥️ Hardware

- **Placa:** AMD BC250 (APU Zen 2 + GPU RDNA2 "Cyan Skillfish")
- **Memoria:** 16GB GDDR6 unificada
- **OS:** Bazzite Linux (inmutable, basado en Fedora)
- **Micrófono:** USB con botón físico Push-to-Talk
- **Altavoces:** USB/3.5mm conectados al PC
- **Cámara:** Web USB apuntando a la TV
- **Control IR:** Arduino Nano + LED infrarrojo
- **Conexión:** Ethernet cableado

## 🧠 Stack Tecnológico

| Componente | Tecnología |
|------------|------------|
| **LLM Principal** | Gemma 4 E4B (4B, Q4_K_M) - Multimodal nativo |
| **Motor Inferencia** | Ollama (Vulkan/ROCm 7.0) |
| **STT (Voz → Texto)** | Faster-Whisper (distil-large-v3) |
| **TTS (Texto → Voz)** | Piper TTS (voces españolas naturales) |
| **Visión** | Integrada en Gemma 4 (nativa) |
| **Control IR** | Arduino Nano + Python (pyserial) |
| **Navegador** | Brave (modo kiosk, sin anuncios) |
| **Orquestación** | Python 3.12 + LangGraph Lite |
| **Memoria** | SQLite (historial, preferencias) |
| **Contenedores** | Docker/Podman |

## 📁 Estructura del Proyecto

```
abuelo-ia/
├── config/                 # Configuraciones (YAML, JSON)
│   ├── system_prompt.yaml  # Prompt principal de personalidad
│   ├── ir_codes.json       # Códigos IR de la TV
│   └── settings.yaml       # Ajustes generales
├── src/                    # Código fuente principal
│   ├── agent/              # Lógica del agente Gemma 4
│   │   ├── orchestrator.py # Gestor de estados y decisiones
│   │   ├── tools.py        # Herramientas (IR, YouTube, HDMI)
│   │   └── memory.py       # Gestión de memoria SQLite
│   ├── vision/             # Procesamiento de imagen de TV
│   │   └── camera.py       # Captura y análisis con Gemma 4
│   ├── audio/              # Procesamiento de audio
│   │   ├── stt.py          # Speech-to-Text (Whisper)
│   │   ├── tts.py          # Text-to-Speech (Piper)
│   │   └── button.py       # Listener del botón físico
│   ├── hardware/           # Control de hardware externo
│   │   ├── ir_controller.py# Comunicación con Arduino
│   │   └── hdmi_switch.py  # Control de entrada HDMI
│   └── utils/              # Utilidades comunes
│       ├── logger.py       # Sistema de logs
│       └── helpers.py      # Funciones auxiliares
├── scripts/                # Scripts de utilidad
│   ├── install.sh          # Instalación en Bazzite
│   ├── update.sh           # Actualización del sistema
│   └── backup.sh           # Copia de seguridad de memoria
├── docker/                 # Configuración de contenedores
│   ├── Dockerfile          # Imagen principal
│   └── compose.yaml        # Orquestación de servicios
├── data/                   # Datos persistentes
│   ├── models/             # Modelos descargados (opcional)
│   ├── memory/             # Base de datos SQLite
│   └── logs/               # Logs de ejecución
├── docs/                   # Documentación
│   └── architecture.md     # Diagramas y explicaciones
├── tests/                  # Tests unitarios y de integración
├── requirements.txt        # Dependencias Python
├── README.md               # Este archivo
└── LICENSE                 # Licencia MIT
```

## 🚀 Flujo de Funcionamiento

1. **Reposo:** TV encendida, volumen alto, sistema en espera
2. **Activación:** Abuelo pulsa botón físico → Arduino envía IR `MUTE`
3. **Captura:** Cámara toma foto de la TV + Micrófono graba audio
4. **Procesamiento:** 
   - Whisper transcribe audio
   - Gemma 4 analiza texto + imagen simultáneamente
   - Decide acción (IR, YouTube, responder)
5. **Ejecución:** 
   - Si es control: ejecuta herramienta correspondiente
   - Si es respuesta: Piper genera audio natural
6. **Cierre:** Arduino envía IR `UNMUTE` → Vuelta a reposo

## 🛠️ Instalación Rápida

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/abuelo-ia.git
cd abuelo-ia

# Ejecutar script de instalación (Bazzite)
chmod +x scripts/install.sh
./scripts/install.sh

# Iniciar servicios
docker compose up -d

# Ver logs
docker compose logs -f
```

## 🎭 Personalidad de la IA

La IA está configurada para:
- Ser paciente, cálida y respetuosa
- Usar lenguaje sencillo, sin tecnicismos
- Hablar despacio y con claridad
- Recordar preferencias y temas anteriores
- No monopolizar la conversación
- Priorizar el bienestar del abuelo

## 📝 Memoria y Privacidad

- **Todo es local:** Sin conexión a APIs externas (excepto YouTube para búsqueda)
- **SQLite:** Almacena videos vistos, preferencias, rutinas
- **Sin grabación permanente:** El audio se procesa en tiempo real, no se guarda
- **Imágenes efímeras:** Las capturas de TV se borran tras el análisis

## 🔧 Mantenimiento

El sistema está diseñado para requerir mínimo mantenimiento:
- Contenedores Docker auto-reiniciables
- Scripts de actualización sencilla
- Logs rotativos para no llenar disco
- Backup automático semanal de memoria

## 👨‍👩‍👧‍👦 Consideraciones Familiares

- **Botón físico:** Solo el abuelo puede activar el sistema
- **Detección de voz (opcional):** Puede ignorar si no es la voz del abuelo
- **Volumen adaptativo:** Baja TV mientras habla la IA
- **Feedback visual:** Muestra subtítulos grandes en pantalla

## 📄 Licencia

MIT License - Ver archivo LICENSE

---

*Proyecto hecho con ❤️ para mejorar la calidad de vida de mi abuelo*
