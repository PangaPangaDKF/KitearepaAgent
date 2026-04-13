#!/bin/bash
# Iniciar Chrome con Remote Debugging
# Esto permite que el bot use TU sesión de Binance

echo "=================================================="
echo "INICIAR CHROME CON DEBUGGING"
echo "=================================================="
echo ""
echo "✅ Esto permite que el bot use tu sesión de Binance"
echo "✅ NO necesitas hacer login de nuevo"
echo "✅ El bot se conecta a TU Chrome"
echo ""

# Cerrar Chrome si está abierto
echo "🔄 Cerrando Chrome existente..."
pkill -f "chrome --remote-debugging-port" 2>/dev/null
sleep 2

# Iniciar Chrome con debugging
echo "🚀 Iniciando Chrome con debugging..."
google-chrome \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/.config/google-chrome/Default" \
  > /dev/null 2>&1 &

sleep 3

echo ""
echo "✅ Chrome iniciado con debugging en puerto 9222"
echo ""
echo "📋 PRÓXIMOS PASOS:"
echo "   1. Chrome se abrió (puede usar tu sesión existente)"
echo "   2. Si no estás logueado en Binance, haz login ahora"
echo "   3. Ve a: https://p2p.binance.com/es-LA/myads"
echo "   4. Deja Chrome abierto"
echo "   5. En otra terminal, ejecuta: python binance_p2p_monitor.py"
echo ""
echo "⚠️  IMPORTANTE:"
echo "    NO CIERRES Chrome mientras el bot está corriendo"
echo ""
