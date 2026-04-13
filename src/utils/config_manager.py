"""
Módulo de Configuración - Abuelo IA
Gestión tipada de configuración usando pydantic-settings
"""

from pathlib import Path
from typing import Optional, Dict, Any
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class ArduinoConfig(BaseSettings):
    """Configuración de Arduino"""
    port: str = Field(default="/dev/ttyUSB0", description="Puerto serial del Arduino")
    baud_rate: int = Field(default=9600, description="Velocidad de comunicación")
    button_pin: int = Field(default=2, description="Pin del botón físico")
    ir_led_pin: int = Field(default=3, description="Pin del LED IR")
    
    model_config = SettingsConfigDict(
        extra='ignore',
        env_prefix='ARDUINO_'
    )


class AudioConfig(BaseSettings):
    """Configuración de audio (STT y TTS)"""
    whisper_model: str = Field(default="small", description="Modelo Whisper: tiny, base, small, medium, large")
    whisper_device: str = Field(default="auto", description="Dispositivo: cpu, cuda, auto")
    whisper_language: str = Field(default="es", description="Idioma para transcripción")
    piper_voice: str = Field(default="es_ES-carlfm-medium", description="Voz para Piper TTS")
    piper_data_dir: str = Field(default="./data/piper_voices", description="Directorio de voces Piper")
    sample_rate: int = Field(default=16000, description="Frecuencia de muestreo")
    silence_threshold: float = Field(default=0.5, description="Umbral de silencio")
    
    model_config = SettingsConfigDict(
        extra='ignore',
        env_prefix='AUDIO_'
    )


class LLMConfig(BaseSettings):
    """Configuración del LLM (Gemma 4 vía Ollama)"""
    model: str = Field(default="gemma4:4b-instruct-q4_K_M", description="Modelo de lenguaje")
    context_length: int = Field(default=8192, description="Ventana de contexto")
    temperature: float = Field(default=0.7, description="Creatividad (0.0-2.0)")
    max_tokens: int = Field(default=512, description="Máximo tokens en respuesta")
    ollama_host: str = Field(default="http://localhost:11434", description="Endpoint de Ollama")
    
    model_config = SettingsConfigDict(
        extra='ignore',
        env_prefix='OLLAMA_'
    )


class VisionConfig(BaseSettings):
    """Configuración de visión"""
    enabled: bool = Field(default=True, description="Habilitar visión por cámara")
    camera_index: int = Field(default=0, description="Índice de cámara web")
    resolution_width: int = Field(default=1280, description="Ancho de resolución")
    resolution_height: int = Field(default=720, description="Alto de resolución")
    capture_delay: float = Field(default=0.5, description="Retraso antes de capturar")
    tv_screen_roi: Optional[Dict[str, int]] = Field(default=None, description="Región de interés TV")
    
    model_config = SettingsConfigDict(
        extra='ignore',
        env_prefix='VISION_'
    )


class TVConfig(BaseSettings):
    """Configuración específica de TV"""
    brand: str = Field(default="Samsung", description="Marca de la TV")
    pc_hdmi_port: str = Field(default="HDMI1", description="Puerto HDMI del PC")
    tv_hdmi_port: str = Field(default="HDMI2", description="Puerto HDMI nativo TV")
    mute_on_press: bool = Field(default=True, description="Muteear al pulsar botón")
    unmute_on_release: bool = Field(default=True, description="Desmuteear al soltar")
    volume_restore_delay: int = Field(default=2, description="Segundos para restaurar volumen")
    
    model_config = SettingsConfigDict(
        extra='ignore',
        env_prefix='TV_'
    )


class YouTubeConfig(BaseSettings):
    """Configuración de YouTube/navegador"""
    browser: str = Field(default="brave", description="Navegador: brave, chrome, firefox")
    kiosk_mode: bool = Field(default=False, description="Modo pantalla completa sin controles")
    default_quality: str = Field(default="1080p", description="Calidad preferida")
    save_history: bool = Field(default=True, description="Guardar historial de videos")
    history_db: str = Field(default="./data/youtube_history.db", description="Base de datos historial")
    
    model_config = SettingsConfigDict(
        extra='ignore',
        env_prefix='YOUTUBE_'
    )


class MemoryConfig(BaseSettings):
    """Configuración de memoria"""
    enabled: bool = Field(default=True, description="Habilitar memoria persistente")
    db_path: str = Field(default="./data/abuelo_memory.db", description="Ruta base de datos")
    max_conversation_history: int = Field(default=20, description="Máximo mensajes en contexto")
    save_preferences: bool = Field(default=True, description="Recordar preferencias")
    auto_suggest_interval: int = Field(default=3600, description="Segundos entre sugerencias")
    
    model_config = SettingsConfigDict(
        extra='ignore',
        env_prefix='MEMORY_'
    )


class InterfaceConfig(BaseSettings):
    """Configuración de interfaz"""
    show_subtitles: bool = Field(default=True, description="Mostrar subtítulos")
    subtitle_font_size: int = Field(default=48, description="Tamaño fuente subtítulos")
    subtitle_position: str = Field(default="bottom", description="Posición: top, bottom, center")
    show_status_indicator: bool = Field(default=True, description="Mostrar estado")
    theme: str = Field(default="dark", description="Tema: light, dark")
    
    model_config = SettingsConfigDict(
        extra='ignore',
        env_prefix='INTERFACE_'
    )


class SystemConfig(BaseSettings):
    """Configuración del sistema"""
    log_level: str = Field(default="INFO", description="Nivel de log: DEBUG, INFO, WARNING, ERROR")
    log_file: str = Field(default="./logs/abuelo_agent.log", description="Archivo de log")
    enable_debug_mode: bool = Field(default=False, description="Modo debug")
    auto_restart_on_error: bool = Field(default=True, description="Reiniciar automático en error")
    
    model_config = SettingsConfigDict(
        extra='ignore',
        env_prefix='SYSTEM_'
    )


class Config(BaseSettings):
    """Configuración principal del agente"""
    arduino: ArduinoConfig = Field(default_factory=ArduinoConfig)
    audio: AudioConfig = Field(default_factory=AudioConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    vision: VisionConfig = Field(default_factory=VisionConfig)
    tv: TVConfig = Field(default_factory=TVConfig)
    youtube: YouTubeConfig = Field(default_factory=YouTubeConfig)
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
    interface: InterfaceConfig = Field(default_factory=InterfaceConfig)
    system: SystemConfig = Field(default_factory=SystemConfig)
    
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )
    
    @classmethod
    def load_from_yaml(cls, yaml_path: str = "./config/settings.yaml") -> "Config":
        """
        Carga configuración desde archivo YAML
        
        Args:
            yaml_path: Ruta al archivo YAML
            
        Returns:
            Instancia de Config con los valores cargados
            
        Prioridad de configuración (mayor a menor):
        1. Variables de entorno (.env o exportadas)
        2. Archivo settings.yaml
        3. Valores por defecto en el código
        """
        import yaml
        
        config_file = Path(yaml_path)
        if not config_file.exists():
            print(f"⚠️ Archivo de configuración no encontrado: {yaml_path}")
            print("   Usando valores por defecto y variables de entorno")
            return cls()
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                yaml_data = yaml.safe_load(f)
            
            # Filtrar None values
            yaml_data = {k: v for k, v in yaml_data.items() if v is not None}
            
            # Crear instancia con los datos del YAML
            # Las variables de entorno tienen prioridad sobre los valores del YAML
            return cls(**yaml_data)
            
        except Exception as e:
            print(f"❌ Error cargando configuración: {e}")
            print("   Usando valores por defecto y variables de entorno")
            return cls()
    
    def validate(self) -> tuple[bool, list[str]]:
        """
        Valida que la configuración sea correcta
        
        Returns:
            Tupla (es_valida, lista_de_errores)
        """
        errors = []
        
        # Validar puerto Arduino
        if not self.arduino.port.startswith("/dev/"):
            errors.append(f"Puerto Arduino inválido: {self.arduino.port} (debe empezar con /dev/)")
        
        # Validar modelo Whisper
        valid_whisper_models = ["tiny", "base", "small", "medium", "large"]
        if self.audio.whisper_model not in valid_whisper_models:
            errors.append(f"Modelo Whisper inválido: {self.audio.whisper_model}. Opciones: {', '.join(valid_whisper_models)}")
        
        # Validar temperatura LLM
        if not 0.0 <= self.llm.temperature <= 2.0:
            errors.append(f"Temperatura LLM fuera de rango: {self.llm.temperature} (debe estar entre 0.0 y 2.0)")
        
        # Validar host Ollama
        if not self.llm.ollama_host.startswith("http"):
            errors.append(f"Host Ollama inválido: {self.llm.ollama_host} (debe empezar con http:// o https://)")
        
        # Validar resolución de cámara
        if self.vision.resolution_width <= 0 or self.vision.resolution_height <= 0:
            errors.append(f"Resolución de cámara inválida: {self.vision.resolution_width}x{self.vision.resolution_height}")
        
        # Validar navegador
        valid_browsers = ["brave", "chrome", "chromium", "firefox"]
        if self.youtube.browser.lower() not in valid_browsers:
            errors.append(f"Navegador no soportado: {self.youtube.browser}. Opciones: {', '.join(valid_browsers)}")
        
        # Validar nivel de log
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.system.log_level.upper() not in valid_log_levels:
            errors.append(f"Nivel de log inválido: {self.system.log_level}. Opciones: {', '.join(valid_log_levels)}")
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    def print_summary(self):
        """Imprime resumen de configuración"""
        print("\n" + "="*60)
        print("📋 CONFIGURACIÓN CARGADA")
        print("="*60)
        print(f"🔌 Arduino:      {self.arduino.port} @ {self.arduino.baud_rate}")
        print(f"🎤 Audio:        Whisper '{self.audio.whisper_model}' + Piper '{self.audio.piper_voice}'")
        print(f"🧠 LLM:          {self.llm.model} @ {self.llm.ollama_host}")
        print(f"👁️ Visión:       {'✅' if self.vision.enabled else '❌'} ({self.vision.resolution_width}x{self.vision.resolution_height})")
        print(f"📺 TV:           {self.tv.brand} → {self.tv.pc_hdmi_port}")
        print(f"💾 Memoria:      {'✅' if self.memory.enabled else '❌'} ({self.memory.db_path})")
        print(f"🌐 Navegador:    {self.youtube.browser} {'(kiosk)' if self.youtube.kiosk_mode else ''}")
        print(f"🪵 Logs:         {self.system.log_level} → {self.system.log_file}")
        print("="*60)
        
        # Validar y mostrar warnings
        is_valid, errors = self.validate()
        if not is_valid:
            print("\n⚠️  ERRORES DE CONFIGURACIÓN DETECTADOS:")
            for error in errors:
                print(f"   ❌ {error}")
            print("\n   El sistema puede funcionar incorrectamente.")
            print("   Revisa el archivo .env o config/settings.yaml\n")
        else:
            print("✅ Configuración válida\n")
