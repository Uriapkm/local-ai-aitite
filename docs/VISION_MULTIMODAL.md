# 📺 Visión Multimodal con Gemma 4

## Descripción

El módulo de visión permite al sistema "ver" lo que hay en la pantalla de la TV usando una cámara web y analizarlo con Gemma 4 multimodal.

## Características

- **Detección básica**: Encendido/apagado, brillo, pantalla negra
- **Detección avanzada con Gemma**: 
  - Aplicación específica (YouTube, Netflix, Prime, Disney+, etc.)
  - Tipo de contenido (película, serie, menú, anuncios)
  - Problemas detectados (pantalla azul, sin señal, congelada)
  - OCR básico para textos visibles

## Arquitectura

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Cámara    │────▶│ TVStateDetector  │────▶│  Imagen + ROI   │
│    USB      │     │  (OpenCV básico) │     │  (temp file)    │
└─────────────┘     └──────────────────┘     └────────┬────────┘
                                                      │
                                                      ▼
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Análisis   │◀────│  Gemma 4 Vision  │◀────│  Base64 Image   │
│  JSON       │     │    Analyzer      │     │                 │
└─────────────┘     └──────────────────┘     └─────────────────┘
```

## Uso Básico

### Detector Simple (sin cámara)

```python
from src.vision.tv_state_detector import SimpleTVStateDetector

detector = SimpleTVStateDetector()

# Obtener estado estimado
state = detector.detect_tv_state()
print(state["is_on"])  # True/False estimado

# Actualizar tras comando IR
detector.update_from_ir_command("POWER")
```

### Detector con Cámara

```python
from src.vision.tv_state_detector import create_tv_state_detector

detector = create_tv_state_detector(use_camera=True, camera_index=0)

# Detectar estado
state = detector.detect_tv_state()
print(f"TV encendida: {state['is_on']}")
print(f"Brillo: {state['brightness']:.2f}")
print(f"App detectada: {state['app_detected']}")

# Liberar recursos
detector.close()
```

### Analizador con Gemma 4

```python
from src.vision.gemma_vision_analyzer import GemmaVisionAnalyzer

analyzer = GemmaVisionAnalyzer(
    ollama_host="http://localhost:11434",
    model="gemma4"
)

# Capturar y analizar
result = analyzer.capture_and_analyze(camera_index=0)

if result["success"]:
    app = result["gemma_analysis"]["analysis"]["app_detected"]
    content = result["gemma_analysis"]["analysis"]["content_type"]
    print(f"Aplicación: {app}")
    print(f"Contenido: {content}")
    
    if result["gemma_analysis"]["analysis"]["issues_detected"]:
        print(f"Problemas: {result['gemma_analysis']['analysis']['issues_detected']}")

analyzer.close()
```

### Factory Function

```python
from src.vision import create_vision_analyzer

# Crea analizador con Gemma si está disponible, fallback a básico
analyzer = create_vision_analyzer(
    use_gemma=True,
    ollama_host="http://localhost:11434",
    model="gemma4",
    camera_index=0
)

# Usar...
app = analyzer.detect_app_quick()

# El factory maneja automáticamente los errores de inicialización
```

## Formato de Respuesta Gemma

Gemma 4 devuelve un JSON estructurado:

```json
{
    "app_detected": "youtube",
    "content_type": "video_clip",
    "is_menu_visible": false,
    "menu_items": [],
    "text_visible": "Mi Video Favorito",
    "dominant_colors": ["red", "white"],
    "has_people": true,
    "is_sports": false,
    "is_cartoon": false,
    "screen_quality": "good",
    "issues_detected": [],
    "confidence": 0.92
}
```

### Valores posibles:

- **app_detected**: `youtube`, `netflix`, `prime_video`, `disney_plus`, `hbo_max`, `movistar_plus`, `tv_normal`, `menu_system`, `unknown`
- **content_type**: `movie`, `series`, `live_tv`, `advertisement`, `menu`, `video_clip`, `music`, `game`, `unknown`
- **screen_quality**: `good`, `blurry`, `dark`, `glare`, `normal`
- **issues_detected**: `blue_screen`, `no_signal`, `frozen`, `black_bars`, etc.

## Integración con el Agente

El agente usa visión para:

1. **Verificar estado antes de acciones**: ¿TV encendida antes de cambiar volumen?
2. **Confirmar cambios de app**: ¿Se abrió YouTube tras el comando?
3. **Detectar problemas**: ¿Pantalla azul o sin señal?
4. **Navegación contextual**: ¿Está en el menú para saber qué botón pulsar?

```python
# En el agente
async def _check_tv_before_action(self):
    """Verifica estado TV antes de ejecutar acción"""
    vision = self.services.get("vision")
    if vision:
        state = vision.detect_tv_state()
        if not state["is_on"]:
            await self._speak("La TV parece estar apagada. ¿Quieres que la encienda?")
            return False
    return True
```

## Requisitos Hardware

- **Cámara web**: Cualquier cámara USB 720p o superior
- **Posicionamiento**: Apuntando a la TV, campo completo
- **Iluminación**: Evitar reflejos directos en pantalla
- **Distancia**: 1-3 metros de la TV

## Requisitos Software

- **OpenCV**: `pip install opencv-python-headless`
- **Ollama**: Corriendo localmente
- **Modelo Gemma 4**: `ollama pull gemma4`

## Configuración en Bazzite

```bash
# 1. Instalar dependencias
pip install opencv-python-headless pillow

# 2. Verificar cámara
ls -l /dev/video*

# 3. Testear captura
python src/vision/tv_state_detector.py

# 4. Pull modelo Gemma
ollama pull gemma4

# 5. Testear análisis
python src/vision/gemma_vision_analyzer.py
```

## Troubleshooting

### Cámara no detectada

```bash
# Listar dispositivos de video
ls -l /dev/video*

# Ver permisos
ls -l /dev/video0

# Si no hay permisos:
sudo usermod -aG video $USER
```

### OpenCV falla

```bash
# Reinstalar
pip uninstall opencv-python-headless
pip install opencv-python-headless --force-reinstall

# Probar versión con GUI (más pesada)
pip install opencv-python
```

### Gemma muy lento

- Usar modelo cuantizado: `ollama pull gemma4:4b-instruct-q4_K_M`
- Reducir resolución de cámara: `(640, 480)` en lugar de `(1280, 720)`
- Aumentar intervalo entre polls: `poll_interval=5.0`

### Falsos positivos en detección

- Ajustar ROI para capturar solo pantalla TV
- Mejorar iluminación ambiental
- Entrenar con ejemplos específicos (futuro)

## Testing

```bash
# Test detector básico
python src/vision/tv_state_detector.py

# Test analizador Gemma
python src/vision/gemma_vision_analyzer.py

# Test integrado
pytest tests/test_vision.py -v
```

## Futuras Mejoras

- [ ] Fine-tuning para logos específicos de apps
- [ ] Detección de gestos (abuelo señala algo)
- [ ] Lectura de subtítulos para contexto
- [ ] Detección de calidad de imagen (pixelado, artefactos)
- [ ] Integración con HDMI-CEC para estado real
