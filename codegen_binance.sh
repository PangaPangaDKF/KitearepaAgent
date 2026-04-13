#!/bin/bash
# Script para abrir Playwright CodeGen con configuración correcta para Binance C2C

echo "=================================================="
echo "PLAYWRIGHT CODEGEN - BINANCE C2C"
echo "=================================================="
echo ""
echo "✅ Configuración:"
echo "   - URL: https://c2c.binance.com/es-LA/myads"
echo "   - Viewport: 1920x1080"
echo "   - Locale: es-VE"
echo ""
echo "⚠️  IMPORTANTE:"
echo "   - Después de que se abra el navegador"
echo "   - Usa CTRL+SHIFT+I para ajustar zoom a 75%"
echo "   - O usa el menú: View → Zoom → Zoom Out"
echo ""
echo "Abriendo en 3 segundos..."
sleep 3

# Ejecutar playwright codegen con la configuración correcta
playwright codegen \
  --viewport-size=1920,1080 \
  --user-agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36" \
  --color-scheme=dark \
  "https://c2c.binance.com/es-LA/myads?type=normal&code=default"
