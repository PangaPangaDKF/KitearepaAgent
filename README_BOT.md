# Bot de Monitoreo Binance P2P - Guía Completa

## 🎯 ¿Qué hace este bot?

1. ✅ Hace login en Binance automáticamente
2. ✅ Monitorea tu página de "Mis anuncios"
3. ✅ Detecta cuando aparece un número en "Órdenes"
4. ✅ Extrae datos de la orden (comprador, monto, precio)
5. ✅ Notifica por Telegram
6. ✅ Repite cada 60-90 segundos

## 📋 Prerequisitos

- ✅ Vault inicializado con credenciales
- ✅ Ollama corriendo con llama3.2:3b
- ✅ Conexión a internet

## 🚀 Ejecución

```bash
# 1. Ir al proyecto
cd ~/binance-agent
source venv/bin/activate

# 2. Verificar que el vault está OK
python vault.py --verify

# 3. Ejecutar bot
python binance_p2p_monitor.py
```

## 📊 Output Esperado

```
============================================================
BOT DE MONITOREO BINANCE P2P - MODO SIMPLE
============================================================

✅ Credenciales cargadas del vault
📧 Email Binance: bey***
💬 Telegram Chat ID: 123456789

📝 Órdenes conocidas: 0

🔑 Iniciando sesión en Binance...
✅ Login exitoso
🔄 Iniciando monitoreo...

[14:30:25] Check #1
   ✅ Sin órdenes activas
   💤 Esperando 75 segundos...

[14:31:40] Check #2
   📊 Órdenes activas: 1
   🔔 ÓRDENES ACTIVAS DETECTADAS: 1
   
   ==================================================
   🚨 NUEVA ORDEN DETECTADA
   ==================================================
   Número: 22875659471647559680
   Comprador: TUCAMBIOSEGURO24
   Monto: 4.04 USDT
   Monto: 2,500,000 Bs
   Precio: 627.15 Bs/USDT
   Estado: En proceso
   ==================================================
   
   📱 Notificación enviada a Telegram
```

## 📱 Notificación de Telegram

```
🔔 NUEVA ORDEN DE VENTA

📋 Orden: 22875659471647559680
👤 Comprador: TUCAMBIOSEGURO24
💰 Monto: 4.04 USDT
💵 Total: 2,500,000 Bs
📊 Precio: 627.15 Bs/USDT
📌 Estado: En proceso

🔗 Ver orden en Binance
⏰ 14:31:40
```

## 🔧 Configuración

### Cambiar intervalo de monitoreo:

Edita `binance_p2p_monitor.py`:

```python
CHECK_INTERVAL_MIN = 60  # Mínimo segundos
CHECK_INTERVAL_MAX = 90  # Máximo segundos
```

### Modo headless (sin ventana):

```python
browser = await p.chromium.launch(
    headless=True,  # Cambiar a True
    args=['--start-maximized']
)
```

## 🐛 Problemas Comunes

### Error: "No se pudo iniciar sesión"

**Solución:**
- Verifica credenciales en vault
- Ejecuta: `python vault.py --verify`
- Confirma TOTP secret correcto

### Error: "Ollama no responde"

**Solución:**
```bash
# Verificar que Ollama está corriendo
ollama list

# Reiniciar Ollama
sudo systemctl restart ollama
```

### No detecta órdenes

**Solución:**
- Verifica que tienes un ad publicado
- Verifica que el ad está "En línea"
- Espera a que un cliente real abra orden
- O usa cuenta de prueba

## 📝 Archivos Generados

- `known_orders.json` - IDs de órdenes ya procesadas
- Evita notificaciones duplicadas

## ⏹️ Detener el Bot

Presiona: `Ctrl + C`

## 🔄 Próximas Mejoras

1. Detectar cuando cliente marca "Pagué"
2. Abrir banco automáticamente
3. Verificar transferencia bancaria
4. Leer Gmail para códigos OTP
5. Generar códigos 2FA automáticos

## 🆘 Soporte

Si algo no funciona:
1. Verifica logs del error
2. Confirma vault OK
3. Confirma Ollama corriendo
4. Confirma internet OK
