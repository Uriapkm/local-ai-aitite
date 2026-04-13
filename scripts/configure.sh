#!/bin/bash
# Configuración - Abuelo IA Assistant
set -e

echo "⚙️  Configurando Abuelo IA"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_info() { echo -e "${GREEN}✓${NC} $1"; }
print_warn() { echo -e "${YELLOW}⚠${NC} $1"; }

# Copiar .env
if [ ! -f .env ]; then
    print_info "Creando .env desde .env.example..."
    cp .env.example .env
else
    print_warn ".env ya existe"
fi

# Detectar puerto Arduino
print_info "Detectando Arduino..."
ARDUINO_PORT=$(ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null | head -1)
if [ -n "$ARDUINO_PORT" ]; then
    print_info "Arduino encontrado en $ARDUINO_PORT"
    sed -i "s|ARDUINO_PORT=.*|ARDUINO_PORT=$ARDUINO_PORT|" .env
else
    print_warn "No se encontró Arduino, edita .env manualmente"
fi

# Permisos
print_info "Configurando permisos..."
sudo setfacl -m u:$USER:rw /dev/ttyUSB0 2>/dev/null || true
sudo usermod -aG video $USER

# Crear directorios
print_info "Creando directorios..."
mkdir -p data logs

echo ""
print_info "✅ Configuración completada"
echo "Edita .env si necesitas ajustar algo"
