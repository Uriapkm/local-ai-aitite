"""
Agente Principal - Abuelo IA
Integra Gemma 4, visión, audio y control de hardware para crear el asistente completo.
"""

import os
import time
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

# Imports locales (se inicializarán bajo demanda)
from .hardware.arduino_controller import ArduinoController
from .audio.audio_processor import AudioProcessor


class AbueloAgent:
    """
    Agente principal que coordina todos los subsistemas:
    - LLM (Gemma 4 vía Ollama)
    - Visión (cámara web + Gemma 4 multimodal)
    - Audio (Whisper STT + Piper TTS)
    - Hardware (Arduino IR + botón)
    - Memoria (SQLite para historial)
    """
    
    def __init__(self, config_path: str = "./config/settings.yaml"):
        self.config = self._load_config(config_path)
        
        # Inicializar componentes
        self.arduino = ArduinoController(
            port=self.config.get("arduino", {}).get("port", "/dev/ttyUSB0"),
            baud_rate=self.config.get("arduino", {}).get("baud_rate", 9600)
        )
        
        self.audio = AudioProcessor(
            whisper_model=self.config.get("audio", {}).get("whisper_model", "small"),
            piper_voice=self.config.get("audio", {}).get("piper_voice", "es_ES-carlfm-medium")
        )
        
        # Estado del sistema
        self.is_active = False
        self.current_state = "IDLE"  # IDLE, LISTENING, PROCESSING, SPEAKING
        self.memory = []  # Historial de conversación reciente
        
        # Herramientas disponibles
        self.tools = {
            "IR_SEND": self._tool_ir_send,
            "SWITCH_HDMI_PC": self._tool_switch_hdmi_pc,
            "YOUTUBE_SEARCH": self._tool_youtube_search,
            "REPLY": self._tool_reply,
            "GET_TV_STATE": self._tool_get_tv_state
        }
        
        print("🤖 Agente Abuelo IA inicializado")
        print(f"   - Estado: {self.current_state}")
        print(f"   - Herramientas: {list(self.tools.keys())}")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Carga la configuración desde YAML."""
        # Implementación simplificada, usar pyyaml en producción
        config_file = Path(config_path)
        if config_file.exists():
            # TODO: Implementar carga real de YAML
            return {"arduino": {}, "audio": {}, "llm": {}, "vision": {}}
        else:
            print(f"⚠️ Config no encontrada en {config_path}, usando defaults")
            return {}
    
    def start(self):
        """Inicia el bucle principal del agente."""
        print("🚀 Iniciando agente...")
        
        # Conectar Arduino
        if not self.arduino.connect():
            print("⚠️ Arduino no conectado, continuando en modo simulación")
        
        # Registrar callbacks del botón
        self.arduino.start_button_monitor(
            on_press=self._on_button_pressed,
            on_release=self._on_button_released
        )
        
        print("✅ Agente en ejecución. Esperando pulsación del botón...")
        
        # Bucle principal (se mantiene vivo por el thread del Arduino)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Deteniendo agente...")
            self.stop()
    
    def stop(self):
        """Detiene el agente y libera recursos."""
        self.is_active = False
        self.arduino.stop()
        print("✅ Agente detenido")
    
    def _on_button_pressed(self):
        """Callback cuando se pulsa el botón."""
        print("\n🔘 === BOTÓN PULSADO ===")
        self.current_state = "LISTENING"
        self.is_active = True
        
        # Muteear TV inmediatamente
        print("🔇 Muteeando TV...")
        self.arduino.mute_tv()
        
        # Aquí iría la lógica de grabación de audio
        # self._start_recording()
    
    def _on_button_released(self):
        """Callback cuando se suelta el botón."""
        print("\n🔘 === BOTÓN SOLTADO ===")
        self.current_state = "PROCESSING"
        
        # Parar grabación y procesar
        # audio_file = self._stop_recording()
        # self._process_user_request(audio_file)
        
        # Desmuteear TV (o mantener mute mientras habla la IA)
        # Depende de la estrategia elegida
        print("🔊 Restaurando volumen TV...")
        self.arduino.unmute_tv()
        
        self.current_state = "IDLE"
    
    def _process_user_request(self, audio_file: str):
        """
        Procesa la petición del usuario:
        1. Transcribe audio
        2. Captura imagen de la TV
        3. Consulta a Gemma 4
        4. Ejecuta acción
        """
        print("🧠 Procesando petición...")
        
        # 1. Transcribir audio
        try:
            transcription, confidence = self.audio.transcribe(audio_file)
            print(f"📝 Usuario dice: '{transcription}'")
        except Exception as e:
            print(f"❌ Error transcribiendo: {e}")
            return
        
        # 2. Capturar imagen de la TV (si hay cámara)
        # tv_image = self._capture_tv_screen()
        
        # 3. Consultar a Gemma 4 (vía Ollama)
        # response = self._query_gemma4(transcription, tv_image)
        
        # 4. Ejecutar respuesta
        # self._execute_response(response)
    
    def _query_gemma4(self, user_text: str, tv_image: Optional[Any] = None) -> Dict[str, Any]:
        """
        Consulta a Gemma 4 con el texto del usuario y opcionalmente la imagen de la TV.
        Devuelve una estructura con la decisión y acciones a tomar.
        """
        # Implementación vía Ollama API
        # prompt = self._build_prompt(user_text, tv_image)
        # response = ollama.generate(model="gemma4:4b-instruct-q4_K_M", prompt=prompt)
        # return self._parse_response(response)
        pass
    
    # === HERRAMIENTAS ===
    
    def _tool_ir_send(self, command: str):
        """Envía un comando IR a la TV."""
        print(f"📡 Herramienta IR_SEND: {command}")
        self.arduino.send_ir_command(command)
    
    def _tool_switch_hdmi_pc(self):
        """Cambia la entrada HDMI al PC."""
        print("📺 Herramienta SWITCH_HDMI_PC")
        # Enviar comando IR para cambiar a HDMI correspondiente
        hdmi_port = self.config.get("tv", {}).get("pc_hdmi_port", "HDMI1")
        self.arduino.switch_hdmi(hdmi_port)
        time.sleep(2)  # Esperar cambio de entrada
    
    def _tool_youtube_search(self, query: str):
        """Busca y reproduce un video en YouTube (Brave)."""
        print(f"▶️ Herramienta YOUTUBE_SEARCH: {query}")
        # Implementar con Selenium o automatización de teclado
        # 1. Abrir Brave si no está abierto
        # 2. Ir a youtube.com
        # 3. Buscar query
        # 4. Reproducir primer resultado
        pass
    
    def _tool_reply(self, text: str):
        """Responde al usuario hablando (TTS)."""
        print(f"💬 Herramienta REPLY: '{text}'")
        # 1. Sintetizar voz
        # 2. Reproducir audio por altavoces del PC
        # 3. Opcional: mostrar texto en pantalla
        pass
    
    def _tool_get_tv_state(self) -> Dict[str, Any]:
        """Obtiene el estado actual de la TV (usando visión)."""
        print("👁️ Herramienta GET_TV_STATE")
        # 1. Capturar imagen
        # 2. Analizar con Gemma 4 vision
        # 3. Devolver descripción
        return {"state": "unknown", "app": "unknown", "content": "unknown"}


# Punto de entrada principal
if __name__ == "__main__":
    agent = AbueloAgent()
    agent.start()
