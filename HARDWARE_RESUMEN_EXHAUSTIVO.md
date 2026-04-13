# 📋 Resumen Exhaustivo de Hardware - Abuelo Agent

## Visión General del Proyecto

**Abuelo Agent** es un asistente de voz multimodal local diseñado específicamente para personas mayores, optimizado para funcionar en hardware AMD BC250 con Gemma 4. Permite controlar televisores tradicionales mediante comandos de voz e infrarrojos, combinando IA de vanguardia con hardware accesible.

---

## 🖥️ HARDWARE PRINCIPAL (Computadora)

### Especificaciones Mínimas Recomendadas

| Componente | Especificación | Notas |
|------------|---------------|-------|
| **APU/CPU** | AMD BC250 o equivalente | Zen 2 + RDNA2 integrado |
| **VRAM** | 16GB GDDR6 (compartida) | Mínimo 8GB dedicados al modelo |
| **RAM Sistema** | 16GB DDR4 | Para sistema operativo y aplicaciones |
| **Almacenamiento** | 256GB NVMe SSD | Para modelos de IA y sistema |
| **Salida Video** | HDMI 2.0+ | Para conectar al TV |
| **Puertos USB** | 3x USB 3.0 | Para Arduino, cámara web, periféricos |

### Hardware Alternativo Compatible

#### Opción 1: Mini PC AMD
- **Beelink SER5 MAX**: AMD Ryzen 7 5800H, 16GB RAM, 500GB SSD
- **Minisforum UM780 XTX**: AMD Ryzen 7 7840HS, Radeon 780M
- **Precio aproximado**: $350-450 USD

#### Opción 2: Laptop AMD
- Cualquier laptop con Ryzen 5000/6000/7000 series
- Gráficos integrados Radeon (RDNA2 o superior)
- Mínimo 16GB RAM

#### Opción 3: Desktop AMD
- CPU: Ryzen 5 5600G o superior
- GPU integrada: Vega o RDNA2
- RAM: 32GB dual-channel (mejor rendimiento)

### Optimización para BC250

El AMD BC250 es ideal porque:
- **Arquitectura RDNA2**: Soporte nativo Vulkan para aceleración de IA
- **16GB GDDR6**: Suficiente VRAM para Gemma 4 4B cuantizado
- **Bajo consumo**: ~15-25W TDP, funcionamiento silencioso
- **Rendimiento**: 50-60 tokens/segundo con Vulkan

### Gestión de Memoria VRAM

| Uso | VRAM Requerida |
|-----|----------------|
| Gemma 4 4B (Q4_K_M) | ~2.6 GB |
| Sistema Operativo | ~1-2 GB |
| Navegador (YouTube) | ~1-2 GB |
| Cámara Web + Visión | ~0.5-1 GB |
| **Total recomendado** | **~11-12 GB libres** |

---

## 🔌 HARDWARE DE CONTROL IR (Arduino)

### Componentes Necesarios

#### 1. Placa Arduino
| Modelo | Precio | Notas |
|--------|--------|-------|
| **Arduino Nano** | $3-5 USD | ✅ Recomendado (compacto, USB integrado) |
| Arduino Uno | $5-8 USD | Más grande pero más robusto |
| Arduino Pro Micro | $4-6 USD | Alternativa compacta |
| Clon CH340 | $2-3 USD | Económico, requiere drivers |

**Especificaciones técnicas:**
- Microcontrolador: ATmega328P (16MHz, 5V)
- Pines digitales: 14 (6 PWM)
- Conexión: USB mini/micro
- Consumo: ~20mA

#### 2. LED Infrarrojo
| Componente | Especificación | Precio |
|------------|---------------|--------|
| **LED IR 940nm** | 5mm, 100mW | $0.50-1 USD |
| LED IR 850nm | 5mm, mayor alcance | $0.50-1 USD |
| Módulo TSAL6100 | Vishay, alta potencia | $1-2 USD |

**Recomendación:** Usar 940nm (invisible) para no molestar visualmente.

#### 3. Resistencia para LED IR
| Valor | Potencia | Función |
|-------|----------|---------|
| **220Ω** | 1/4W | Limitar corriente a ~20mA |
| 150Ω | 1/4W | Mayor intensidad (~30mA) |
| 330Ω | 1/4W | Menor intensidad (~15mA) |

**Cálculo:** (5V - 1.2V LED) / 220Ω = 17mA (seguro para LED y pin Arduino)

#### 4. Botón Físico
| Tipo | Especificación | Notas |
|------|---------------|-------|
| **Botón pulsador NA** | 12mm, 250mA | Normalmente abierto |
| Botón con LED | 12mm, luz integrada | Feedback visual opcional |
| Botón grande | 30mm, fácil presión | ✅ Ideal para adultos mayores |

**Características recomendadas:**
- Tamaño grande (fácil de presionar)
- Fuerza de activación suave
- Con o sin luz LED indicadora
- Montaje en caja accesible

#### 5. Cables y Conectores
- **Cables jumper Macho-Macho**: 10-15 unidades
- **Protoboard pequeña**: 400 puntos (opcional para pruebas)
- **Cable USB A-Mini/Micro**: Para conectar Arduino al PC

---

## 📡 ESQUEMA DE CONEXIONES ARDUINO

### Diagrama de Cableado

```
                    ARDUINO NANO
                 ┌─────────────────┐
                 │                 │
    BOTÓN ───────┤ D2          D3 ├──┬── RESISTENCIA 220Ω ──┬── LED IR (+)
    (GND)        │                 │  │                      │
       │         │           GND ├───┴──────────────────────┴── LED IR (-)
       │         │                 │
       └─────────┤ 5V              │
                 │                 │
                 │      USB        │
                 └────────┬────────┘
                          │
                     PC/Laptop
```

### Conexiones Detalladas

#### Pin D2 - Botón Físico
```
Arduino D2 ───┬─── Botón Terminal 1
              │
              └─── GND (usando INPUT_PULLUP interno)
```

**Configuración:** `INPUT_PULLUP` (resistencia interna activada)
- Estado reposo: HIGH (5V)
- Estado presionado: LOW (GND)
- No requiere resistencia externa

#### Pin D3 - LED IR
```
Arduino D3 ─── Resistor 220Ω ─── LED IR Ánodo (+)
                                  │
GND ──────────────────────────────┴── LED IR Cátodo (-)
```

**Nota:** El cátodo del LED es la pata más corta o el lado plano.

#### Alimentación
- Arduino se alimenta vía USB (5V)
- No requiere fuente externa
- Consumo total: ~40-50mA (Arduino + LED IR)

---

## 📷 CÁMARA WEB (Opcional para Visión)

### Requisitos
| Especificación | Mínima | Recomendada |
|---------------|--------|-------------|
| **Resolución** | 640x480 | 1280x720 |
| **FPS** | 15 fps | 30 fps |
| **Conexión** | USB 2.0 | USB 3.0 |
| **Enfoque** | Fijo | Autofocus |
| **Micrófono** | No necesario | No necesario |

### Modelos Compatibles
- **Logitech C270**: 720p, económico ($25 USD)
- **Logitech C920**: 1080p, excelente calidad ($70 USD)
- **Cámara genérica UVC**: Cualquier webcam USB estándar

**Nota:** La cámara se usa para detectar si el TV está encendido/apagado mediante visión computacional.

---

## 📺 COMPATIBILIDAD CON TELEVISORES

### Marcas Soportadas por IR

| Marca | Protocolo IR | Comandos Soportados |
|-------|-------------|---------------------|
| **Samsung** | NEC | ✅ Power, Volumen, Canal, HDMI, Netflix, YouTube |
| LG | NEC/Fujitsu | ✅ Power, Volumen, Canal, HDMI |
| Sony | SIRC | ✅ Power, Volumen, Canal, HDMI |
| Panasonic | RC-5/NEC | ✅ Power, Volumen, Canal, HDMI |
| TCL | NEC | ✅ Power, Volumen, Canal, HDMI |
| Hisense | NEC | ✅ Power, Volumen, Canal, HDMI |
| Philips | RC-5 | ✅ Power, Volumen, Canal, HDMI |

### Códigos IR por Comando (Ejemplo Samsung)

```cpp
// Códigos NEC para Samsung TV
#define POWER     0x04FB55AA
#define VOL_UP    0x04FB40BF
#define VOL_DOWN  0x04FB20DF
#define MUTE      0x04FB45BA
#define CH_UP     0x04FB15EA
#define CH_DOWN   0x04FB35CA
#define HDMI1     0x04FB807F
#define HDMI2     0x04FB609F
#define NETFLIX   0x04FBF00F
#define YOUTUBE   0x04FB906F
```

### Cómo Obtener Códigos IR de tu TV

1. **Buscar en internet**: "Samsung TV IR codes NEC"
2. **Usar módulo receptor IR**: TSOP38238 + Arduino
3. **Base de datos LIRC**: https://lirc.sourceforge.net/remotes/
4. **Aprender desde control remoto**: Usar módulo IR learning

---

## 🛠️ HERRAMIENTAS NECESARIAS

### Para Ensamblaje
- [ ] Cautín (soldador) 25-40W
- [ ] Estaño para electrónica
- [ ] Pelacables
- [ ] Pinzas de punta fina
- [ ] Cinta aislante o termocontraíble
- [ ] Multímetro (opcional para verificar conexiones)

### Para Programación Arduino
- [ ] Computadora con Arduino IDE instalado
- [ ] Cable USB compatible con Arduino
- [ ] Drivers CH340 (si es clon chino)

### Para Configuración de Software
- [ ] Acceso a internet (para descargar modelos)
- [ ] Permisos de administrador/sudo
- [ ] Cuenta de usuario en Linux

---

## 💰 PRESUPUESTO ESTIMADO

### Opción Económica (Clones)

| Componente | Cantidad | Precio Unitario | Total |
|------------|----------|-----------------|-------|
| Arduino Nano (clon) | 1 | $3 USD | $3 |
| LED IR 940nm | 2 | $0.50 | $1 |
| Resistencia 220Ω | 5 | $0.10 | $0.50 |
| Botón pulsador | 1 | $0.50 | $0.50 |
| Cables jumper | 10 | $0.05 | $0.50 |
| Webcam genérica | 1 | $15 | $15 |
| **Total hardware IR** | | | **$20.50 USD** |

### Opción Calidad (Originales)

| Componente | Cantidad | Precio Unitario | Total |
|------------|----------|-----------------|-------|
| Arduino Nano (original) | 1 | $8 USD | $8 |
| Módulo IR TSAL6100 | 1 | $2 | $2 |
| Resistencia 220Ω | 5 | $0.10 | $0.50 |
| Botón grande con LED | 1 | $3 | $3 |
| Cables calidad | 10 | $0.10 | $1 |
| Logitech C270 | 1 | $25 | $25 |
| Caja protectora | 1 | $5 | $5 |
| **Total hardware IR** | | | **$44.50 USD** |

### Costo Total del Proyecto

| Escenario | Hardware IR | PC/Laptop | Total |
|-----------|-------------|-----------|-------|
| **Mínimo** (ya tienes PC) | $20 | $0 | **$20 USD** |
| **Recomendado** | $45 | $0 | **$45 USD** |
| **Completo** (con Mini PC) | $45 | $400 | **$445 USD** |
| **Premium** (laptop nueva) | $60 | $700 | **$760 USD** |

---

## 🔧 MANTENIMIENTO Y REEMPLAZOS

### Vida Útil Estimada

| Componente | Duración | Reemplazo |
|------------|----------|-----------|
| LED IR | 50,000 horas | Cada 5-10 años |
| Botón físico | 100,000 pulsaciones | Cada 2-5 años |
| Arduino | Ilimitado | Rara vez |
| Webcam | 3-5 años | Según desgaste |

### Problemas Comunes y Soluciones

| Problema | Causa Probable | Solución |
|----------|----------------|----------|
| TV no responde | LED IR mal orientado | Apuntar directamente al sensor IR del TV |
| Alcance corto | Corriente insuficiente | Usar resistor 150Ω en lugar de 220Ω |
| Falsos positivos | Rebote del botón | Ajustar debounce en firmware (50ms) |
| Arduino no detectado | Drivers faltantes | Instalar drivers CH340/CP2102 |
| Cámara no funciona | Permiso USB | `sudo usermod -aG video $USER` |

---

## 📦 LISTA DE COMPRA RESUMIDA

### Para Imprimir y Llevar a la Tienda

```
☐ Arduino Nano (con cable USB)
☐ LED infrarrojo 940nm (5mm)
☐ Resistencia 220Ω 1/4W (5 unidades)
☐ Botón pulsador normalmente abierto (grande)
☐ Cables jumper macho-macho (10 unidades)
☐ Webcam USB 720p mínimo
☐ Protoboard pequeña (opcional)
☐ Cinta termocontraíble (opcional)
```

### Enlaces de Compra Recomendados

- **Amazon**: Buscar "Arduino Nano kit", "IR LED 940nm"
- **AliExpress**: Kits completos más económicos (envío 2-4 semanas)
- **Tiendas locales**: Electrónica, robótica, maker spaces
- **Mercado Libre**: Opciones regionales con envío rápido

---

## ⚠️ ADVERTENCIAS DE SEGURIDAD

1. **Voltaje bajo**: Arduino trabaja a 5V, seguro al tacto
2. **No conectar a 220V**: Solo usar alimentación USB
3. **LED IR**: No mirar directamente por periodos largos
4. **Soldadura**: Usar precaución con cautín caliente
5. **USB**: Conectar/desconectar con PC apagado preferiblemente

---

## 🎯 SIGUIENTES PASOS

Una vez adquirido todo el hardware:

1. **Ensamblar circuito** según diagrama
2. **Programar Arduino** con el firmware incluido
3. **Instalar software** en PC/Laptop (ver Manual de Software)
4. **Configurar códigos IR** para tu TV específico
5. **Probar comandos** básicos (power, volumen)
6. **Personalizar** configuración según necesidades

**Documentación completa disponible en:**
- `MANUAL_INSTALACION_SOFTWARE.md` (guía paso a paso de software)
- `/src/hardware/arduino_firmware/ir_button_controller.ino` (código Arduino)
- `/config/settings.yaml` (archivo de configuración)
