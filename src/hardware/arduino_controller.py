import serial
import time
import threading
from typing import Callable, Optional

class ArduinoController:
    def __init__(self, port: str = "/dev/ttyUSB0", baud_rate: int = 9600):
        self.port = port
        self.baud_rate = baud_rate
        self.ser = None
        self.is_listening = False
        self.button_pressed_callback: Optional[Callable] = None
        self.button_released_callback: Optional[Callable] = None
        self._monitor_thread = None
        
    def connect(self):
        """Conecta con el Arduino."""
        try:
            self.ser = serial.Serial(self.port, self.baud_rate, timeout=1)
            time.sleep(2)  # Esperar reinicio del Arduino
            print(f"✅ Conectado a Arduino en {self.port}")
            return True
        except serial.SerialException as e:
            print(f"❌ Error conectando al Arduino: {e}")
            return False

    def send_ir_command(self, command: str):
        """Envía un comando IR al Arduino (ej: 'POWER', 'VOL_UP', 'HDMI1')."""
        if self.ser and self.ser.is_open:
            cmd_str = f"IR:{command}\n"
            self.ser.write(cmd_str.encode('utf-8'))
            print(f"📡 Enviando IR: {command}")
        else:
            print("⚠️ Arduino no conectado, no se puede enviar IR.")

    def mute_tv(self):
        """Envía comando MUTE."""
        self.send_ir_command("MUTE")

    def unmute_tv(self):
        """Envía comando UNMUTE (o restaura volumen)."""
        self.send_ir_command("UNMUTE")

    def switch_hdmi(self, input_name: str):
        """Cambia entrada HDMI (ej: 'HDMI1', 'HDMI2')."""
        self.send_ir_command(f"HDMI:{input_name}")

    def start_button_monitor(self, on_press: Callable, on_release: Callable):
        """Inicia un hilo para monitorizar el botón físico."""
        self.button_pressed_callback = on_press
        self.button_released_callback = on_release
        self.is_listening = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()

    def _monitor_loop(self):
        """Bucle interno para leer el estado del botón desde el Arduino."""
        while self.is_listening:
            if self.ser and self.ser.in_waiting > 0:
                try:
                    line = self.ser.readline().decode('utf-8').strip()
                    if line == "BUTTON_PRESSED":
                        print("🔘 Botón PULSADO")
                        if self.button_pressed_callback:
                            self.button_pressed_callback()
                    elif line == "BUTTON_RELEASED":
                        print("🔘 Botón SOLTADO")
                        if self.button_released_callback:
                            self.button_released_callback()
                except Exception as e:
                    print(f"Error leyendo serial: {e}")
            time.sleep(0.1)

    def stop(self):
        """Detiene el monitor y cierra la conexión."""
        self.is_listening = False
        if self._monitor_thread:
            self._monitor_thread.join()
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("🔌 Arduino desconectado.")
