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
    port: str = "/dev/ttyUSB0"
    baud_rate: int = 9600
    button_pin: int = 2
    ir_led_pin: int = 3
    
    model_config = SettingsConfigDict(extra='ignore')


class AudioConfig(BaseSettings):
    """Configuración de audio (STT y TTS)"""
    whisper_model: str = "small"
    whisper_device: str = "auto"
    whisper_language: str = "es"
    piper_voice: str = "es_ES-carlfm-medium"
    piper_data_dir: str = "./data/piper_voices"
    sample_rate: int = 16000
    silence_threshold: float = 0.5
    
    model_config = SettingsConfigDict(extra='ignore')


class LLMConfig(BaseSettings):
    """Configuración del LLM (Gemma 4 vía Ollama)"""
    model: str = "gemma4:4b-instruct-q4_K_M"
    context_length: int = 8192
    temperature: float = 0.7
    max_tokens: int = 512
    ollama_host: str = "http://localhost:11434"
    
    model_config = SettingsConfigDict(extra='ignore')


class VisionConfig(BaseSettings):
    """Configuración de visión"""
    enabled: bool = True
    camera_index: int = 0
    resolution_width: int = 1280
    resolution_height: int = 720
    capture_delay: float = 0.5
    tv_screen_roi: Optional[Dict[str, int]] = None
    
    model_config = SettingsConfigDict(extra='ignore')


class TVConfig(BaseSettings):
    """Configuración específica de TV"""
    brand: str = "Samsung"
    pc_hdmi_port: str = "HDMI1"
    tv_hdmi_port: str = "HDMI2"
    mute_on_press: bool = True
    unmute_on_release: bool = True
    volume_restore_delay: int = 2
    
    model_config = SettingsConfigDict(extra='ignore')


class YouTubeConfig(BaseSettings):
    """Configuración de YouTube/navegador"""
    browser: str = "brave"
    kiosk_mode: bool = False
    default_quality: str = "1080p"
    save_history: bool = True
    history_db: str = "./data/youtube_history.db"
    
    model_config = SettingsConfigDict(extra='ignore')


class MemoryConfig(BaseSettings):
    """Configuración de memoria"""
    enabled: bool = True
    db_path: str = "./data/abuelo_memory.db"
    max_conversation_history: int = 20
    save_preferences: bool = True
    auto_suggest_interval: int = 3600
    
    model_config = SettingsConfigDict(extra='ignore')


class InterfaceConfig(BaseSettings):
    """Configuración de interfaz"""
    show_subtitles: bool = True
    subtitle_font_size: int = 48
    subtitle_position: str = "bottom"
    show_status_indicator: bool = True
    theme: str = "dark"
    
    model_config = SettingsConfigDict(extra='ignore')


class SystemConfig(BaseSettings):
    """Configuración del sistema"""
    log_level: str = "INFO"
    log_file: str = "./logs/abuelo_agent.log"
    enable_debug_mode: bool = False
    auto_restart_on_error: bool = True
    
    model_config = SettingsConfigDict(extra='ignore')


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
        """
        import yaml
        
        config_file = Path(yaml_path)
        if not config_file.exists():
            print(f"⚠️ Archivo de configuración no encontrado: {yaml_path}")
            print("   Usando valores por defecto")
            return cls()
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                yaml_data = yaml.safe_load(f)
            
            # Filtrar None values
            yaml_data = {k: v for k, v in yaml_data.items() if v is not None}
            
            # Crear instancia con los datos del YAML
            return cls(**yaml_data)
            
        except Exception as e:
            print(f"❌ Error cargando configuración: {e}")
            print("   Usando valores por defecto")
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
            errors.append(f"Puerto Arduino inválido: {self.arduino.port}")
        
        # Validar modelo Whisper
        valid_whisper_models = ["tiny", "base", "small", "medium", "large"]
        if self.audio.whisper_model not in valid_whisper_models:
            errors.append(f"Modelo Whisper inválido: {self.audio.whisper_model}")
        
        # Validar temperatura LLM
        if not 0.0 <= self.llm.temperature <= 2.0:
            errors.append(f"Temperatura LLM fuera de rango: {self.llm.temperature}")
        
        # Validar host Ollama
        if not self.llm.ollama_host.startswith("http"):
            errors.append(f"Host Ollama inválido: {self.llm.ollama_host}")
        
        # Validar resolución de cámara
        if self.vision.resolution_width <= 0 or self.vision.resolution_height <= 0:
            errors.append("Resolución de cámara inválida")
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    def print_summary(self):
        """Imprime resumen de configuración"""
        print("\n" + "="*50)
        print("📋 CONFIGURACIÓN CARGADA")
        print("="*50)
        print(f"🔌 Arduino: {self.arduino.port} @ {self.arduino.baud_rate}")
        print(f"🎤 Audio: Whisper '{self.audio.whisper_model}' + Piper '{self.audio.piper_voice}'")
        print(f"🧠 LLM: {self.llm.model} @ {self.llm.ollama_host}")
        print(f"👁️ Visión: {'✅' if self.vision.enabled else '❌'} ({self.vision.resolution_width}x{self.vision.resolution_height})")
        print(f"📺 TV: {self.tv.brand} → {self.tv.pc_hdmi_port}")
        print(f"💾 Memoria: {'✅' if self.memory.enabled else '❌'} ({self.memory.db_path})")
        print(f"🪵 Logs: {self.system.log_level} → {self.system.log_file}")
        print("="*50 + "\n")
