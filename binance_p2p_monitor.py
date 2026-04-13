#!/usr/bin/env python3
"""
Bot de Monitoreo Binance P2P - Versión FINAL SIMPLE
Monitorea el badge de "Órdenes" para detectar nuevas órdenes
"""

import asyncio
import json
import random
from datetime import datetime
from playwright.async_api import async_playwright
from vault import SecureVault

# ====== CONFIGURACIÓN ======
MYADS_URL = "https://p2p.binance.com/es-LA/myads?type=normal&code=default"
ORDERS_URL = "https://p2p.binance.com/es-LA/fiatOrder?tab=1&page=1"
CHECK_INTERVAL_MIN = 60  # segundos
CHECK_INTERVAL_MAX = 90
KNOWN_ORDERS_FILE = "known_orders.json"

# ====== CARGAR CREDENCIALES ======
vault = SecureVault()
credentials = vault.load_credentials()

# ====== FUNCIONES AUXILIARES ======
def load_known_orders():
    """Cargar IDs de órdenes ya procesadas"""
    try:
        with open(KNOWN_ORDERS_FILE, 'r') as f:
            return set(json.load(f))
    except:
        return set()

def save_known_orders(orders):
    """Guardar IDs de órdenes procesadas"""
    with open(KNOWN_ORDERS_FILE, 'w') as f:
        json.dump(list(orders), f)

async def login_binance(page):
    """Login a Binance con credenciales del vault"""
    print("🔑 Iniciando sesión en Binance...")
    
    try:
        # Ir a login
        await page.goto("https://accounts.binance.com/es-LA/login")
        await page.wait_for_load_state('networkidle')
        
        # Llenar email
        await page.fill('input[name="email"]', credentials['binance']['email'])
        await asyncio.sleep(random.uniform(0.5, 1.5))
        
        # Llenar password
        await page.fill('input[name="password"]', credentials['binance']['password'])
        await asyncio.sleep(random.uniform(0.5, 1.5))
        
        # Click login
        await page.click('button[type="submit"]')
        await page.wait_for_load_state('networkidle')
        
        # TOTP
        import pyotp
        totp = pyotp.TOTP(credentials['binance']['totp_secret'])
        code = totp.now()
        
        # Buscar input de TOTP (varios selectores posibles)
        totp_selectors = [
            'input[placeholder*="código"]',
            'input[placeholder*="code"]',
            'input[type="text"]',
            'input[autocomplete="one-time-code"]'
        ]
        
        for selector in totp_selectors:
            try:
                await page.fill(selector, code)
                break
            except:
                continue
        
        await asyncio.sleep(random.uniform(1, 2))
        
        # Submit TOTP
        await page.keyboard.press('Enter')
        await page.wait_for_load_state('networkidle')
        
        print("✅ Login exitoso")
        return True
        
    except Exception as e:
        print(f"❌ Error en login: {e}")
        return False

async def check_orders_badge(page):
    """Verifica si hay un número en el badge de Órdenes"""
    try:
        # Buscar el badge de órdenes
        # El badge suele estar en un elemento con clase badge o similar
        badge_selectors = [
            'text=Órdenes >> .. >> span.badge',
            '[href*="fiatOrder"] span',
            'a:has-text("Órdenes") span'
        ]
        
        for selector in badge_selectors:
            try:
                badge = await page.query_selector(selector)
                if badge:
                    text = await badge.text_content()
                    if text and text.strip().isdigit():
                        count = int(text.strip())
                        if count > 0:
                            print(f"   📊 Órdenes activas: {count}")
                            return count
            except:
                continue
        
        # Si no encontramos badge con número, asumir 0
        return 0
        
    except Exception as e:
        print(f"   ⚠️  Error al verificar badge: {e}")
        return 0

async def extract_active_orders(page):
    """Extrae datos de órdenes activas"""
    try:
        await page.goto(ORDERS_URL)
        await page.wait_for_load_state('networkidle')
        
        # Esperar un poco para que cargue
        await asyncio.sleep(2)
        
        # Extraer HTML completo
        html = await page.content()
        
        # Usar Ollama para analizar
        import ollama
        
        response = ollama.generate(
            model='llama3.2:3b',
            prompt=f"""
            Analiza este HTML de la página de órdenes de Binance P2P.
            Extrae SOLO las órdenes que están "En proceso" (NO las completadas).
            
            Para cada orden EN PROCESO extrae:
            - Número de orden (20 dígitos)
            - Tipo (Venta USDT)
            - Precio en VES (bolívares)
            - Monto en fiat/cripto
            - Contraparte (nombre del comprador)
            - Estado
            
            HTML (primeros 50k):
            {html[:50000]}
            
            Responde SOLO con JSON válido:
            {{
                "ordenes_activas": [
                    {{
                        "numero": "...",
                        "precio_ves": ...,
                        "monto_usdt": ...,
                        "monto_ves": ...,
                        "comprador": "...",
                        "estado": "..."
                    }}
                ]
            }}
            
            Si NO hay órdenes en proceso, responde: {{"ordenes_activas": []}}
            """
        )
        
        # Parsear respuesta
        import re
        response_text = response['response']
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        
        if json_match:
            data = json.loads(json_match.group())
            return data.get('ordenes_activas', [])
        
        return []
        
    except Exception as e:
        print(f"   ❌ Error al extraer órdenes: {e}")
        return []

async def notify_telegram(message):
    """Envía notificación por Telegram"""
    try:
        import requests
        
        token = credentials['telegram']['bot_token']
        chat_id = credentials['telegram']['chat_id']
        
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print("   📱 Notificación enviada a Telegram")
        else:
            print(f"   ⚠️  Error al enviar Telegram: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error en Telegram: {e}")

async def main():
    """Función principal del bot"""
    
    print("=" * 60)
    print("BOT DE MONITOREO BINANCE P2P - MODO SIMPLE")
    print("=" * 60)
    print()
    print("✅ Credenciales cargadas del vault")
    print(f"📧 Email Binance: {credentials['binance']['email'][:3]}***")
    print(f"💬 Telegram Chat ID: {credentials['telegram']['chat_id']}")
    print()
    
    known_orders = load_known_orders()
    print(f"📝 Órdenes conocidas: {len(known_orders)}")
    print()
    
    async with async_playwright() as p:
        # Lanzar navegador
        browser = await p.chromium.launch(
            headless=False,  # Visible para debug inicial
            args=['--start-maximized']
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            locale='es-VE',
            timezone_id='America/Caracas'
        )
        
        page = await context.new_page()
        
        # Login inicial
        if not await login_binance(page):
            print("❌ No se pudo iniciar sesión. Abortando.")
            await browser.close()
            return
        
        # Esperar un poco después del login
        await asyncio.sleep(5)
        
        # Ir a "Mis anuncios"
        await page.goto(MYADS_URL)
        await page.wait_for_load_state('networkidle')
        
        print("🔄 Iniciando monitoreo...")
        print()
        
        iteration = 0
        
        while True:
            iteration += 1
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            print(f"[{timestamp}] Check #{iteration}")
            
            try:
                # Refrescar página
                await page.reload()
                await page.wait_for_load_state('networkidle')
                
                # Verificar badge de órdenes
                order_count = await check_orders_badge(page)
                
                if order_count > 0:
                    print(f"   🔔 ÓRDENES ACTIVAS DETECTADAS: {order_count}")
                    
                    # Extraer detalles
                    active_orders = await extract_active_orders(page)
                    
                    for order in active_orders:
                        order_id = order.get('numero', 'UNKNOWN')
                        
                        if order_id not in known_orders:
                            # NUEVA ORDEN!
                            print()
                            print("   " + "=" * 50)
                            print("   🚨 NUEVA ORDEN DETECTADA")
                            print("   " + "=" * 50)
                            print(f"   Número: {order_id}")
                            print(f"   Comprador: {order.get('comprador', 'N/A')}")
                            print(f"   Monto: {order.get('monto_usdt', 'N/A')} USDT")
                            print(f"   Monto: {order.get('monto_ves', 'N/A')} Bs")
                            print(f"   Precio: {order.get('precio_ves', 'N/A')} Bs/USDT")
                            print(f"   Estado: {order.get('estado', 'N/A')}")
                            print("   " + "=" * 50)
                            print()
                            
                            # Notificar Telegram
                            message = f"""
🔔 <b>NUEVA ORDEN DE VENTA</b>

📋 Orden: <code>{order_id}</code>
👤 Comprador: {order.get('comprador', 'N/A')}
💰 Monto: {order.get('monto_usdt', 'N/A')} USDT
💵 Total: {order.get('monto_ves', 'N/A')} Bs
📊 Precio: {order.get('precio_ves', 'N/A')} Bs/USDT
📌 Estado: {order.get('estado', 'N/A')}

🔗 <a href="{ORDERS_URL}">Ver orden en Binance</a>

⏰ {timestamp}
                            """.strip()
                            
                            await notify_telegram(message)
                            
                            # Marcar como conocida
                            known_orders.add(order_id)
                            save_known_orders(known_orders)
                else:
                    print("   ✅ Sin órdenes activas")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
            
            # Esperar intervalo aleatorio
            wait_time = random.randint(CHECK_INTERVAL_MIN, CHECK_INTERVAL_MAX)
            print(f"   💤 Esperando {wait_time} segundos...")
            print()
            
            await asyncio.sleep(wait_time)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n✅ Bot detenido por usuario")
