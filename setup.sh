#!/bin/bash
# Setup Completo del Agente Binance P2P
# Ejecutar: chmod +x setup.sh && ./setup.sh

set -e

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║    SETUP AGENTE BINANCE P2P + OLLAMA + VAULT            ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}[1/8] Instalando herramientas de sistema...${NC}"
sudo apt update
sudo apt install -y \
    flameshot \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    wget

echo -e "${GREEN}[2/8] Verificando Ollama...${NC}"
if command -v ollama &> /dev/null; then
    echo "✅ Ollama ya instalado"
else
    echo "⚠️  Ollama no detectado, instalando..."
    curl -fsSL https://ollama.com/install.sh | sh
fi

echo -e "${GREEN}[3/8] Descargando modelo Llama 3.2...${NC}"
ollama pull llama3.2:3b
echo "✅ Modelo descargado (2GB)"

echo -e "${GREEN}[4/8] Creando estructura del proyecto...${NC}"
mkdir -p ~/binance-agent
cd ~/binance-agent

# Crear directorios
mkdir -p logs
mkdir -p screenshots
mkdir -p session_data

echo -e "${GREEN}[5/8] Creando entorno virtual Python...${NC}"
python3 -m venv venv
source venv/bin/activate

echo -e "${GREEN}[6/8] Instalando dependencias Python...${NC}"
pip install --upgrade pip

cat > requirements.txt << 'EOF'
# Browser automation
playwright==1.48.0
playwright-stealth==1.0.6

# AI y LLM
ollama==0.1.6

# Autenticación y seguridad
pyotp==2.9.0
cryptography==42.0.5

# Notificaciones
python-telegram-bot==20.7

# Utilities
python-dotenv==1.0.0
aiofiles==23.2.1
EOF

pip install -r requirements.txt

echo "Instalando navegadores Playwright..."
playwright install chromium
playwright install-deps

echo -e "${GREEN}[7/8] Configurando Flameshot...${NC}"
echo "Para usar Flameshot:"
echo "  1. Presiona: Print Screen"
echo "  2. O ejecuta: flameshot gui"
echo ""
echo "Configurar atajo personalizado:"
echo "  Settings → Keyboard → Custom Shortcuts"
echo "  Comando: flameshot gui"
echo "  Atajo: Print Screen"

echo -e "${GREEN}[8/8] Creando archivos del proyecto...${NC}"

# Crear .gitignore
cat > .gitignore << 'EOF'
# Vault y credenciales
.binance-vault/
*.enc
*.key
*.backup

# Environment
venv/
*.env
.env.local

# Python
__pycache__/
*.py[cod]
*$py.class
*.so

# Logs
logs/
*.log

# Session data
session_data/
cookies.json
*.json

# Screenshots con datos sensibles
screenshots/*.png
screenshots/*.jpg

# Backups
backups/
*.backup

# IDE
.vscode/
.idea/
*.swp
EOF

# Crear README
cat > README.md << 'EOF'
# Agente Binance P2P - Venezuela

Agente inteligente para monitoreo automático de órdenes P2P en Binance.

## Stack

- **Automatización**: Playwright + playwright-stealth
- **Inteligencia**: Ollama (Llama 3.2 local)
- **Seguridad**: Vault cifrado (AES-256)
- **Notificaciones**: Telegram
- **2FA**: pyotp (TOTP)

## Instalación

```bash
chmod +x setup.sh
./setup.sh
```

## Configuración inicial

```bash
# 1. Activar entorno
source venv/bin/activate

# 2. Inicializar vault (primera vez)
python vault.py --init

# 3. Verificar vault
python vault.py --verify
```

## Uso

```bash
# Activar entorno
source venv/bin/activate

# Ejecutar bot
python main.py
```

## Seguridad

- ✅ Todas las credenciales cifradas con AES-256
- ✅ Contraseña maestra nunca almacenada
- ✅ Salt único por instalación
- ✅ Permisos de archivo restrictivos (600)
- ✅ Backups automáticos cifrados

## Estructura

```
~/binance-agent/
├── vault.py              # Sistema de cifrado
├── bot_example.py        # Ejemplo de uso del vault
├── main.py              # Bot principal (crear)
├── venv/                # Entorno virtual
├── logs/                # Logs del bot
├── screenshots/         # Screenshots de referencia
└── session_data/        # Cookies y sesiones
```

## Herramientas

- **Screenshots**: `flameshot gui` o Print Screen
- **Remote Desktop**: Chrome Remote Desktop
- **Logs**: `tail -f logs/bot.log`

## Backup

```bash
# Exportar backup
python vault.py --backup ~/backup_$(date +%Y%m%d).enc

# Cambiar contraseña maestra
python vault.py --change-pass
```
EOF

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              INSTALACIÓN COMPLETADA ✅                   ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "📁 Proyecto creado en: ~/binance-agent/"
echo ""
echo "📋 Próximos pasos:"
echo ""
echo "1. Activar entorno:"
echo "   cd ~/binance-agent"
echo "   source venv/bin/activate"
echo ""
echo "2. Inicializar vault (primera vez):"
echo "   python vault.py --init"
echo "   (Ingresa tus credenciales - serán cifradas)"
echo ""
echo "3. Verificar instalación:"
echo "   python vault.py --verify"
echo "   ollama run llama3.2:3b \"test\""
echo ""
echo "4. Configurar screenshots:"
echo "   flameshot gui"
echo ""
echo "5. (Opcional) Chrome Remote Desktop:"
echo "   https://remotedesktop.google.com/headless"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANTE - Seguridad:${NC}"
echo "   • Haz backup de ~/.binance-vault/"
echo "   • NO compartas archivos .enc"
echo "   • Usa contraseña maestra fuerte (12+ caracteres)"
echo "   • Guarda backup en lugar SEGURO"
echo ""
