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

# Imports locales
from src.hardware.arduino_controller import ArduinoController
from src.audio.audio_processor import AudioProcessor
from src.audio.audio_recorder import ButtonTriggeredRecorder
from src.utils.config_manager import Config
from src.utils.ollama_client import OllamaClient, build_system_prompt, parse_llm_response
from src.utils.memory_manager import MemoryManager
from src.vision.tv_state_detector import create_tv_state_detector


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
        # Cargar configuración real desde YAML
        self.config = Config.load_from_yaml(config_path)
        self.config.print_summary()
        
        # Validar configuración
        is_valid, errors = self.config.validate()
        if not is_valid:
            print("⚠️ Errores en configuración:")
            for error in errors:
                print(f"   - {error}")
        
        # Inicializar componentes
        self.arduino = ArduinoController(
            port=self.config.arduino.port,
            baud_rate=self.config.arduino.baud_rate
        )
        
        self.audio = AudioProcessor(
            whisper_model=self.config.audio.whisper_model,
            whisper_device=self.config.audio.whisper_device,
            piper_voice=self.config.audio.piper_voice,
            piper_data_dir=self.config.audio.piper_data_dir
        )
        
        # Inicializar cliente Ollama con soporte Vulkan para RDNA2
        self.llm = OllamaClient(
            host=self.config.llm.ollama_host,
            model=self.config.llm.model,
            timeout=120,
            use_vulkan=self.config.llm.use_vulkan
        )
        
        # Inicializar grabadora con trigger de botón
        self.recorder = ButtonTriggeredRecorder(
            arduino_controller=self.arduino,
            sample_rate=self.config.audio.sample_rate,
            silence_threshold=self.config.audio.silence_threshold
        )
        
        # Inicializar sistema de memoria
        self.memory_manager = MemoryManager(
            db_path=self.config.memory.db_path
        ) if self.config.memory.enabled else None
        
        # Inicializar detector de estado de TV
        self.tv_detector = create_tv_state_detector(
            use_camera=self.config.vision.enabled,
            camera_index=self.config.vision.camera_index,
            resolution=(self.config.vision.resolution_width, self.config.vision.resolution_height)
        )
        
        # Estado del sistema
        self.is_active = False
        self.current_state = "IDLE"  # IDLE, LISTENING, PROCESSING, SPEAKING
        self.memory: List[Dict[str, str]] = []  # Historial de conversación en RAM (para contexto LLM)
        self.last_recording_file: Optional[str] = None
        
        # System prompt para personalidad
        self.system_prompt = build_system_prompt("abuelo")
        
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
    
    def start(self):
        """Inicia el bucle principal del agente."""
        print("🚀 Iniciando agente...")
        
        # Conectar Arduino
        if not self.arduino.connect():
            print("⚠️ Arduino no conectado, continuando en modo simulación")
        
        # Configurar grabadora con trigger de botón
        self.recorder.setup_button_trigger()
        
        print("✅ Agente en ejecución. Esperando pulsación del botón...")
        print("   (Presiona el botón físico para comenzar)")
        
        # Bucle principal (se mantiene vivo por el thread del Arduino)
        try:
            while True:
                # Verificar si hay una grabación lista para procesar
                if self.last_recording_file and self.current_state == "IDLE":
                    audio_file = self.last_recording_file
                    self.last_recording_file = None
                    self._process_user_request(audio_file)
                
                time.sleep(0.5)
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
    
    def _on_button_released(self):
        """Callback cuando se suelta el botón."""
        print("\n🔘 === BOTÓN SOLTADO ===")
        self.current_state = "PROCESSING"
        
        # La grabadora ya guardó el archivo automáticamente
        # El bucle principal lo detectará y procesará
        
        # Desmuteear TV (o mantener mute mientras habla la IA)
        # Depende de la estrategia elegida
        print("🔊 Restaurando volumen TV...")
        self.arduino.unmute_tv()
        
        self.current_state = "IDLE"
    
    def _process_user_request(self, audio_file: str):
        """
        Procesa la petición del usuario:
        1. Transcribe audio
        2. Consulta a Gemma 4
        3. Ejecuta acción
        4. Guarda en memoria persistente
        """
        print("\n🧠 === PROCESANDO PETICIÓN ===")
        self.current_state = "PROCESSING"
        
        # 1. Transcribir audio
        try:
            print(f"📝 Transcribiendo: {audio_file}")
            transcription, confidence = self.audio.transcribe(audio_file)
            print(f"🗣️ Usuario dice: '{transcription}' (confianza: {confidence:.2f})")
            
            # Limpiar archivo temporal
            try:
                os.unlink(audio_file)
            except:
                pass
                
        except Exception as e:
            print(f"❌ Error transcribiendo: {e}")
            self.current_state = "IDLE"
            return
        
        # 2. Consultar a Gemma 4 (vía Ollama)
        try:
            print("🤔 Consultando a Gemma 4...")
            
            # Mantener solo últimos N mensajes en contexto
            max_context = self.config.memory.max_conversation_history
            context = self.memory[-max_context:] if len(self.memory) > max_context else self.memory
            
            response = self.llm.generate(
                prompt=transcription,
                system_prompt=self.system_prompt,
                context=context[:-1] if len(context) > 1 else None,  # Excluir mensaje actual
                temperature=self.config.llm.temperature,
                max_tokens=self.config.llm.max_tokens
            )
            
            # Parsear respuesta
            parsed = parse_llm_response(response)
            llm_text = parsed.get('text', '')
            llm_action = parsed.get('action', 'REPLY')
            
            print(f"💬 Gemma responde: '{llm_text[:100]}...'")
            print(f"🎯 Acción detectada: {llm_action}")
            
            # Agregar respuesta al historial en RAM
            self.memory.append({"role": "user", "content": transcription})
            self.memory.append({"role": "assistant", "content": llm_text})
            
            # 3. Ejecutar acción
            action_result = self._execute_response(llm_action, llm_text, parsed.get('parameters', {}))
            
            # 4. Guardar en memoria persistente
            if self.memory_manager:
                self.memory_manager.save_conversation(
                    user_input=transcription,
                    assistant_response=llm_text,
                    action_taken=llm_action,
                    context={"action_result": str(action_result)}
                )
                self.memory_manager.increment_interaction_count()
            
        except Exception as e:
            print(f"❌ Error consultando LLM: {e}")
            # Fallback: responder con TTS directamente
            fallback_text = "Lo siento, tuve un problema. ¿Podrías repetir?"
            self._tool_reply(fallback_text)
        
        self.current_state = "IDLE"
    
    def _execute_response(self, action: str, text: str, parameters: Dict[str, Any]):
        """Ejecuta la acción determinada por el LLM"""
        
        if action == "IR_SEND":
            # Extraer comando IR del texto o parámetros
            command = parameters.get('command', 'POWER')  # Default a POWER
            self._tool_ir_send(command)
            # Luego responder
            self._tool_reply(text)
            
        elif action == "SWITCH_HDMI_PC":
            self._tool_switch_hdmi_pc()
            self._tool_reply(text)
            
        elif action == "YOUTUBE_SEARCH":
            query = parameters.get('query', text)
            self._tool_youtube_search(query)
            
        elif action == "GET_TV_STATE":
            tv_state = self._tool_get_tv_state()
            self._tool_reply(f"La TV está mostrando: {tv_state.get('state', 'desconocido')}")
            
        else:
            # REPLY por defecto
            self._tool_reply(text)
    
    # === HERRAMIENTAS ===
    
    def _tool_ir_send(self, command: str) -> bool:
        """Envía un comando IR a la TV."""
        print(f"📡 Herramienta IR_SEND: {command}")
        
        # Validar comando
        valid_commands = ["POWER", "POWER_ON", "POWER_OFF", "VOL_UP", "VOL_DOWN", 
                         "MUTE", "CH_UP", "CH_DOWN", "HDMI1", "HDMI2", "NETFLIX", 
                         "YOUTUBE", "UP", "DOWN", "LEFT", "RIGHT", "OK", "BACK"]
        
        if command.upper() not in valid_commands:
            print(f"⚠️ Comando IR no válido: {command}")
            return False
        
        # Enviar comando
        success = self.arduino.send_ir_command(command.upper())
        
        # Actualizar detector de estado si existe
        if hasattr(self, 'tv_detector') and self.tv_detector:
            if isinstance(self.tv_detector.__class__.__name__, 'SimpleTVStateDetector'):
                self.tv_detector.update_from_ir_command(command.upper())
        
        # Guardar estadística
        if self.memory_manager and success:
            self.memory_manager.increment_ir_commands()
        
        return success
    
    def _tool_switch_hdmi_pc(self) -> bool:
        """Cambia la entrada HDMI al PC."""
        print("📺 Herramienta SWITCH_HDMI_PC")
        
        # Obtener puerto HDMI del PC desde configuración
        hdmi_port = self.config.tv.pc_hdmi_port
        
        # Mapear puerto a comando IR
        port_to_command = {
            "HDMI1": "HDMI1",
            "HDMI2": "HDMI2",
            "HDMI3": "HDMI3",
            "HDMI4": "HDMI4"
        }
        
        command = port_to_command.get(hdmi_port.upper(), "HDMI1")
        
        # Enviar comando
        success = self.arduino.switch_hdmi(hdmi_port)
        
        # Esperar cambio de entrada
        time.sleep(2)
        
        return success
    
    def _tool_youtube_search(self, query: str) -> bool:
        """Busca y reproduce un video en YouTube (Brave + Selenium + PyAutoGUI)."""
        print(f"▶️ Herramienta YOUTUBE_SEARCH: {query}")
        
        try:
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.common.keys import Keys
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from urllib.parse import quote_plus
            import pyautogui
            import time
            
            # Configurar opciones de Chrome/Brave
            options = webdriver.ChromeOptions()
            
            # Intentar Brave primero, fallback a Chrome
            brave_paths = [
                "/usr/bin/brave",
                "/usr/bin/brave-browser",
                "/usr/bin/google-chrome",
                "/usr/bin/chromium"
            ]
            
            brave_binary = None
            for path in brave_paths:
                if os.path.exists(path):
                    brave_binary = path
                    break
            
            if brave_binary:
                options.binary_location = brave_binary
                print(f"   🌐 Usando navegador: {brave_binary}")
            else:
                print("   ⚠️ No se encontró Brave/Chrome, usando Chrome por defecto")
            
            # Opciones para modo kiosk (pantalla completa)
            options.add_argument("--start-maximized")
            options.add_argument("--no-first-run")
            options.add_argument("--disable-infobars")
            options.add_argument("--disable-notifications")
            
            # Iniciar driver
            print("   🚗 Iniciando WebDriver...")
            driver = webdriver.Chrome(options=options)
            driver.set_window_size(1920, 1080)
            
            # Construir URL de búsqueda
            search_url = f"https://www.youtube.com/results?search_query={quote_plus(query)}"
            print(f"   🔍 Buscando: {search_url}")
            
            # Navegar a YouTube
            driver.get(search_url)
            
            # Esperar a que carguen los resultados
            print("   ⏳ Esperando resultados...")
            wait = WebDriverWait(driver, 10)
            try:
                # Esperar primer resultado de video
                first_video = wait.until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, "ytd-video-renderer:first-of-type")
                    )
                )
                
                # Hacer click en el primer video
                print("   ▶️ Click en primer video...")
                first_video.click()
                
                # Esperar que cargue el video
                time.sleep(3)
                
                # Pantalla completa con 'f'
                print("   📺 Pantalla completa...")
                pyautogui.press('f')
                
                # Guardar estadística
                if self.memory_manager:
                    self.memory_manager.increment_youtube_searches()
                
                print("   ✅ Video reproduciéndose")
                return True
                
            except Exception as e:
                print(f"   ⚠️ Error encontrando video: {e}")
                # Fallback: intentar con teclado
                print("   🎹 Usando control por teclado...")
                time.sleep(2)
                pyautogui.press('tab', presses=3)  # Navegar al primer video
                time.sleep(0.5)
                pyautogui.press('enter')
                time.sleep(2)
                pyautogui.press('f')  # Pantalla completa
                
                if self.memory_manager:
                    self.memory_manager.increment_youtube_searches()
                
                return True
                
        except ImportError as e:
            print(f"   ❌ Error: selenium o pyautogui no instalados ({e})")
            response_text = "Vale, buscando en YouTube... (necesito instalar dependencias)"
            self._tool_reply(response_text)
            return False
            
        except Exception as e:
            print(f"   ❌ Error en YouTube search: {e}")
            response_text = "Tuve un problema buscando en YouTube. ¿Intentamos de nuevo?"
            self._tool_reply(response_text)
            return False
    
    def _tool_reply(self, text: str) -> bool:
        """Responde al usuario hablando (TTS)."""
        print(f"💬 Herramienta REPLY: '{text}'")
        
        # 1. Sintetizar voz
        import tempfile
        output_path = tempfile.mktemp(suffix=".wav")
        
        try:
            success = self.audio.synthesize(text, output_path)
            
            if success and os.path.exists(output_path):
                # 2. Reproducir audio por altavoces del PC (NO bloqueante)
                print("🔊 Reproduciendo respuesta...")
                
                # Usar reproductor no-bloqueante desde nuevo módulo
                from src.audio.audio_player import play_audio_async, stop_audio_playback
                
                # Callback cuando termine de hablar
                def on_speech_finished():
                    print("✅ Speech finished")
                    # Aquí se podría restaurar volumen de TV si estaba muteada
                
                play_success = play_audio_async(output_path, on_finish=on_speech_finished)
                
                # Esperar a que termine (pero sin bloquear completamente)
                from src.audio.audio_player import get_audio_player
                player = get_audio_player()
                player.wait_until_finished(timeout=30.0)  # Timeout de 30s
                
                return play_success
            else:
                print("⚠️ No se pudo generar audio, mostrando solo texto")
                return False
                
        except Exception as e:
            print(f"❌ Error en TTS: {e}")
            return False
        finally:
            # Limpiar archivo temporal
            try:
                if os.path.exists(output_path):
                    os.unlink(output_path)
            except:
                pass
    
    def _play_audio_file(self, file_path: str) -> bool:
        """Reproduce un archivo de audio WAV"""
        try:
            import sounddevice as sd
            import wave
            import numpy as np
            
            with wave.open(file_path, 'rb') as wav_file:
                # Leer datos
                frames = wav_file.readframes(wav_file.getnframes())
                sample_rate = wav_file.getframerate()
                
                # Convertir a numpy array
                audio_data = np.frombuffer(frames, dtype=np.int16)
                
                # Reproducir
                sd.play(audio_data, sample_rate)
                sd.wait()  # Esperar hasta que termine
                
                return True
                
        except ImportError:
            print("⚠️ sounddevice no disponible, no se puede reproducir audio")
            print(f"   Archivo generado: {file_path}")
            return False
        except Exception as e:
            print(f"❌ Error reproduciendo audio: {e}")
            print(f"   Archivo generado: {file_path}")
            return False
    
    def _tool_get_tv_state(self) -> Dict[str, Any]:
        """Obtiene el estado actual de la TV (usando visión)."""
        print("👁️ Herramienta GET_TV_STATE")
        
        # Obtener estado del detector
        tv_state = self.tv_detector.detect_tv_state()
        
        print(f"   - TV encendida: {tv_state.get('is_on', False)}")
        print(f"   - App detectada: {tv_state.get('app_detected', 'unknown')}")
        print(f"   - Confianza: {tv_state.get('confidence', 0):.2f}")
        
        return tv_state


# Punto de entrada principal
if __name__ == "__main__":
    agent = AbueloAgent()
    agent.start()
