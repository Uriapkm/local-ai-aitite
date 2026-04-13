"""
Módulo de grabación de audio en tiempo real
Integrado con detección de botón y VAD (Voice Activity Detection)
"""

import os
import tempfile
import threading
import time
from typing import Optional, Callable
from pathlib import Path

# Imports para grabación
try:
    import sounddevice as sd
    import numpy as np
    import wave
    import io
    _sounddevice_available = True
except ImportError:
    _sounddevice_available = False
    print("⚠️ sounddevice no disponible. Instala: pip install sounddevice soundfile")


class AudioRecorder:
    """
    Grabadora de audio en tiempo real con control por botón
    """
    
    def __init__(self, 
                 sample_rate: int = 16000,
                 channels: int = 1,
                 dtype: str = "int16",
                 silence_threshold: float = 0.5,
                 min_silence_duration: float = 0.5):
        """
        Inicializa la grabadora
        
        Args:
            sample_rate: Frecuencia de muestreo (16000 recomendado para Whisper)
            channels: Número de canales (1 = mono)
            dtype: Tipo de dato (int16 = 16 bits)
            silence_threshold: Umbral para detectar silencio (0.0-1.0)
            min_silence_duration: Duración mínima de silencio para considerar fin de habla
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.dtype = np.int16 if dtype == "int16" else np.float32
        self.silence_threshold = silence_threshold
        self.min_silence_duration = min_silence_duration
        
        self._is_recording = False
        self._recording_thread: Optional[threading.Thread] = None
        self._audio_buffer = bytearray()
        self._start_time: Optional[float] = None
        self._silence_start: Optional[float] = None
        
        if not _sounddevice_available:
            raise ImportError("sounddevice no está instalado")
        
        print(f"🎙️ AudioRecorder inicializado:")
        print(f"   - Sample rate: {sample_rate} Hz")
        print(f"   - Canales: {channels}")
        print(f"   - Umbral silencio: {silence_threshold}")
    
    def start_recording(self, on_stop_callback: Optional[Callable[[str], None]] = None):
        """
        Inicia la grabación de audio
        
        Args:
            on_stop_callback: Función a llamar cuando se detenga la grabación, 
                              recibe la ruta del archivo WAV
        """
        if self._is_recording:
            print("⚠️ Ya hay una grabación en curso")
            return
        
        self._is_recording = True
        self._audio_buffer = bytearray()
        self._start_time = time.time()
        self._silence_start = None
        self._on_stop_callback = on_stop_callback
        
        # Iniciar hilo de grabación
        self._recording_thread = threading.Thread(target=self._record_loop, daemon=True)
        self._recording_thread.start()
        
        print("🔴 Grabando...")
    
    def stop_recording(self) -> Optional[str]:
        """
        Detiene la grabación y guarda el archivo WAV
        
        Returns:
            Ruta al archivo WAV guardado, o None si falló
        """
        if not self._is_recording:
            print("⚠️ No hay grabación activa")
            return None
        
        self._is_recording = False
        
        # Esperar que termine el hilo
        if self._recording_thread:
            self._recording_thread.join(timeout=2.0)
        
        # Guardar archivo
        return self._save_to_file()
    
    def _record_loop(self):
        """Bucle interno de grabación"""
        try:
            def audio_callback(indata, frames, time_info, status):
                """Callback llamado por sounddevice cuando hay nuevos datos de audio"""
                if not self._is_recording:
                    return
                
                # Convertir a bytes
                audio_bytes = indata.tobytes()
                self._audio_buffer.extend(audio_bytes)
                
                # Detectar silencio para auto-detener
                rms = self._calculate_rms(indata)
                if rms < self.silence_threshold:
                    if self._silence_start is None:
                        self._silence_start = time.time()
                    elif (time.time() - self._silence_start) >= self.min_silence_duration:
                        # Silencio prolongado detected
                        print("🤫 Silencio detectado, deteniendo grabación...")
                        self._is_recording = False
                        
                        # Llamar callback si existe
                        if self._on_stop_callback:
                            file_path = self._save_to_file()
                            if file_path:
                                self._on_stop_callback(file_path)
                else:
                    self._silence_start = None
            
            # Iniciar stream de audio
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=self.dtype,
                callback=audio_callback
            ):
                while self._is_recording:
                    time.sleep(0.1)
                    
        except Exception as e:
            print(f"❌ Error en grabación: {e}")
            self._is_recording = False
    
    def _calculate_rms(self, audio_data: np.ndarray) -> float:
        """Calcula el RMS (Root Mean Square) del audio para detectar volumen"""
        return np.sqrt(np.mean(audio_data ** 2))
    
    def _save_to_file(self) -> Optional[str]:
        """Guarda el buffer de audio como archivo WAV"""
        if len(self._audio_buffer) == 0:
            print("⚠️ Buffer de audio vacío")
            return None
        
        # Crear archivo temporal
        temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        temp_path = temp_file.name
        temp_file.close()
        
        try:
            with wave.open(temp_path, 'wb') as wav_file:
                wav_file.setnchannels(self.channels)
                wav_file.setsampwidth(2)  # 16 bits = 2 bytes
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(bytes(self._audio_buffer))
            
            duration = time.time() - self._start_time if self._start_time else 0
            print(f"✅ Audio guardado: {temp_path} ({duration:.2f}s)")
            return temp_path
            
        except Exception as e:
            print(f"❌ Error guardando audio: {e}")
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            return None
    
    def record_fixed_duration(self, duration: float) -> Optional[str]:
        """
        Graba durante una duración fija
        
        Args:
            duration: Duración en segundos
            
        Returns:
            Ruta al archivo WAV guardado, o None si falló
        """
        print(f"🎙️ Grabando durante {duration} segundos...")
        
        self.start_recording()
        time.sleep(duration)
        return self.stop_recording()


class ButtonTriggeredRecorder(AudioRecorder):
    """
    Grabadora activada por botón físico (Arduino)
    Extiende AudioRecorder con integración de hardware
    """
    
    def __init__(self, 
                 arduino_controller,
                 sample_rate: int = 16000,
                 channels: int = 1,
                 silence_threshold: float = 0.5):
        """
        Inicializa grabadora con trigger de botón
        
        Args:
            arduino_controller: Instancia de ArduinoController
            sample_rate: Frecuencia de muestreo
            channels: Número de canales
            silence_threshold: Umbral de silencio
        """
        super().__init__(
            sample_rate=sample_rate,
            channels=channels,
            silence_threshold=silence_threshold
        )
        
        self.arduino = arduino_controller
        self._last_recording_file: Optional[str] = None
        
        print("🔘 ButtonTriggeredRecorder listo")
    
    def setup_button_trigger(self):
        """Configura el botón del Arduino para triggerar grabación"""
        self.arduino.start_button_monitor(
            on_press=self._on_button_pressed,
            on_release=self._on_button_released
        )
        print("✅ Botón configurado como trigger de grabación")
    
    def _on_button_pressed(self):
        """Callback cuando se pulsa el botón"""
        print("\n🔘 === BOTÓN PULSADO ===")
        self.start_recording(on_stop_callback=self._on_recording_stopped)
    
    def _on_button_released(self):
        """Callback cuando se suelta el botón"""
        print("\n🔘 === BOTÓN SOLTADO ===")
        file_path = self.stop_recording()
        if file_path:
            self._last_recording_file = file_path
            print(f"📁 Archivo listo para procesar: {file_path}")
    
    def _on_recording_stopped(self, file_path: str):
        """Callback cuando se detiene la grabación (auto por silencio)"""
        self._last_recording_file = file_path
        print(f"📁 Grabación automática guardada: {file_path}")
    
    def get_last_recording(self) -> Optional[str]:
        """Obtiene la ruta de la última grabación"""
        return self._last_recording_file
    
    def clear_last_recording(self):
        """Limpia la referencia a la última grabación"""
        self._last_recording_file = None
