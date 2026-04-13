"""
Módulo de Audio - STT y TTS
Maneja la transcripción de voz (Whisper) y síntesis de voz (Piper)
"""

import os
import tempfile
from typing import Optional, Tuple
from pathlib import Path

# Imports para Whisper (se inicializarán bajo demanda)
_faster_whisper_available = False
try:
    from faster_whisper import WhisperModel
    _faster_whisper_available = True
except ImportError:
    pass

# Imports para Piper (se inicializarán bajo demanda)
_piper_available = False
try:
    # Piper se usa típicamente vía subprocess o librería específica
    import subprocess
    _piper_available = True
except ImportError:
    pass


class AudioProcessor:
    def __init__(self, 
                 whisper_model: str = "small",
                 whisper_device: str = "auto",  # "cpu", "cuda", "auto"
                 piper_voice: str = "es_ES-carlfm-medium",
                 piper_data_dir: str = "./data/piper_voices"):
        """
        Inicializa el procesador de audio.
        
        Args:
            whisper_model: Modelo de Whisper a usar ("tiny", "base", "small", "medium", "large")
            whisper_device: Dispositivo para inferencia ("cpu", "cuda", "auto")
            piper_voice: Nombre de la voz en español para Piper TTS
            piper_data_dir: Directorio donde están los modelos de Piper
        """
        self.whisper_model_name = whisper_model
        self.whisper_device = whisper_device
        self.piper_voice = piper_voice
        self.piper_data_dir = Path(piper_data_dir)
        
        self._whisper_model = None
        self._stt_initialized = False
        
        print(f"🎤 AudioProcessor inicializado:")
        print(f"   - Whisper: {whisper_model} ({whisper_device})")
        print(f"   - Piper Voice: {piper_voice}")
        
    def initialize_stt(self):
        """Carga el modelo de Whisper en memoria."""
        if not _faster_whisper_available:
            raise ImportError("faster-whisper no está instalado. Ejecuta: pip install faster-whisper")
        
        if self._whisper_model is None:
            print(f"⏳ Cargando modelo Whisper '{self.whisper_model_name}'...")
            
            # Determinar dispositivo
            device = self.whisper_device
            if device == "auto":
                # Intentar detectar GPU, si no, usar CPU
                device = "cuda" if self._check_cuda_available() else "cpu"
                print(f"   Detectado dispositivo: {device}")
            
            # Cargar modelo con cuantización para eficiencia
            compute_type = "float16" if device == "cuda" else "int8"
            
            self._whisper_model = WhisperModel(
                self.whisper_model_name,
                device=device,
                compute_type=compute_type
            )
            self._stt_initialized = True
            print(f"✅ Modelo Whisper cargado en {device}")
    
    def _check_cuda_available(self) -> bool:
        """Verifica si CUDA está disponible."""
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False
    
    def transcribe(self, audio_file_path: str, language: str = "es") -> Tuple[str, float]:
        """
        Transcribe un archivo de audio a texto.
        
        Args:
            audio_file_path: Ruta al archivo de audio (WAV, MP3, etc.)
            language: Código de idioma ("es" para español)
            
        Returns:
            Tupla (texto_transcrito, confianza_promedio)
        """
        if not self._stt_initialized:
            self.initialize_stt()
        
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Archivo de audio no encontrado: {audio_file_path}")
        
        print(f"👂 Transcribiendo audio...")
        
        segments, info = self._whisper_model.transcribe(
            audio_file_path,
            language=language,
            vad_filter=True,  # Filtrar silencios automáticamente
            vad_parameters=dict(min_silence_duration_ms=500)
        )
        
        text_parts = []
        confidence_sum = 0
        segment_count = 0
        
        for segment in segments:
            text_parts.append(segment.text)
            # Nota: Faster-Whisper no devuelve confianza directa por segmento en todas las versiones
            # Se puede estimar o usar average_probability si está disponible
            segment_count += 1
        
        full_text = "".join(text_parts).strip()
        avg_confidence = 1.0  # Placeholder, se podría calcular si el modelo lo soporta
        
        print(f"📝 Transcripción completada: '{full_text[:50]}...' ({len(full_text)} chars)")
        
        return full_text, avg_confidence
    
    def synthesize(self, text: str, output_path: str) -> bool:
        """
        Convierte texto a voz usando Piper TTS.
        
        Args:
            text: Texto a sintetizar
            output_path: Ruta donde guardar el archivo WAV resultante
            
        Returns:
            True si éxito, False si fallo
        """
        if not _piper_available:
            raise ImportError("Piper TTS no está disponible correctamente")
        
        # Construir rutas de archivos del modelo
        model_path = self.piper_data_dir / f"{self.piper_voice}.onnx"
        config_path = self.piper_data_dir / f"{self.piper_voice}.onnx.json"
        
        if not model_path.exists():
            print(f"⚠️ Modelo de voz no encontrado en {model_path}")
            print(f"   Descarga voces de Piper desde: https://github.com/rhasspy/piper/blob/master/VOICES.md")
            return False
        
        print(f"🔊 Sintetizando voz: '{text[:50]}...'")
        
        try:
            # Ejecutar Piper como subprocess (método más compatible)
            cmd = [
                "piper",
                "--model", str(model_path),
                "--output_file", output_path,
                "--sentence_silence", "0.2"  # Pausas más naturales
            ]
            
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE
            )
            
            stdout, stderr = process.communicate(input=text.encode('utf-8'))
            
            if process.returncode == 0 and os.path.exists(output_path):
                print(f"✅ Audio generado en: {output_path}")
                return True
            else:
                print(f"❌ Error en Piper: {stderr.decode('utf-8') if stderr else 'Desconocido'}")
                return False
                
        except Exception as e:
            print(f"❌ Excepción en síntesis de voz: {e}")
            return False
    
    def transcribe_bytes(self, audio_bytes: bytes, language: str = "es") -> Tuple[str, float]:
        """
        Transcribe audio directamente desde bytes (útil para streaming).
        
        Args:
            audio_bytes: Bytes del audio en formato WAV
            language: Código de idioma
            
        Returns:
            Tupla (texto_transcrito, confianza)
        """
        # Guardar temporalmente
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_path = tmp_file.name
        
        try:
            text, confidence = self.transcribe(tmp_path, language)
            return text, confidence
        finally:
            # Limpiar archivo temporal
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)


# Función utilitaria para grabación simple (opcional, depende de sounddevice)
def record_audio(duration: int = 5, sample_rate: int = 16000) -> bytes:
    """
    Graba audio del micrófono durante 'duration' segundos.
    Requiere: pip install sounddevice soundfile
    
    Args:
        duration: Duración de la grabación en segundos
        sample_rate: Frecuencia de muestreo (16000 es bueno para Whisper)
        
    Returns:
        Bytes del audio en formato WAV
    """
    try:
        import sounddevice as sd
        import numpy as np
        import wave
        import io
        
        print(f"🎙️ Grabando durante {duration} segundos...")
        
        # Grabar
        recording = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype=np.int16
        )
        sd.wait()
        
        # Convertir a WAV en memoria
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)  # 16 bits = 2 bytes
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(recording.tobytes())
        
        return wav_buffer.getvalue()
        
    except ImportError:
        print("⚠️ sounddevice no instalado. Instala: pip install sounddevice soundfile")
        raise
