"""
Sistema de Monitoring y Health Checks para Abuelo IA
Verifica el estado de todos los componentes y realiza auto-recovery si es necesario
"""

import os
import time
import threading
import logging
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from pathlib import Path

# Importar setup_logger para logging rotativo
from src.utils.logger import setup_logger

# Configurar logger rotativo
logger = setup_logger("health_monitor")


class HealthCheckResult:
    """Resultado de un health check individual"""
    
    def __init__(self, component: str, is_healthy: bool, message: str = "", details: Optional[Dict] = None):
        self.component = component
        self.is_healthy = is_healthy
        self.message = message
        self.details = details or {}
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "component": self.component,
            "healthy": self.is_healthy,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat()
        }


class ComponentHealthMonitor:
    """Monitor de salud para un componente específico"""
    
    def __init__(self, name: str, check_function: Callable[[], bool], 
                 recovery_function: Optional[Callable[[], bool]] = None,
                 max_failures_before_recovery: int = 3,
                 check_interval_seconds: int = 30):
        self.name = name
        self.check_function = check_function
        self.recovery_function = recovery_function
        self.max_failures = max_failures_before_recovery
        self.check_interval = check_interval_seconds
        
        self.consecutive_failures = 0
        self.last_check_time: Optional[datetime] = None
        self.last_check_result: Optional[bool] = None
        self.is_monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
    
    def check(self) -> HealthCheckResult:
        """Ejecuta el health check del componente"""
        try:
            self.last_check_time = datetime.now()
            is_healthy = self.check_function()
            self.last_check_result = is_healthy
            
            if is_healthy:
                self.consecutive_failures = 0
                return HealthCheckResult(
                    component=self.name,
                    is_healthy=True,
                    message="Componente saludable"
                )
            else:
                self.consecutive_failures += 1
                message = f"Fallo detectado ({self.consecutive_failures}/{self.max_failures})"
                
                # Intentar auto-recovery si superó el umbral
                if self.consecutive_failures >= self.max_failures and self.recovery_function:
                    logger.warning(f"🔧 Intentando auto-recovery para {self.name}...")
                    recovery_success = self.recovery_function()
                    
                    if recovery_success:
                        self.consecutive_failures = 0
                        return HealthCheckResult(
                            component=self.name,
                            is_healthy=True,
                            message="Auto-recovery exitoso",
                            details={"recovered": True}
                        )
                    else:
                        return HealthCheckResult(
                            component=self.name,
                            is_healthy=False,
                            message="Auto-recovery fallido",
                            details={"recovered": False}
                        )
                
                return HealthCheckResult(
                    component=self.name,
                    is_healthy=False,
                    message=message,
                    details={"consecutive_failures": self.consecutive_failures}
                )
                
        except Exception as e:
            self.consecutive_failures += 1
            logger.error(f"❌ Error en health check de {self.name}: {e}")
            return HealthCheckResult(
                component=self.name,
                is_healthy=False,
                message=f"Error: {str(e)}",
                details={"exception": str(e)}
            )
    
    def start_monitoring(self):
        """Inicia el monitoring en un thread separado"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        
        def monitor_loop():
            logger.info(f"🔍 Iniciando monitoring para {self.name}")
            while self.is_monitoring:
                result = self.check()
                if not result.is_healthy:
                    logger.warning(f"⚠️ {self.name}: {result.message}")
                time.sleep(self.check_interval)
        
        self._monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self._monitor_thread.start()
    
    def stop_monitoring(self):
        """Detiene el monitoring"""
        self.is_monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5.0)


class SystemHealthMonitor:
    """
    Monitor de salud del sistema completo
    Coordina todos los monitores de componentes y proporciona dashboard de estado
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.monitors: Dict[str, ComponentHealthMonitor] = {}
        self.is_running = False
        self._dashboard_thread: Optional[threading.Thread] = None
        self.config_path = config_path
        
        # Umbrales de configuración
        self.check_interval = 30  # segundos
        self.dashboard_update_interval = 60  # segundos
        self.auto_recovery_enabled = True
        
        # Historial de health checks
        self.history: List[HealthCheckResult] = []
        self.max_history_size = 100
        
        logger.info("🏥 SystemHealthMonitor inicializado")
    
    def register_component(self, name: str, check_function: Callable[[], bool],
                          recovery_function: Optional[Callable[[], bool]] = None,
                          check_interval: int = 30):
        """Registra un componente para monitoring"""
        monitor = ComponentHealthMonitor(
            name=name,
            check_function=check_function,
            recovery_function=recovery_function,
            check_interval_seconds=check_interval
        )
        self.monitors[name] = monitor
        logger.info(f"✅ Componente registrado: {name}")
    
    def check_all(self) -> Dict[str, HealthCheckResult]:
        """Ejecuta health checks en todos los componentes"""
        results = {}
        for name, monitor in self.monitors.items():
            result = monitor.check()
            results[name] = result
            self._add_to_history(result)
        return results
    
    def get_system_status(self) -> Dict[str, Any]:
        """Obtiene el estado actual del sistema"""
        results = self.check_all()
        
        healthy_count = sum(1 for r in results.values() if r.is_healthy)
        total_count = len(results)
        
        status = "HEALTHY" if healthy_count == total_count else "DEGRADED"
        if healthy_count == 0 and total_count > 0:
            status = "CRITICAL"
        
        return {
            "status": status,
            "healthy_components": healthy_count,
            "total_components": total_count,
            "health_percentage": (healthy_count / total_count * 100) if total_count > 0 else 0,
            "components": {name: result.to_dict() for name, result in results.items()},
            "timestamp": datetime.now().isoformat()
        }
    
    def _add_to_history(self, result: HealthCheckResult):
        """Añade resultado al historial"""
        self.history.append(result)
        if len(self.history) > self.max_history_size:
            self.history.pop(0)
    
    def start_dashboard(self):
        """Inicia el dashboard de monitoring en segundo plano"""
        if self.is_running:
            return
        
        self.is_running = True
        
        # Iniciar todos los monitores individuales
        for monitor in self.monitors.values():
            monitor.start_monitoring()
        
        # Iniciar thread del dashboard
        def dashboard_loop():
            logger.info("📊 Dashboard de monitoring iniciado")
            while self.is_running:
                status = self.get_system_status()
                
                # Log periódico del estado
                if status["status"] != "HEALTHY":
                    logger.warning(f"📊 ESTADO DEL SISTEMA: {status['status']} - "
                                 f"{status['healthy_components']}/{status['total_components']} componentes OK")
                else:
                    logger.debug(f"📊 Sistema saludable: {status['health_percentage']:.0f}%")
                
                time.sleep(self.dashboard_update_interval)
        
        self._dashboard_thread = threading.Thread(target=dashboard_loop, daemon=True)
        self._dashboard_thread.start()
    
    def stop_dashboard(self):
        """Detiene el dashboard"""
        self.is_running = False
        
        # Detener todos los monitores
        for monitor in self.monitors.values():
            monitor.stop_monitoring()
        
        if self._dashboard_thread:
            self._dashboard_thread.join(timeout=5.0)
        
        logger.info("🛑 Dashboard detenido")


# Funciones helper para checks comunes del sistema Abuelo IA

def check_ollama_connection(host: str = "http://localhost:11434") -> bool:
    """Verifica conexión con Ollama"""
    try:
        import requests
        response = requests.get(f"{host}/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False


def check_audio_device(sample_rate: int = 16000) -> bool:
    """Verifica dispositivo de audio"""
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        return len(devices) > 0
    except:
        return False


def check_serial_port(port: str = "/dev/ttyUSB0") -> bool:
    """Verifica puerto serial Arduino"""
    try:
        import serial
        ser = serial.Serial(port, baudrate=9600, timeout=1)
        ser.close()
        return True
    except:
        return False


def check_disk_space(path: str = "/", min_gb: float = 1.0) -> bool:
    """Verifica espacio en disco"""
    try:
        import shutil
        total, used, free = shutil.disk_usage(path)
        free_gb = free / (1024**3)
        return free_gb >= min_gb
    except:
        return False


def check_memory_usage(max_percent: float = 90.0) -> bool:
    """Verifica uso de memoria RAM"""
    try:
        import psutil
        percent = psutil.virtual_memory().percent
        return percent < max_percent
    except:
        return False


def restart_ollama_service() -> bool:
    """Intenta reiniciar el servicio de Ollama"""
    try:
        import subprocess
        # En Bazzite/Systemd
        subprocess.run(["systemctl", "--user", "restart", "ollama"], timeout=10)
        time.sleep(2)
        return check_ollama_connection()
    except:
        return False


def restart_audio_service() -> bool:
    """Intenta reiniciar el servicio de audio PipeWire"""
    try:
        import subprocess
        subprocess.run(["systemctl", "--user", "restart", "pipewire"], timeout=10)
        time.sleep(2)
        return check_audio_device()
    except:
        return False


# Punto de entrada para testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("🧪 Testing SystemHealthMonitor...\n")
    
    # Crear monitor
    monitor = SystemHealthMonitor()
    
    # Registrar componentes de ejemplo
    monitor.register_component(
        name="Ollama",
        check_function=lambda: check_ollama_connection(),
        recovery_function=restart_ollama_service,
        check_interval=30
    )
    
    monitor.register_component(
        name="Audio",
        check_function=lambda: check_audio_device(),
        recovery_function=restart_audio_service,
        check_interval=30
    )
    
    monitor.register_component(
        name="Disk Space",
        check_function=lambda: check_disk_space(),
        check_interval=60
    )
    
    # Ejecutar check manual
    print("📋 Ejecutando health checks...\n")
    status = monitor.get_system_status()
    
    print(f"Estado del sistema: {status['status']}")
    print(f"Componentes saludables: {status['healthy_components']}/{status['total_components']}")
    print(f"Porcentaje: {status['health_percentage']:.0f}%\n")
    
    for comp_name, comp_data in status['components'].items():
        icon = "✅" if comp_data['healthy'] else "❌"
        print(f"{icon} {comp_name}: {comp_data['message']}")
    
    print("\n✅ Test completado")
