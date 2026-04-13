#!/usr/bin/env python3
"""
Bot Simple de Monitoreo P2P - Usa Chrome Existente
NO hace login - usa tu sesión activa
"""

import asyncio
import json
from playwright.async_api import async_playwright
import ollama
from datetime import datetime

# ====== CONFIGURACIÓN ======
BINANCE_URL = "https://p2p.binance.com/trade/sell/USDT?fiat=VES&payment=all-payments"
CHECK_INTERVAL = 90  # segundos entre checks
KNOWN_ORDERS_FILE = "known_orders.json"

# ====== CARGAR ÓRDENES CONOCIDAS ======
def load_known_orders():
    try:
        with open(KNOWN_ORDERS_FILE, 'r') as f:
            return set(json.load(f))
    except:
        return set()

def save_known_orders(orders):
    with open(KNOWN_ORDERS_FILE, 'w') as f:
        json.dump(list(orders), f)

# ====== FUNCIÓN PRINCIPAL ======
async def monitor_binance():
    """Monitorea Binance P2P usando Chrome existente"""
    
    known_orders = load_known_orders()
    
    async with async_playwright() as p:
        # Conectar a Chrome existente (debes iniciarlo con debugging)
        print("=" * 60)
        print("BOT DE MONITOREO BINANCE P2P - MODO SIMPLE")
        print("=" * 60)
        print()
        print("⚠️  PREREQUISITO:")
        print("   Chrome debe estar abierto con debugging habilitado")
        print("   Ejecuta primero:")
        print("   google-chrome --remote-debugging-port=9222")
        print()
        print("✅ Conectando a Chrome...")
        
        try:
            # Conectar a Chrome existente
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
            
            # Obtener contexto existente
            contexts = browser.contexts
            if not contexts:
                print("❌ No hay contextos abiertos en Chrome")
                return
            
            context = contexts[0]
            pages = context.pages
            
            # Buscar o crear página de Binance
            binance_page = None
            for page in pages:
                if "binance.com" in page.url:
                    binance_page = page
                    break
            
            if not binance_page:
                print("📄 Abriendo nueva pestaña de Binance...")
                binance_page = await context.new_page()
                await binance_page.goto(BINANCE_URL)
            
            print(f"✅ Conectado a: {binance_page.url}")
            print()
            print("🔄 Iniciando monitoreo...")
            print(f"   Intervalo: {CHECK_INTERVAL} segundos")
            print(f"   Órdenes conocidas: {len(known_orders)}")
            print()
            
            iteration = 0
            
            while True:
                iteration += 1
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                print(f"[{timestamp}] Check #{iteration}")
                
                try:
                    # Refrescar página
                    await binance_page.reload()
                    await binance_page.wait_for_load_state('networkidle')
                    
                    # Extraer HTML
                    html_content = await binance_page.content()
                    
                    # Ollama analiza
                    print("   🤖 Analizando con Ollama...")
                    
                    response = ollama.generate(
                        model='llama3.2:3b',
                        prompt=f"""
                        Analiza este HTML de Binance P2P (Vista de VENTA de USDT).
                        Extrae TODOS los anunciantes disponibles.
                        
                        Para cada anunciante extrae:
                        - Nombre del anunciante
                        - Precio en Bs (bolívares)
                        - Cantidad de USDT disponible
                        - Límites (mínimo y máximo en VES)
                        
                        HTML (fragmento):
                        {html_content[:30000]}
                        
                        Responde SOLO con JSON válido:
                        {{
                            "anunciantes": [
                                {{
                                    "nombre": "...",
                                    "precio_bs": ...,
                                    "usdt_disponible": ...,
                                    "limite_min_ves": ...,
                                    "limite_max_ves": ...
                                }}
                            ]
                        }}
                        """
                    )
                    
                    # Limpiar respuesta de Ollama (quitar markdown)
                    import re
                    response_text = response['response']
                    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                    
                    if json_match:
                        data = json.loads(json_match.group())
                        anunciantes = data.get('anunciantes', [])
                        
                        print(f"   📊 Anunciantes encontrados: {len(anunciantes)}")
                        
                        # Detectar nuevos
                        current_orders = set()
                        for anunciante in anunciantes:
                            order_id = f"{anunciante['nombre']}_{anunciante['precio_bs']}"
                            current_orders.add(order_id)
                            
                            if order_id not in known_orders:
                                # NUEVA ORDEN!
                                print()
                                print("   🔔 NUEVO ANUNCIANTE DETECTADO!")
                                print(f"      Nombre: {anunciante['nombre']}")
                                print(f"      Precio: Bs {anunciante['precio_bs']}")
                                print(f"      USDT: {anunciante['usdt_disponible']}")
                                print()
                                
                                # Aquí enviarías notificación Telegram
                                # telegram_notify(anunciante)
                        
                        # Actualizar conocidos
                        known_orders.update(current_orders)
                        save_known_orders(known_orders)
                        
                    else:
                        print("   ⚠️  Ollama no devolvió JSON válido")
                
                except Exception as e:
                    print(f"   ❌ Error: {e}")
                
                # Esperar antes del próximo check
                print(f"   💤 Esperando {CHECK_INTERVAL} segundos...")
                print()
                await asyncio.sleep(CHECK_INTERVAL)
        
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            print()
            print("💡 Solución:")
            print("   1. Cierra Chrome completamente")
            print("   2. Ejecuta: google-chrome --remote-debugging-port=9222")
            print("   3. Haz login en Binance")
            print("   4. Ejecuta este script de nuevo")

if __name__ == "__main__":
    asyncio.run(monitor_binance())
