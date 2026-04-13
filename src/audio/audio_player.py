"""
Reproductor de audio no-bloqueante para Abuelo IA
Permite reproducción de audio en segundo plano con capacidad de interrupción
"""

import os
import threading
import time
from typing import Optional, Callable
import numpy as np

try:
    import sounddevice as sd
    import wave
    _sounddevice_available = True
except ImportError:
    _sounddevice_available = False
    print("⚠️ sounddevice no disponible. Instala: pip install sounddevice")


class NonBlockingAudioPlayer:
    """
    Reproductor de audio no-bloqueante con soporte para interrupción
    
    Características:
    - Reproducción en thread separado
    - No bloquea el hilo principal
    - Se puede interrumpir en cualquier momento
    - Callback al finalizar reproducción
    """
    
    def __init__(self):
        if not _sounddevice_available:
            raise ImportError("sounddevice no está instalado")
        
        self._is_playing = False
        self._stop_flag = False
        self._current_stream = None
        self._play_thread: Optional[threading.Thread] = None
        self._on_finish_callback: Optional[Callable] = None
        
        print("🔊 NonBlockingAudioPlayer inicializado")
    
    def play(
        self, 
        file_path: str, 
        on_finish: Optional[Callable] = None,
        allow_interrupt: bool = True
    ) -> bool:
        """
        Reproduce un archivo de audio en segundo plano
        
        Args:
            file_path: Ruta al archivo WAV
            on_finish: Callback opcional al terminar reproducción
            allow_interrupt: Si True, se puede interrumpir con stop()
            
        Returns:
            True si inició la reproducción, False si falló
        """
        if not os.path.exists(file_path):
            print(f"❌ Archivo de audio no encontrado: {file_path}")
            return False
        
        # Detener reproducción anterior si existe
        if self._is_playing and allow_interrupt:
            self.stop()
        
        # Esperar un poco para asegurar que se liberó el stream anterior
        time.sleep(0.1)
        
        self._stop_flag = False
        self._on_finish_callback = on_finish
        
        # Iniciar thread de reproducción
        self._play_thread = threading.Thread(
            target=self._play_thread_target,
            args=(file_path,),
            daemon=True
        )
        self._play_thread.start()
        
        return True
    
    def _play_thread_target(self, file_path: str):
        """Hilo interno de reproducción"""
        try:
            with wave.open(file_path, 'rb') as wav_file:
                # Leer configuración del audio
                n_channels = wav_file.getnchannels()
                sample_width = wav_file.getsampwidth()
                frame_rate = wav_file.getframerate()
                n_frames = wav_file.getnframes()
                
                # Determinar dtype según sample_width
                if sample_width == 2:  # 16 bits
                    dtype = np.int16
                elif sample_width == 4:  # 32 bits
                    dtype = np.int32
                else:
                    dtype = np.float32
                
                # Leer todos los frames
                audio_data = wav_file.readframes(n_frames)
                audio_array = np.frombuffer(audio_data, dtype=dtype)
                
                # Configurar stream de sonido
                self._is_playing = True
                
                def audio_callback(outdata, frames, time, status):
                    """Callback para streaming de audio"""
                    if self._stop_flag:
                        raise sd.CallbackStop()
                    
                    # Obtener datos pendientes
                    available = len(audio_array) - getattr(self, '_frame_pos', 0)
                    
                    if available <= 0:
                        raise sd.CallbackStop()
                    
                    # Calcular cuántos frames leer
                    to_read = min(frames, available)
                    
                    # Copiar datos al buffer de salida
                    start_pos = getattr(self, '_frame_pos', 0)
                    end_pos = start_pos + to_read
                    
                    if n_channels == 1:
                        outdata[:to_read, 0] = audio_array[start_pos:end_pos]
                    else:
                        # Para stereo, replicar en ambos canales
                        for ch in range(n_channels):
                            outdata[:to_read, ch] = audio_array[start_pos:end_pos]
                    
                    self._frame_pos = end_pos
                
                # Inicializar posición de frame
                self._frame_pos = 0
                
                # Crear y ejecutar stream
                with sd.Stream(
                    samplerate=frame_rate,
                    channels=n_channels,
                    dtype=dtype,
                    callback=audio_callback
                ) as stream:
                    while self._is_playing and not self._stop_flag:
                        time.sleep(0.1)
                        
        except sd.CallbackStop:
            # Interrupción normal
            pass
        except Exception as e:
            print(f"❌ Error reproduciendo audio: {e}")
        finally:
            self._is_playing = False
            
            # Llamar callback si existe
            if self._on_finish_callback:
                try:
                    self._on_finish_callback()
                except Exception as e:
                    print(f"⚠️ Error en callback de finish: {e}")
    
    def stop(self):
        """Detiene la reproducción actual inmediatamente"""
        if not self._is_playing:
            return
        
        print("⏹️ Deteniendo reproducción de audio...")
        self._stop_flag = True
        self._is_playing = False
        
        # Esperar que el thread termine (con timeout)
        if self._play_thread and self._play_thread.is_alive():
            self._play_thread.join(timeout=1.0)
    
    def is_playing(self) -> bool:
        """Devuelve True si está reproduciendo actualmente"""
        return self._is_playing
    
    def wait_until_finished(self, timeout: Optional[float] = None) -> bool:
        """
        Espera hasta que termine la reproducción o se alcance el timeout
        
        Args:
            timeout: Tiempo máximo de espera en segundos (None = infinito)
            
        Returns:
            True si terminó naturalmente, False si timeout o interrupción
        """
        if not self._play_thread:
            return True
        
        self._play_thread.join(timeout=timeout)
        
        # Si el thread sigue vivo, hubo timeout
        if self._play_thread.is_alive():
            return False
        
        # Si no está playing, terminó
        return not self._is_playing


# Singleton global para usar en todo el proyecto
_audio_player_instance: Optional[NonBlockingAudioPlayer] = None


def get_audio_player() -> NonBlockingAudioPlayer:
    """Obtiene la instancia singleton del reproductor de audio"""
    global _audio_player_instance
    if _audio_player_instance is None:
        _audio_player_instance = NonBlockingAudioPlayer()
    return _audio_player_instance


def play_audio_async(
    file_path: str, 
    on_finish: Optional[Callable] = None
) -> bool:
    """
    Función utilitaria para reproducir audio asíncronamente
    
    Args:
        file_path: Ruta al archivo WAV
        on_finish: Callback opcional al terminar
        
    Returns:
        True si inició la reproducción
    """
    player = get_audio_player()
    return player.play(file_path, on_finish=on_finish)


def stop_audio_playback():
    """Detiene cualquier reproducción de audio en curso"""
    player = get_audio_player()
    player.stop()


def is_audio_playing() -> bool:
    """Devuelve True si hay audio reproduciéndose"""
    player = get_audio_player()
    return player.is_playing()


# Punto de entrada para testing
if __name__ == "__main__":
    print("🧪 Testing NonBlockingAudioPlayer...\n")
    
    if not _sounddevice_available:
        print("❌ sounddevice no disponible, skipping test")
        exit(1)
    
    # Crear reproductor
    player = NonBlockingAudioPlayer()
    
    # Test 1: Verificar que no hay reproducción inicial
    print("Test 1: Estado inicial")
    assert not player.is_playing(), "No debería estar reproduciendo inicialmente"
    print("   ✅ OK\n")
    
    # Test 2: Intentar reproducir archivo inexistente
    print("Test 2: Archivo inexistente")
    result = player.play("/tmp/nonexistent.wav")
    assert not result, "Debería fallar con archivo inexistente"
    print("   ✅ OK\n")
    
    # Test 3: Reproducir archivo real (si existe)
    print("Test 3: Reproducción real")
    test_file = "/tmp/test_audio.wav"
    
    # Crear archivo de test (silencio de 1 segundo)
    import wave
    with wave.open(test_file, 'wb') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(16000)
        wav.writeframes(b'\x00\x00' * 16000)
    
    finished = threading.Event()
    
    def on_finish():
        print("   🎵 Reproducción terminada")
        finished.set()
    
    print("   🔊 Iniciando reproducción...")
    result = player.play(test_file, on_finish=on_finish)
    
    if result:
        print("   ✅ Reproducción iniciada")
        
        # Esperar a que termine
        finished.wait(timeout=5.0)
        
        if finished.is_set():
            print("   ✅ Test completado correctamente")
        else:
            print("   ⚠️ Timeout esperando finalización")
    else:
        print("   ❌ Falló iniciar reproducción")
    
    # Limpiar
    if os.path.exists(test_file):
        os.unlink(test_file)
    
    print("\n✅ Todos los tests completados")
