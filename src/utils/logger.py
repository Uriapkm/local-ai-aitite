"""
Configuración centralizada de logging rotativo para Abuelo IA
Previene llenado del disco con rotación automática de logs
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from datetime import datetime
import json


def setup_logger(
    name: str,
    log_dir: str = "./logs",
    level: int = logging.INFO,
    max_bytes: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5,
    console_output: bool = True,
    json_format: bool = False
) -> logging.Logger:
    """
    Configura un logger con rotación automática
    
    Args:
        name: Nombre del logger (usualmente __name__)
        log_dir: Directorio para almacenar logs
        level: Nivel de logging
        max_bytes: Tamaño máximo antes de rotar
        backup_count: Número de archivos backup a mantener
        console_output: Si True, muestra logs en consola
        json_format: Si True, usa formato JSON estructurado
    
    Returns:
        Logger configurado
    """
    
    # Crear directorio de logs si no existe
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    # Crear logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Evitar duplicación de handlers
    if logger.handlers:
        return logger
    
    # Formato del log
    if json_format:
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    # Handler rotativo para archivo
    log_file = log_path / f"{name}.log"
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Handler para consola (opcional)
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger


class JsonFormatter(logging.Formatter):
    """Formatter JSON para logs estructurados - útil para ELK/Splunk"""
    
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data, ensure_ascii=False)


# Loggers pre-configurados para los módulos principales

def get_main_logger() -> logging.Logger:
    """Obtiene el logger principal del agente"""
    return setup_logger("abuelo_agent")


def get_llm_logger() -> logging.Logger:
    """Obtiene el logger para operaciones del LLM"""
    return setup_logger("llm_operations")


def get_audio_logger() -> logging.Logger:
    """Obtiene el logger para operaciones de audio"""
    return setup_logger("audio_operations")


def get_health_logger() -> logging.Logger:
    """Obtiene el logger para monitoring y health checks"""
    return setup_logger("health_monitor")


def get_vision_logger() -> logging.Logger:
    """Obtiene el logger para operaciones de visión"""
    return setup_logger("vision_operations")


def get_hardware_logger() -> logging.Logger:
    """Obtiene el logger para hardware (Arduino/IR)"""
    return setup_logger("hardware_controller")


# Ejemplo de uso y testing
if __name__ == "__main__":
    print("🧪 Testing sistema de logging rotativo...\n")
    
    logger = get_main_logger()
    
    # Test diferentes niveles de log
    logger.debug("🔍 Este es un mensaje DEBUG (solo si level=DEBUG)")
    logger.info("🚀 Iniciando sistema de logging rotativo")
    logger.info("Este es un mensaje INFO estándar")
    logger.warning("⚠️ Este es un mensaje WARNING")
    logger.error("❌ Este es un mensaje ERROR")
    
    # Test logging de excepción
    try:
        raise ValueError("Error de prueba para logging")
    except Exception as e:
        logger.exception("💥 Excepción capturada y loggeada")
    
    # Test logger secundario
    llm_logger = get_llm_logger()
    llm_logger.info("🧠 Operación LLM completada")
    
    audio_logger = get_audio_logger()
    audio_logger.info("🎵 Reproducción de audio iniciada")
    
    health_logger = get_health_logger()
    health_logger.info("🏥 Health check: Sistema OK")
    
    print(f"\n✅ Logs guardados en: ./logs/")
    print(f"   Archivos creados:")
    
    import os
    log_files = sorted(Path("./logs").glob("*.log"))
    for lf in log_files:
        size = lf.stat().st_size
        print(f"   - {lf.name} ({size} bytes)")
    
    print(f"\n📋 Configuración:")
    print(f"   - Tamaño máximo por archivo: 10 MB")
    print(f"   - Backups mantenidos: 5")
    print(f"   - Espacio máximo total: ~50 MB por módulo")
    print(f"\n💡 Comandos útiles:")
    print(f"   tail -f logs/abuelo_agent.log     # Ver logs en tiempo real")
    print(f"   grep ERROR logs/*.log             # Buscar errores")
    print(f"   du -sh logs/                      # Ver tamaño total")
