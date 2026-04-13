#!/bin/bash
# ============================================
# Script de Configuración - Abuelo IA Assistant
# Ayuda a configurar el sistema para la primera ejecución
# ============================================

set -e

echo "🔧 CONFIGURADOR DE ABUELO IA ASSISTANT"
echo "======================================="
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_info() { echo -e "${GREEN}✓${NC} $1"; }
print_warn() { echo -e "${YELLOW}⚠${NC} $1"; }
print_error() { echo -e "${RED}✗${NC} $1"; }

# ============================================
# 1. Crear archivo .env si no existe
# ============================================
if [ ! -f ".env" ]; then
    print_info "Creando archivo .env desde plantilla..."
    cp .env.example .env
    print_info "Archivo .env creado en: $(pwd)/.env"
else
    print_info "Archivo .env ya existe"
fi

echo ""

# ============================================
# 2. Detectar puerto Arduino
# ============================================
print_info "Detectando puertos USB disponibles..."

ARDUINO_PORTS=()
while IFS= read -r line; do
    ARDUINO_PORTS+=("$line")
done < <(ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null || true)

if [ ${#ARDUINO_PORTS[@]} -eq 0 ]; then
    print_warn "No se detectaron puertos Arduino (/dev/ttyUSB* o /dev/ttyACM*)"
    print_warn "Conecta el Arduino y ejecuta este script de nuevo"
    CURRENT_ARDUINO="/dev/ttyUSB0"
else
    print_info "Puertos encontrados:"
    for i in "${!ARDUINO_PORTS[@]}"; do
        echo "   [$i] ${ARDUINO_PORTS[$i]}"
    done
    
    if [ ${#ARDUINO_PORTS[@]} -eq 1 ]; then
        CURRENT_ARDUINO="${ARDUINO_PORTS[0]}"
        print_info "Usando: $CURRENT_ARDUINO"
    else
        echo ""
        echo -n "Selecciona el puerto (0-$((${#ARDUINO_PORTS[@]}-1))): "
        read -r selection
        if [[ "$selection" =~ ^[0-9]+$ ]] && [ "$selection" -lt "${#ARDUINO_PORTS[@]}" ]; then
            CURRENT_ARDUINO="${ARDUINO_PORTS[$selection]}"
        else
            CURRENT_ARDUINO="${ARDUINO_PORTS[0]}"
            print_warn "Selección inválida, usando: $CURRENT_ARDUINO"
        fi
    fi
fi

# Actualizar .env con el puerto Arduino
if grep -q "^ARDUINO_PORT=" .env; then
    sed -i "s|^ARDUINO_PORT=.*|ARDUINO_PORT=$CURRENT_ARDUINO|" .env
else
    echo "ARDUINO_PORT=$CURRENT_ARDUINO" >> .env
fi
print_info "ARDUINO_PORT configurado como: $CURRENT_ARDUINO"

echo ""

# ============================================
# 3. Detectar navegador disponible
# ============================================
print_info "Detectando navegadores disponibles..."

BROWSER=""
if command -v brave &> /dev/null || [ -f "/usr/bin/brave" ] || [ -f "/usr/bin/brave-browser" ]; then
    BROWSER="brave"
    print_info "Brave encontrado"
elif command -v google-chrome &> /dev/null || [ -f "/usr/bin/google-chrome" ]; then
    BROWSER="chrome"
    print_info "Chrome encontrado"
elif command -v chromium &> /dev/null || [ -f "/usr/bin/chromium" ]; then
    BROWSER="chromium"
    print_info "Chromium encontrado"
elif command -v firefox &> /dev/null || [ -f "/usr/bin/firefox" ]; then
    BROWSER="firefox"
    print_info "Firefox encontrado"
else
    print_warn "No se encontró ningún navegador soportado"
    BROWSER="brave"
    print_warn "Usando 'brave' por defecto (puedes cambiarlo en .env)"
fi

# Actualizar .env con el navegador
if grep -q "^BROWSER=" .env; then
    sed -i "s|^BROWSER=.*|BROWSER=$BROWSER|" .env
else
    echo "BROWSER=$BROWSER" >> .env
fi
print_info "BROWSER configurado como: $BROWSER"

echo ""

# ============================================
# 4. Verificar Ollama
# ============================================
print_info "Verificando Ollama..."

if command -v ollama &> /dev/null; then
    print_info "Ollama está instalado"
    
    # Verificar si el modelo está descargado
    if ollama list 2>/dev/null | grep -q "gemma4"; then
        print_info "Modelo Gemma 4 ya está descargado"
    else
        print_warn "Modelo Gemma 4 no está descargado"
        echo ""
        echo -n "¿Quieres descargarlo ahora? (s/n): "
        read -r response
        if [[ "$response" =~ ^[Ss]$ ]]; then
            print_info "Descargando Gemma 4... (esto puede tardar varios minutos)"
            ollama pull gemma4:4b-instruct-q4_K_M
        fi
    fi
else
    print_warn "Ollama no está instalado"
    print_info "Para instalar Ollama, ejecuta:"
    echo "   curl -fsSL https://ollama.com/install.sh | sh"
fi

echo ""

# ============================================
# 5. Verificar cámaras
# ============================================
print_info "Detectando cámaras web..."

CAMERAS=()
while IFS= read -r line; do
    if [[ -n "$line" ]]; then
        CAMERAS+=("$line")
    fi
done < <(ls /dev/video* 2>/dev/null || true)

if [ ${#CAMERAS[@]} -eq 0 ]; then
    print_warn "No se detectaron cámaras web"
    print_warn "La visión estará deshabilitada por defecto"
    if grep -q "^VISION_ENABLED=" .env; then
        sed -i "s|^VISION_ENABLED=.*|VISION_ENABLED=false|" .env
    else
        echo "VISION_ENABLED=false" >> .env
    fi
else
    print_info "Cámaras encontradas:"
    for camera in "${CAMERAS[@]}"; do
        echo "   - $camera"
    done
    print_info "Visión habilitada (puedes deshabilitarla en .env)"
fi

echo ""

# ============================================
# 6. Crear directorios necesarios
# ============================================
print_info "Creando directorios necesarios..."

mkdir -p data logs tests data/piper_voices
print_info "Directorios creados: data/, logs/, tests/"

echo ""

# ============================================
# 7. Configurar permisos (solo Linux)
# ============================================
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    print_info "Configurando permisos de hardware..."
    
    # Añadir usuario al grupo dialout
    if groups $USER | grep -q dialout; then
        print_info "Usuario ya está en grupo dialout"
    else
        print_warn "Añadiendo usuario al grupo dialout (requiere sudo)"
        sudo usermod -a -G dialout $USER || print_warn "No se pudo añadir al grupo dialout"
        print_warn "Debes cerrar sesión y volver a entrar para que surta efecto"
    fi
    
    # Crear regla udev
    if [ -d "/etc/udev/rules.d" ]; then
        print_info "Creando regla udev para Arduino..."
        cat << 'EOF' | sudo tee /etc/udev/rules.d/99-arduino.rules > /dev/null
SUBSYSTEM=="tty", ATTRS{idVendor}=="2341", MODE="0666"
SUBSYSTEM=="tty", ATTRS{idVendor}=="2a03", MODE="0666"
EOF
        sudo udevadm control --reload-rules
        sudo udevadm trigger
        print_info "Regla udev creada"
    fi
fi

echo ""

# ============================================
# 8. Resumen final
# ============================================
echo "=================================================="
print_info "¡CONFIGURACIÓN COMPLETADA!"
echo "=================================================="
echo ""
echo "📋 Resumen de configuración:"
echo "   - Arduino:     $CURRENT_ARDUINO"
echo "   - Navegador:   $BROWSER"
echo "   - Directorios: data/, logs/, tests/"
echo ""
echo "📁 Archivo .env actualizado en: $(pwd)/.env"
echo ""
echo "🚀 Próximos pasos:"
echo "   1. Revisa el archivo .env y ajusta lo necesario"
echo "   2. Si instalaste Ollama, inicia el servicio: ollama serve"
echo "   3. Activa el entorno virtual: source venv/bin/activate"
echo "   4. Ejecuta el agente: python -m src.agent.abuelo_agent"
echo ""
echo "📖 Para más información, consulta: docs/GUIA_CONFIGURACION.md"
echo "=================================================="
