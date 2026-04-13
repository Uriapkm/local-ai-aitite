"""
Módulo de Visión - Abuelo IA
Detección básica del estado de la TV usando cámara web y procesamiento de imágenes
"""

import os
import time
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from datetime import datetime

# Imports para visión
try:
    import cv2
    import numpy as np
    _opencv_available = True
except ImportError:
    _opencv_available = False
    # No definir cv2 ni np para evitar errores en type hints


class TVStateDetector:
    """
    Detecta el estado de la TV usando visión computacional:
    - ¿Está encendida o apagada?
    - ¿Qué aplicación está mostrando? (YouTube, Netflix, TV normal)
    - ¿Hay contenido visible o pantalla negra/azul?
    """
    
    def __init__(self, 
                 camera_index: int = 0,
                 resolution: Tuple[int, int] = (1280, 720),
                 tv_roi: Optional[Tuple[int, int, int, int]] = None):
        """
        Inicializa el detector de estado de TV
        
        Args:
            camera_index: Índice de la cámara web
            resolution: Resolución de captura (ancho, alto)
            tv_roi: Región de interés (x, y, width, height) o None para toda la imagen
        """
        if not _opencv_available:
            raise ImportError("OpenCV no está instalado. Instala: pip install opencv-python")
        
        import cv2
        import numpy as np
        
        self.camera_index = camera_index
        self.resolution = resolution
        self.tv_roi = tv_roi
        
        self.camera = None
        self._camera_initialized = False
        
        # Inicializar cámara
        self._init_camera()
        
        print(f"👁️ TVStateDetector inicializado:")
        print(f"   - Cámara: índice {camera_index}")
        print(f"   - Resolución: {resolution[0]}x{resolution[1]}")
        print(f"   - ROI TV: {tv_roi or 'toda la imagen'}")
    
    def _init_camera(self):
        """Inicializa la cámara web"""
        try:
            self.camera = cv2.VideoCapture(self.camera_index)
            
            if not self.camera.isOpened():
                print(f"❌ No se pudo abrir la cámara {self.camera_index}")
                return
            
            # Configurar resolución
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
            
            # Esperar que la cámara se caliente
            time.sleep(0.5)
            
            # Verificar que funciona
            ret, frame = self.camera.read()
            if ret:
                self._camera_initialized = True
                actual_width = self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)
                actual_height = self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
                print(f"   ✅ Cámara lista ({actual_width:.0f}x{actual_height:.0f})")
            else:
                print("   ⚠️ Cámara no devuelve frames")
                
        except Exception as e:
            print(f"❌ Error inicializando cámara: {e}")
            self._camera_initialized = False
    
    def capture_frame(self) -> Optional[Any]:
        """
        Captura un frame de la cámara
        
        Returns:
            Frame como array numpy BGR, o None si falló
        """
        if not self._camera_initialized or self.camera is None:
            return None
        
        try:
            ret, frame = self.camera.read()
            
            if not ret:
                print("⚠️ No se pudo capturar frame")
                return None
            
            # Recortar a ROI si está definida
            if self.tv_roi:
                x, y, w, h = self.tv_roi
                frame = frame[y:y+h, x:x+w]
            
            return frame
            
        except Exception as e:
            print(f"❌ Error capturando frame: {e}")
            return None
    
    def save_frame(self, frame: Any, output_path: Optional[str] = None) -> str:
        """
        Guarda un frame como archivo de imagen
        
        Args:
            frame: Frame a guardar
            output_path: Ruta de salida (opcional, crea temporal si None)
            
        Returns:
            Ruta al archivo guardado
        """
        if output_path is None:
            temp_file = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
            output_path = temp_file.name
            temp_file.close()
        
        try:
            cv2.imwrite(output_path, frame)
            return output_path
        except Exception as e:
            print(f"❌ Error guardando frame: {e}")
            return ""
    
    def detect_tv_state(self) -> Dict[str, Any]:
        """
        Detecta el estado actual de la TV
        
        Returns:
            Dict con:
            - is_on: bool (TV encendida?)
            - brightness: float (0.0-1.0)
            - app_detected: str (youtube, netflix, tv, unknown)
            - is_black_screen: bool
            - confidence: float (0.0-1.0)
        """
        result = {
            "is_on": False,
            "brightness": 0.0,
            "app_detected": "unknown",
            "is_black_screen": False,
            "confidence": 0.0,
            "timestamp": datetime.now().isoformat(),
            "image_path": None
        }
        
        # Capturar frame
        frame = self.capture_frame()
        
        if frame is None:
            print("⚠️ No se pudo capturar imagen, asumiendo TV apagada")
            return result
        
        # Guardar frame para debugging/LLM
        temp_path = self.save_frame(frame)
        result["image_path"] = temp_path
        
        # Analizar brillo promedio
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        brightness = np.mean(gray) / 255.0
        result["brightness"] = float(brightness)
        
        # Detectar pantalla negra/azul (TV apagada o sin señal)
        is_dark = brightness < 0.15
        result["is_black_screen"] = is_dark
        
        # Si es muy oscura, probablemente apagada
        if is_dark:
            result["is_on"] = False
            result["confidence"] = 0.8
            return result
        
        # TV parece encendida
        result["is_on"] = True
        
        # Intentar detectar aplicación por colores/patrones
        app_detected = self._detect_app(frame)
        result["app_detected"] = app_detected
        
        # Calcular confianza basada en claridad de la imagen
        variance = np.var(gray)
        confidence = min(1.0, variance / 1000.0 + brightness * 0.3)
        result["confidence"] = float(confidence)
        
        return result
    
    def _detect_app(self, frame: Any) -> str:
        """
        Intenta detectar qué aplicación está mostrando la TV
        
        Args:
            frame: Frame BGR de la cámara
            
        Returns:
            Nombre de la app detectada o 'unknown'
        """
        # Convertir a HSV para análisis de color
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Calcular histograma de colores dominantes
        hist_b = cv2.calcHist([frame], [0], None, [32], [0, 256])
        hist_g = cv2.calcHist([frame], [1], None, [32], [0, 256])
        hist_r = cv2.calcHist([frame], [2], None, [32], [0, 256])
        
        # Normalizar
        total_pixels = frame.shape[0] * frame.shape[1]
        hist_b = hist_b / total_pixels
        hist_g = hist_g / total_pixels
        hist_r = hist_r / total_pixels
        
        # Detectar patrones de color característicos
        
        # YouTube: mucho rojo (#FF0000)
        red_percentage = float(hist_r[-1])  # Último bin = rojo intenso
        if red_percentage > 0.05:
            return "youtube"
        
        # Netflix: rojo oscuro/negro
        # (más difícil de distinguir, usar heurísticas adicionales)
        
        # TV normal: más variedad de colores
        color_variance = np.var(hist_r) + np.var(hist_g) + np.var(hist_b)
        if color_variance > 0.001:
            return "tv"
        
        return "unknown"
    
    def is_tv_on(self) -> bool:
        """
        Verificación rápida de si la TV está encendida
        
        Returns:
            True si encendida
        """
        state = self.detect_tv_state()
        return state["is_on"]
    
    def wait_for_state_change(self, 
                              previous_state: Dict[str, Any],
                              timeout: float = 10.0,
                              poll_interval: float = 0.5) -> Dict[str, Any]:
        """
        Espera a que el estado de la TV cambie
        
        Args:
            previous_state: Estado anterior para comparar
            timeout: Tiempo máximo de espera en segundos
            poll_interval: Intervalo entre comprobaciones
            
        Returns:
            Nuevo estado detectado
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            current_state = self.detect_tv_state()
            
            # Comparar estados
            if current_state["is_on"] != previous_state.get("is_on", not current_state["is_on"]):
                print(f"✅ Cambio de estado detectado: {'ON' if current_state['is_on'] else 'OFF'}")
                return current_state
            
            if current_state["app_detected"] != previous_state.get("app_detected", "unknown"):
                print(f"✅ App change detected: {current_state['app_detected']}")
                return current_state
            
            time.sleep(poll_interval)
        
        print("⏱️ Timeout esperando cambio de estado")
        return self.detect_tv_state()
    
    def close(self):
        """Libera recursos de la cámara"""
        if self.camera is not None:
            self.camera.release()
            self._camera_initialized = False
            print("📷 Cámara cerrada")


class SimpleTVStateDetector:
    """
    Versión simplificada sin OpenCV para sistemas sin cámara
    Usa heurísticas basadas en comandos IR enviados
    """
    
    def __init__(self):
        """Inicializa detector simplificado"""
        self._last_known_state = {
            "is_on": True,  # Asumir encendida por defecto
            "last_command": None,
            "last_update": datetime.now().isoformat()
        }
        
        print("👁️ SimpleTVStateDetector inicializado (sin cámara)")
    
    def detect_tv_state(self) -> Dict[str, Any]:
        """
        Devuelve estado estimado basado en últimos comandos
        
        Returns:
            Dict con estado estimado
        """
        return {
            "is_on": self._last_known_state["is_on"],
            "brightness": 0.5 if self._last_known_state["is_on"] else 0.0,
            "app_detected": "unknown",
            "is_black_screen": not self._last_known_state["is_on"],
            "confidence": 0.5,  # Baja confianza porque es estimado
            "timestamp": datetime.now().isoformat(),
            "image_path": None,
            "note": "Estado estimado sin visión real"
        }
    
    def update_from_ir_command(self, command: str):
        """
        Actualiza estado estimado basado en comando IR enviado
        
        Args:
            command: Comando IR enviado
        """
        self._last_known_state["last_command"] = command
        self._last_known_state["last_update"] = datetime.now().isoformat()
        
        if command == "POWER":
            self._last_known_state["is_on"] = not self._last_known_state["is_on"]
        elif command in ["POWER_ON"]:
            self._last_known_state["is_on"] = True
        elif command in ["POWER_OFF"]:
            self._last_known_state["is_on"] = False
        
        print(f"   📡 Estado TV actualizado: {'ON' if self._last_known_state['is_on'] else 'OFF'}")
    
    def is_tv_on(self) -> bool:
        """Devuelve si la TV está estimada como encendida"""
        return self._last_known_state["is_on"]
    
    def close(self):
        """No hace nada (sin recursos que liberar)"""
        pass


# Factory function para crear detector apropiado
def create_tv_state_detector(use_camera: bool = True,
                            camera_index: int = 0,
                            resolution: Tuple[int, int] = (1280, 720)) -> Any:
    """
    Crea un detector de estado de TV
    
    Args:
        use_camera: Si True, usa cámara; si False, usa detector simplificado
        camera_index: Índice de cámara (solo si use_camera=True)
        resolution: Resolución de captura (solo si use_camera=True)
        
    Returns:
        Instancia de TVStateDetector o SimpleTVStateDetector
    """
    if use_camera and _opencv_available:
        try:
            return TVStateDetector(
                camera_index=camera_index,
                resolution=resolution
            )
        except Exception as e:
            print(f"⚠️ Falló inicialización con cámara: {e}")
            print("   Usando detector simplificado...")
            return SimpleTVStateDetector()
    else:
        if not _opencv_available:
            print("⚠️ OpenCV no disponible, usando detector simplificado")
        return SimpleTVStateDetector()


# Punto de entrada para testing
if __name__ == "__main__":
    print("🧪 Testing TV State Detection...\n")
    
    # Test con detector simplificado (siempre disponible)
    print("=== Test SimpleTVStateDetector ===\n")
    
    detector = SimpleTVStateDetector()
    
    print("Estado inicial:")
    state = detector.detect_tv_state()
    for key, value in state.items():
        print(f"   - {key}: {value}")
    
    print("\nEnviando comando POWER...")
    detector.update_from_ir_command("POWER")
    
    print("\nEstado después de POWER:")
    state = detector.detect_tv_state()
    for key, value in state.items():
        if value is not None:
            print(f"   - {key}: {value}")
    
    print("\n✅ Test completado")
    
    # Test con cámara (si OpenCV está disponible)
    if _opencv_available:
        print("\n\n=== Test TVStateDetector (con cámara) ===\n")
        
        try:
            cam_detector = TVStateDetector(camera_index=0)
            
            print("\nCapturando frame y detectando estado...")
            state = cam_detector.detect_tv_state()
            
            print("\nEstado detectado:")
            for key, value in state.items():
                if value is not None:
                    print(f"   - {key}: {value}")
            
            cam_detector.close()
            print("\n✅ Test con cámara completado")
            
        except Exception as e:
            print(f"\n⚠️ Test con cámara falló: {e}")
            print("   (Esto es normal si no hay cámara conectada)")
