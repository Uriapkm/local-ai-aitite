#!/bin/bash
# ============================================
# Script de Instalación - Abuelo IA con Gemma 4
# Optimizado para AMD BC250 (RDNA2) en Bazzite
# ============================================

set -e  # Detener en caso de error

echo "╔══════════════════════════════════════════════════╗"
echo "║  🚀 Instalación de Abuelo IA con Gemma 4        ║"
echo "║  Optimizado para AMD BC250 (RDNA2 + Vulkan)     ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

# Verificar que estamos en Bazzite/Fedora
if [ ! -f /etc/fedora-release ] && [ ! -f /etc/bazzite-release ]; then
    print_warning "Este script está optimizado para Bazzite/Fedora"
    print_warning "Puede que necesites ajustes en otros sistemas"
fi

# Paso 1: Actualizar sistema
print_info "Paso 1/8: Actualizando sistema..."
sudo dnf upgrade --refresh -y || {
    print_error "Falló la actualización del sistema"
    exit 1
}
print_success "Sistema actualizado"

# Paso 2: Instalar dependencias del sistema
print_info "Paso 2/8: Instalando dependencias del sistema..."
sudo dnf install -y \
    python3 \
    python3-pip \
    python3-devel \
    python3-venv \
    git \
    curl \
    wget \
    gcc \
    gcc-c++ \
    make \
    cmake \
    portaudio-devel \
    libsndfile-devel \
    ffmpeg \
    libxcb \
    vulkan-loader \
    vulkan-tools \
    mesa-vulkan-drivers \
    mesa-dri-drivers \
    libdrm \
    rocm-hip-sdk \
    rocm-opencl-sdk \
    ollama

if [ $? -eq 0 ]; then
    print_success "Dependencias instaladas"
else
    print_error "Falló la instalación de dependencias"
    exit 1
fi

# Paso 3: Configurar entorno virtual Python
print_info "Paso 3/8: Configurando entorno virtual Python..."
if [ -d "venv" ]; then
    print_warning "Entorno virtual ya existe, recreando..."
    rm -rf venv
fi

python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
print_success "Entorno Python configurado"

# Paso 4: Instalar dependencias Python
print_info "Paso 4/8: Instalando dependencias de Python..."
pip install -r requirements.txt || {
    print_error "Falló la instalación de dependencias Python"
    exit 1
}
print_success "Dependencias Python instaladas"

# Paso 5: Instalar Ollama y descargar Gemma 4
print_info "Paso 5/8: Configurando Ollama y descargando Gemma 4..."

# Verificar si Ollama ya está instalado
if ! command -v ollama &> /dev/null; then
    print_warning "Ollama no encontrado, instalando..."
    curl -fsSL https://ollama.ai/install.sh | sh
fi

# Iniciar Ollama como servicio
print_info "Iniciando servicio Ollama..."
systemctl --user enable ollama.service 2>/dev/null || true
systemctl --user start ollama.service 2>/dev/null || {
    print_warning "No se pudo iniciar como servicio, iniciando manualmente..."
    ollama serve > /dev/null 2>&1 &
    sleep 3
}

# Descargar Gemma 4 optimizado para BC250
print_info "Descargando Gemma 4 (4B instruct quantizado)..."
print_info "Este paso puede tardar 5-15 minutos dependiendo de tu conexión..."

# Usar la versión específica recomendada para BC250
OLLAMA_MODEL="gemma4:4b-instruct-q4_K_M"

# Verificar si ya existe el modelo
if ollama list | grep -q "gemma4"; then
    print_success "Gemma 4 ya está instalado"
else
    ollama pull $OLLAMA_MODEL
    if [ $? -eq 0 ]; then
        print_success "Gemma 4 descargado exitosamente"
    else
        print_error "Falló la descarga de Gemma 4"
        print_warning "Intentando con gemma2:9b como fallback..."
        ollama pull gemma2:9b
        OLLAMA_MODEL="gemma2:9b"
    fi
fi

# Paso 6: Configurar variables de entorno para Vulkan/ROCm
print_info "Paso 6/8: Configurando GPU para AMD BC250..."

# Crear archivo .env con configuración optimizada
cat > .env << EOF
# ============================================
# Configuración Abuelo IA - AMD BC250
# ============================================

# Hardware Arduino (AJUSTAR SEGÚN TU SISTEMA)
ARDUINO_PORT=/dev/ttyACM0

# LLM - Gemma 4 Multimodal
OLLAMA_MODEL=$OLLAMA_MODEL
OLLAMA_OLLAMA_HOST=http://localhost:11434
OLLAMA_USE_VULKAN=true

# Audio
AUDIO_WHISPER_MODEL=small
AUDIO_WHISPER_DEVICE=cpu
AUDIO_PIPER_VOICE=es_ES-carlfm-medium

# Visión
VISION_ENABLED=true
VISION_CAMERA_INDEX=0

# Navegador
YOUTUBE_BROWSER=brave

# Vulkan optimizations for RDNA2
export VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/radeon_icd.x86_64.json
export RADV_PERFTEST=sam,nggc
export MESA_GL_VERSION_OVERRIDE=4.6
EOF

print_success "Archivo .env creado con configuración optimizada"

# Paso 7: Crear directorios necesarios
print_info "Paso 7/8: Creando estructura de directorios..."
mkdir -p data/piper_voices
mkdir -p logs
mkdir -p captures
print_success "Directorios creados"

# Paso 8: Verificación final
print_info "Paso 8/8: Verificando instalación..."

# Verificar Ollama
if ollama list | grep -q "gemma"; then
    print_success "✅ Ollama + Gemma funcionando"
else
    print_error "❌ Ollama o Gemma no están disponibles"
    exit 1
fi

# Verificar Python packages
if python -c "import speechrecognition" 2>/dev/null; then
    print_success "✅ Dependencias Python OK"
else
    print_warning "⚠️  Algunas dependencias Python pueden faltar"
fi

# Mostrar resumen
echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║           ✅ INSTALACIÓN COMPLETADA              ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""
echo "📋 Resumen de configuración:"
echo "   - Modelo LLM: $OLLAMA_MODEL"
echo "   - GPU Backend: Vulkan (optimizado para RDNA2)"
echo "   - Puerto Arduino: /dev/ttyACM0 (ajustar si es necesario)"
echo ""
echo "🚀 Próximos pasos:"
echo "   1. Conecta el Arduino y verifica el puerto:"
echo "      ls /dev/ttyACM*"
echo ""
echo "   2. Ajusta el puerto en .env si es necesario:"
echo "      nano .env"
echo ""
echo "   3. Activa el entorno virtual:"
echo "      source venv/bin/activate"
echo ""
echo "   4. Ejecuta el agente:"
echo "      python src/main.py"
echo ""
echo "📖 Para más información, consulta:"
echo "   docs/GUIA_CONFIGURACION.md"
echo ""
print_success "¡Listo para usar!"
