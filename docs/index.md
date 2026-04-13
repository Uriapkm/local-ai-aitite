# Documentación de Abuelo IA

## 📚 Índice

1. [Arquitectura del Sistema](docs/architecture.md)
2. [Configuración de Hardware](docs/hardware_setup.md)
3. [Guía de Instalación](docs/installation.md)
4. [Configuración de Códigos IR](docs/ir_setup.md)
5. [Personalización del Sistema](docs/customization.md)
6. [Solución de Problemas](docs/troubleshooting.md)
7. [API y Desarrollo](docs/api.md)

## 🚀 Inicio Rápido

```bash
# 1. Clonar repositorio
git clone https://github.com/tu-usuario/abuelo-ia.git
cd abuelo-ia

# 2. Ejecutar instalación automática
chmod +x scripts/install.sh
./scripts/install.sh

# 3. Configurar códigos IR (ver docs/ir_setup.md)
# 4. Subir sketch a Arduino (ver docs/hardware_setup.md)
# 5. Iniciar sistema
sudo systemctl start abuelo-ia
```

## 📖 Documentos Disponibles

### Para Usuarios Finales
- **Guía de Uso**: Cómo interactuar con el sistema
- **Comandos de Voz**: Lista de frases que entiende la IA
- **Solución de Problemas**: Errores comunes y soluciones

### Para Desarrolladores
- **Arquitectura**: Diagramas y flujo de datos
- **API Reference**: Documentación de clases y funciones
- **Contributing**: Cómo contribuir al proyecto

### Para Mantenedores
- **Deploy**: Guía de despliegue en producción
- **Monitoring**: Cómo monitorizar el sistema
- **Backup**: Estrategia de copias de seguridad

## 🔗 Enlaces Externos

- [Gemma 4 Documentation](https://ai.google.dev/gemma)
- [Ollama Python Client](https://github.com/ollama/ollama-python)
- [Faster Whisper](https://github.com/guillaumekln/faster-whisper)
- [Piper TTS](https://github.com/rhasspy/piper)
- [IRremote Library](https://github.com/Arduino-IRremote/Arduino-IRremote)

## 📞 Soporte

Para problemas o preguntas:
1. Revisa [docs/troubleshooting.md](docs/troubleshooting.md)
2. Abre un issue en GitHub
3. Consulta los logs: `journalctl -u abuelo-ia -f`

---

*Proyecto desarrollado con ❤️ para mejorar la calidad de vida de personas mayores*
