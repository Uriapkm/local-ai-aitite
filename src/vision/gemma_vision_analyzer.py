"""
Módulo de Visión Multimodal - Abuelo IA
Integración con Gemma 4 para análisis avanzado de pantalla TV
"""

import os
import time
import base64
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from datetime import datetime

try:
    import cv2
    import numpy as np
    _opencv_available = True
except ImportError:
    _opencv_available = False


class GemmaVisionAnalyzer:
    """
    Analizador de pantalla TV usando Gemma 4 multimodal:
    - Detecta aplicación específica (YouTube, Netflix, Prime, Disney+, etc.)
    - Identifica contenido (película, serie, menú, anuncios)
    - Detecta problemas (pantalla azul, sin señal, congelada)
    - OCR para textos visibles (títulos, menús)
    """
    
    def __init__(self, 
                 ollama_host: str = "http://localhost:11434",
                 model: str = "gemma4",
                 tv_state_detector=None):
        """
        Inicializa el analizador de visión con Gemma
        
        Args:
            ollama_host: URL del servidor Ollama
            model: Modelo multimodal a usar
            tv_state_detector: Instancia opcional de TVStateDetector
        """
        self.ollama_host = ollama_host
        self.model = model
        self.tv_state_detector = tv_state_detector
        
        # Importar cliente Ollama
        try:
            from src.utils.ollama_client import OllamaClient
            self.ollama_client = OllamaClient(host=ollama_host)
        except Exception as e:
            print(f"❌ Error inicializando cliente Ollama: {e}")
            self.ollama_client = None
        
        print(f"👁️‍🗨️ GemmaVisionAnalyzer inicializado:")
        print(f"   - Modelo: {model}")
        print(f"   - Ollama: {ollama_host}")
        print(f"   - OpenCV: {'disponible' if _opencv_available else 'no disponible'}")
    
    def capture_and_analyze(self, 
                           camera_index: int = 0,
                           save_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Captura imagen de la cámara y analiza con Gemma
        
        Args:
            camera_index: Índice de cámara web
            save_path: Ruta para guardar imagen (opcional)
            
        Returns:
            Dict con análisis completo
        """
        result = {
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "image_path": None,
            "tv_state": {},
            "gemma_analysis": {},
            "error": None
        }
        
        # Paso 1: Capturar frame con detector básico
        if self.tv_state_detector is None:
            from src.vision.tv_state_detector import create_tv_state_detector
            self.tv_state_detector = create_tv_state_detector(
                use_camera=True,
                camera_index=camera_index
            )
        
        # Obtener estado básico
        basic_state = self.tv_state_detector.detect_tv_state()
        result["tv_state"] = basic_state
        result["image_path"] = basic_state.get("image_path")
        
        # Si no hay imagen, retornar error
        image_path = basic_state.get("image_path")
        if not image_path or not os.path.exists(image_path):
            result["error"] = "No se pudo capturar imagen"
            return result
        
        # Paso 2: Analizar con Gemma si está disponible
        if self.ollama_client is None:
            result["error"] = "Cliente Ollama no disponible"
            return result
        
        # Verificar que el modelo existe
        try:
            models = self.ollama_client.list_models()
            if not any(model.get("name", "").startswith("gemma") for model in models):
                result["error"] = f"Modelo {self.model} no encontrado en Ollama"
                print(f"⚠️ Modelos disponibles: {[m.get('name') for m in models]}")
                return result
        except Exception as e:
            result["error"] = f"Error verificando modelos: {e}"
            return result
        
        # Paso 3: Enviar imagen a Gemma para análisis
        try:
            gemma_result = self._analyze_with_gemma(image_path)
            result["gemma_analysis"] = gemma_result
            result["success"] = True
            
            # Guardar ruta si se especificó
            if save_path and save_path != image_path:
                import shutil
                shutil.copy(image_path, save_path)
                result["image_path"] = save_path
            
        except Exception as e:
            result["error"] = f"Error en análisis Gemma: {e}"
        
        return result
    
    def _analyze_with_gemma(self, image_path: str) -> Dict[str, Any]:
        """
        Envía imagen a Gemma para análisis detallado
        
        Args:
            image_path: Ruta a la imagen
            
        Returns:
            Dict con análisis de Gemma
        """
        # Leer imagen y codificar a base64
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")
        
        # Prompt estructurado para análisis de TV
        prompt = """
Analiza esta imagen de una pantalla de televisión y proporciona información estructurada en formato JSON.

Responde EXACTAMENTE con este formato JSON, sin texto adicional:
{
    "app_detected": "youtube|netflix|prime_video|disney_plus|hbo_max|movistar_plus|davinci_resolve|tv_normal|menu_system|unknown",
    "content_type": "movie|series|live_tv|advertisement|menu|video_clip|music|game|unknown",
    "is_menu_visible": true/false,
    "menu_items": ["item1", "item2"],
    "text_visible": "texto principal visible o null",
    "dominant_colors": ["color1", "color2"],
    "has_people": true/false,
    "is_sports": true/false,
    "is_cartoon": true/false,
    "screen_quality": "good|blurry|dark|glare|normal",
    "issues_detected": ["issue1", "issue2"] o [],
    "confidence": 0.0-1.0
}

Reglas:
- app_detected: identifica la aplicación por logos, interfaz o colores característicos
- content_type: tipo de contenido que se está mostrando
- menu_items: lista elementos del menú si es visible
- text_visible: título de película/serie o texto prominente
- dominant_colors: 2-3 colores principales
- issues_detected: problemas como "blue_screen", "no_signal", "frozen", "black_bars"
- confidence: tu confianza en el análisis (0.0-1.0)
"""
        
        # Enviar solicitud multimodal
        response = self.ollama_client.generate_multimodal(
            model=self.model,
            prompt=prompt,
            image_base64=image_data,
            stream=False
        )
        
        # Parsear respuesta JSON
        if response and "response" in response:
            import json
            try:
                # Extraer JSON de la respuesta
                response_text = response["response"]
                
                # Intentar encontrar JSON en la respuesta
                start_idx = response_text.find("{")
                end_idx = response_text.rfind("}") + 1
                
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = response_text[start_idx:end_idx]
                    parsed = json.loads(json_str)
                    return {
                        "success": True,
                        "analysis": parsed,
                        "raw_response": response_text,
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    return {
                        "success": False,
                        "error": "No se encontró JSON válido en respuesta",
                        "raw_response": response_text
                    }
                    
            except json.JSONDecodeError as e:
                return {
                    "success": False,
                    "error": f"Error parsing JSON: {e}",
                    "raw_response": response.get("response", "")[:500]
                }
        else:
            return {
                "success": False,
                "error": "Respuesta vacía de Ollama",
                "raw_response": str(response)
            }
    
    def detect_app_quick(self, timeout: float = 5.0) -> str:
        """
        Detección rápida de aplicación (fallback sin Gemma)
        
        Args:
            timeout: Tiempo máximo de espera
            
        Returns:
            Nombre de app detectada o 'unknown'
        """
        if self.tv_state_detector is None:
            return "unknown"
        
        state = self.tv_state_detector.detect_tv_state()
        app = state.get("app_detected", "unknown")
        
        # Si el detector básico ya identificó YouTube, confiar
        if app == "youtube":
            return "youtube"
        
        # Si tenemos Gemma, usarlo para mejor detección
        if self.ollama_client:
            try:
                result = self.capture_and_analyze()
                if result["success"] and result["gemma_analysis"].get("success"):
                    return result["gemma_analysis"]["analysis"].get("app_detected", "unknown")
            except Exception:
                pass
        
        return app
    
    def wait_for_app_change(self, 
                           current_app: str,
                           timeout: float = 30.0,
                           poll_interval: float = 2.0) -> str:
        """
        Espera a que cambie la aplicación en pantalla
        
        Args:
            current_app: Aplicación actual
            timeout: Tiempo máximo de espera
            poll_interval: Intervalo entre comprobaciones
            
        Returns:
            Nueva aplicación detectada
        """
        start_time = time.time()
        last_app = current_app
        
        while time.time() - start_time < timeout:
            new_app = self.detect_app_quick()
            
            if new_app != last_app and new_app != "unknown":
                print(f"✅ App change detected: {current_app} → {new_app}")
                return new_app
            
            time.sleep(poll_interval)
        
        print(f"⏱️ Timeout esperando cambio de app (sigue siendo {last_app})")
        return last_app
    
    def close(self):
        """Libera recursos"""
        if self.tv_state_detector:
            self.tv_state_detector.close()


# Factory function
def create_vision_analyzer(use_gemma: bool = True,
                          ollama_host: str = "http://localhost:11434",
                          model: str = "gemma4",
                          camera_index: int = 0) -> Any:
    """
    Crea un analizador de visión
    
    Args:
        use_gemma: Si True, usa Gemma; si False, solo detector básico
        ollama_host: URL de Ollama
        model: Modelo Gemma
        camera_index: Índice de cámara
        
    Returns:
        Instancia de GemmaVisionAnalyzer o TVStateDetector
    """
    from src.vision.tv_state_detector import create_tv_state_detector
    
    tv_detector = create_tv_state_detector(
        use_camera=True,
        camera_index=camera_index
    )
    
    if use_gemma:
        try:
            analyzer = GemmaVisionAnalyzer(
                ollama_host=ollama_host,
                model=model,
                tv_state_detector=tv_detector
            )
            return analyzer
        except Exception as e:
            print(f"⚠️ Falló inicialización con Gemma: {e}")
            print("   Usando detector básico...")
            return tv_detector
    else:
        return tv_detector


# Testing
if __name__ == "__main__":
    print("🧪 Testing Gemma Vision Analyzer...\n")
    
    # Test básico sin Gemma
    print("=== Test TVStateDetector ===\n")
    detector = create_tv_state_detector(use_camera=False)
    state = detector.detect_tv_state()
    print(f"Estado: {state}")
    
    # Test con Gemma (si está disponible)
    print("\n=== Test GemmaVisionAnalyzer ===\n")
    try:
        analyzer = GemmaVisionAnalyzer(
            ollama_host="http://localhost:11434",
            model="gemma4"
        )
        
        print("\nCapturando y analizando...")
        result = analyzer.capture_and_analyze(camera_index=0)
        
        print(f"\nResultado:")
        print(f"   - Success: {result['success']}")
        print(f"   - Image: {result['image_path']}")
        print(f"   - TV State: {result['tv_state']}")
        
        if result.get("gemma_analysis"):
            print(f"   - Gemma Analysis: {result['gemma_analysis']}")
        
        if result.get("error"):
            print(f"   - Error: {result['error']}")
        
        analyzer.close()
        
    except Exception as e:
        print(f"⚠️ Test con Gemma falló: {e}")
        print("   (Normal si Ollama no está corriendo o Gemma4 no instalado)")
