"""
Cliente Ollama para Gemma 4
Maneja la comunicación con el LLM local vía API REST
"""

import requests
import json
from typing import Optional, Dict, Any, List, Generator
from pathlib import Path


class OllamaClient:
    """
    Cliente para interactuar con Ollama API
    Soporta modelos de texto y visión multimodal
    """
    
    def __init__(self, 
                 host: str = "http://localhost:11434",
                 model: str = "gemma4:4b-instruct-q4_K_M",
                 timeout: int = 120):
        """
        Inicializa cliente Ollama
        
        Args:
            host: URL del servidor Ollama
            model: Nombre del modelo a usar
            timeout: Timeout máximo en segundos para respuestas
        """
        self.host = host.rstrip('/')
        self.model = model
        self.timeout = timeout
        
        # Verificar conexión inicial
        self._check_connection()
        
        print(f"🧠 OllamaClient inicializado:")
        print(f"   - Host: {self.host}")
        print(f"   - Modelo: {self.model}")
    
    def _check_connection(self) -> bool:
        """Verifica que Ollama esté disponible"""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            if response.status_code == 200:
                print("   ✅ Conexión con Ollama OK")
                return True
            else:
                print(f"   ⚠️ Ollama respondió con status {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print(f"   ❌ No se pudo conectar a Ollama en {self.host}")
            print("      Asegúrate de que Ollama esté ejecutándose: ollama serve")
            return False
        except Exception as e:
            print(f"   ❌ Error verificando Ollama: {e}")
            return False
    
    def is_available(self) -> bool:
        """Verifica si Ollama está disponible"""
        return self._check_connection()
    
    def list_models(self) -> List[str]:
        """Lista modelos disponibles en Ollama"""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                models = [m['name'] for m in data.get('models', [])]
                return models
            return []
        except Exception as e:
            print(f"❌ Error listando modelos: {e}")
            return []
    
    def generate(self, 
                 prompt: str, 
                 system_prompt: Optional[str] = None,
                 context: Optional[List[Dict[str, str]]] = None,
                 temperature: float = 0.7,
                 max_tokens: int = 512,
                 stream: bool = False) -> Dict[str, Any]:
        """
        Genera respuesta del LLM
        
        Args:
            prompt: Prompt del usuario
            system_prompt: Prompt de sistema (instrucciones de comportamiento)
            context: Historial de conversación (lista de dicts con 'role' y 'content')
            temperature: Temperatura (0.0-2.0)
            max_tokens: Máximo de tokens en respuesta
            stream: Si True, devuelve generador para streaming
            
        Returns:
            Dict con 'response', 'done', 'total_duration', etc.
        """
        # Construir payload
        messages = []
        
        # Agregar system prompt si existe
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Agregar contexto/historial
        if context:
            messages.extend(context)
        
        # Agregar prompt actual
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        try:
            if stream:
                return self._generate_stream(payload)
            else:
                response = requests.post(
                    f"{self.host}/api/chat",
                    json=payload,
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.json()
                
        except requests.exceptions.Timeout:
            print(f"❌ Timeout esperando respuesta de Ollama ({self.timeout}s)")
            return {"error": "timeout", "response": ""}
        except requests.exceptions.RequestException as e:
            print(f"❌ Error en petición a Ollama: {e}")
            return {"error": str(e), "response": ""}
    
    def _generate_stream(self, payload: Dict) -> Generator[Dict[str, Any], None, None]:
        """Generador para streaming de respuestas"""
        try:
            with requests.post(
                f"{self.host}/api/chat",
                json=payload,
                stream=True,
                timeout=self.timeout
            ) as response:
                response.raise_for_status()
                
                for line in response.iter_lines():
                    if line:
                        try:
                            chunk = json.loads(line)
                            yield chunk
                        except json.JSONDecodeError:
                            continue
                            
        except Exception as e:
            print(f"❌ Error en streaming: {e}")
            yield {"error": str(e)}
    
    def generate_multimodal(self,
                           model: str,
                           prompt: str,
                           image_base64: str,
                           system_prompt: Optional[str] = None,
                           temperature: float = 0.7,
                           max_tokens: int = 512,
                           stream: bool = False) -> Dict[str, Any]:
        """
        Genera respuesta con entrada multimodal (texto + imagen)
        
        Args:
            model: Modelo a usar
            prompt: Prompt del usuario
            image_base64: Imagen en base64
            system_prompt: Prompt de sistema
            temperature: Temperatura
            max_tokens: Máximo de tokens
            stream: Si True, devuelve generador
            
        Returns:
            Dict con respuesta del modelo
        """
        # Construir mensaje con imagen
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({
            "role": "user",
            "content": prompt,
            "images": [image_base64]
        })
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        try:
            if stream:
                return self._generate_stream(payload)
            else:
                response = requests.post(
                    f"{self.host}/api/chat",
                    json=payload,
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.json()
            
        except requests.exceptions.Timeout:
            print(f"❌ Timeout esperando respuesta de Ollama ({self.timeout}s)")
            return {"error": "timeout", "response": ""}
        except Exception as e:
            print(f"❌ Error en generación multimodal: {e}")
            return {"error": str(e), "response": ""}
    
    def generate_with_image(self,
                           prompt: str,
                           image_path: str,
                           system_prompt: Optional[str] = None,
                           temperature: float = 0.7,
                           max_tokens: int = 512) -> Dict[str, Any]:
        """
        Genera respuesta con entrada multimodal (texto + imagen)
        Método legacy, usar generate_multimodal en su lugar
        
        Args:
            prompt: Prompt del usuario
            image_path: Ruta a la imagen
            system_prompt: Prompt de sistema
            temperature: Temperatura
            max_tokens: Máximo de tokens
            
        Returns:
            Dict con respuesta del modelo
        """
        # Leer imagen y convertir a base64
        import base64
        
        try:
            with open(image_path, 'rb') as img_file:
                image_base64 = base64.b64encode(img_file.read()).decode('utf-8')
        except Exception as e:
            print(f"❌ Error leyendo imagen: {e}")
            return {"error": str(e), "response": ""}
        
        return self.generate_multimodal(
            model=self.model,
            prompt=prompt,
            image_base64=image_base64,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )
    
    def pull_model(self, model_name: Optional[str] = None) -> bool:
        """
        Descarga un modelo desde Ollama library
        
        Args:
            model_name: Nombre del modelo (usa el default si None)
            
        Returns:
            True si éxito, False si fallo
        """
        model = model_name or self.model
        
        print(f"⏳ Descargando modelo '{model}'...")
        
        try:
            response = requests.post(
                f"{self.host}/api/pull",
                json={"name": model},
                stream=True,
                timeout=600  # 10 minutos para descarga
            )
            response.raise_for_status()
            
            # Mostrar progreso
            for line in response.iter_lines():
                if line:
                    try:
                        chunk = json.loads(line)
                        status = chunk.get('status', '')
                        completed = chunk.get('completed', 0)
                        total = chunk.get('total', 0)
                        
                        if total > 0:
                            percent = (completed / total) * 100
                            print(f"   📥 {status}: {percent:.1f}%")
                        else:
                            print(f"   {status}")
                            
                    except json.JSONDecodeError:
                        continue
            
            print(f"✅ Modelo '{model}' descargado")
            return True
            
        except Exception as e:
            print(f"❌ Error descargando modelo: {e}")
            return False
    
    def check_model_exists(self, model_name: Optional[str] = None) -> bool:
        """Verifica si un modelo está instalado localmente"""
        models = self.list_models()
        model = model_name or self.model
        
        # Buscar coincidencia exacta o parcial
        for m in models:
            if m == model or m.startswith(model.split(':')[0]):
                return True
        
        return False


# Funciones utilitarias
def build_system_prompt(personality: str = "abuelo") -> str:
    """
    Construye prompt de sistema según personalidad
    
    Args:
        personality: Tipo de personalidad ("abuelo", "asistente", etc.)
        
    Returns:
        String con el system prompt
    """
    if personality == "abuelo":
        return """Eres un asistente IA amable y paciente diseñado para ayudar a personas mayores 
a usar su televisión y computadora. 

Características:
- Habla de forma clara, simple y directa
- Sé muy paciente y repetitivo si es necesario
- Usa un tono cálido y familiar
- Explica los pasos uno por uno
- Nunca uses jerga técnica sin explicarla
- Ofrece ayuda adicional al final

Tu objetivo principal es:
1. Ayudar a cambiar canales y configurar la TV
2. Buscar y reproducir videos en YouTube
3. Resolver problemas técnicos simples
4. Hacer compañía y conversar

Siempre confirma que el usuario entendió antes de continuar."""
    
    elif personality == "asistente":
        return """Eres un asistente IA útil, respetuoso y eficiente.
Responde de forma clara y concisa.
Ofrece ayuda relevante sin ser intrusivo."""
    
    else:
        return "Eres un asistente IA útil y amable."


def parse_llm_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parsea respuesta del LLM para extraer acciones
    Ahora soporta tanto JSON estructurado como texto libre (fallback)
    
    Args:
        response: Respuesta cruda de Ollama
        
    Returns:
        Dict con 'text', 'action', 'parameters'
    """
    import json
    
    text = response.get('message', {}).get('content', '')
    action = "REPLY"
    parameters = {}
    
    # Intento 1: Buscar JSON explícito en la respuesta
    try:
        # Buscar bloques JSON entre llaves
        import re
        json_pattern = r'\{[^{}]*"action"[^{}]*\}'
        json_matches = re.findall(json_pattern, text, re.DOTALL)
        
        if json_matches:
            # Intentar parsear el primer JSON encontrado
            for json_str in json_matches:
                try:
                    parsed_json = json.loads(json_str)
                    action = parsed_json.get('action', 'REPLY').upper()
                    parameters = parsed_json.get('parameters', {})
                    # Extraer texto de respuesta si existe
                    if 'text' in parsed_json:
                        text = parsed_json['text']
                    break
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        print(f"⚠️ Error parseando JSON: {e}")
    
    # Intento 2: Fallback a patrones de texto simple (compatibilidad)
    if action == "REPLY":
        text_upper = text.upper()
        
        if "IR_SEND" in text_upper or "ENVIAR IR" in text_upper:
            action = "IR_SEND"
            # Intentar extraer comando
            for cmd in ["POWER", "VOL_UP", "VOL_DOWN", "MUTE", "HDMI"]:
                if cmd in text_upper:
                    parameters['command'] = cmd
                    break
                    
        elif "YOUTUBE" in text_upper or "VIDEO" in text_upper or "BUSCAR EN YOUTUBE" in text_upper:
            action = "YOUTUBE_SEARCH"
            # Extraer query si está en formato estructurado
            if 'query' in parameters:
                pass  # Ya está en parameters
            else:
                # Usar el texto completo como query
                parameters['query'] = text
                
        elif "HDMI" in text_upper or "CAMBIAR ENTRADA" in text_upper:
            action = "SWITCH_HDMI_PC"
            
        elif "TV_STATE" in text_upper or "ESTADO TV" in text_upper:
            action = "GET_TV_STATE"
    
    return {
        "text": text,
        "action": action,
        "parameters": parameters,
        "done": response.get('done', False),
        "total_duration": response.get('total_duration', 0)
    }
