#!/usr/bin/env python3
"""
Script de Auto-Discovery de Selectores CSS
Encuentra elementos en Binance P2P automáticamente
"""

import asyncio
from playwright.async_api import async_playwright
import json

async def discover_binance_selectors():
    """Descubre selectores de Binance P2P automáticamente"""
    
    async with async_playwright() as p:
        # Abrir navegador visible con configuración correcta
        browser = await p.chromium.launch(
            headless=False,
            args=['--start-maximized']
        )
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            locale='es-VE',
            user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        )
        page = await context.new_page()
        
        # Configurar zoom al 75%
        await page.evaluate('document.body.style.zoom = "0.75"')
        
        print("=" * 60)
        print("DESCUBRIDOR DE SELECTORES - BINANCE P2P")
        print("=" * 60)
        print()
        print("INSTRUCCIONES:")
        print("1. Haz login manualmente en Binance")
        print("2. Ve a P2P → Mis anuncios")
        print("3. Abre una orden (si tienes)")
        print("4. Presiona Enter en la terminal cuando estés listo")
        print()
        
        # Ir a Binance C2C - Mis anuncios (URL CORRECTA)
        await page.goto('https://c2c.binance.com/es-LA/myads?type=normal&code=default')
        
        # Esperar a que el usuario haga login
        input("Presiona Enter después de hacer login y estar en 'Mis anuncios'...")
        
        selectors = {}
        
        # === DESCUBRIR SELECTORES COMUNES ===
        
        print("\n🔍 Buscando elementos en la página...")
        
        # 1. Buscar botón de órdenes
        ordenes_candidates = [
            'text=Órdenes',
            'text=Orders',
            '[data-bn-type="link"]:has-text("Orden")',
            'a:has-text("Orden")',
        ]
        
        for selector in ordenes_candidates:
            try:
                element = await page.query_selector(selector)
                if element:
                    selectors['boton_ordenes'] = selector
                    print(f"✅ Botón Órdenes: {selector}")
                    break
            except:
                pass
        
        # 2. Buscar cards de órdenes
        order_cards_candidates = [
            '[class*="order"]',
            '[data-testid*="order"]',
            '[class*="Order"]',
            'div[class*="card"]',
        ]
        
        for selector in order_cards_candidates:
            try:
                elements = await page.query_selector_all(selector)
                if elements and len(elements) > 0:
                    selectors['orden_cards'] = selector
                    print(f"✅ Cards de orden: {selector} (encontrados: {len(elements)})")
                    break
            except:
                pass
        
        # 3. Buscar ID de orden
        order_id_candidates = [
            'text=/[0-9]{15,}/',  # Número largo
            '[class*="order-id"]',
            '[class*="orderId"]',
        ]
        
        for selector in order_id_candidates:
            try:
                element = await page.query_selector(selector)
                if element:
                    text = await element.text_content()
                    if text and len(text) > 10:
                        selectors['orden_id'] = selector
                        print(f"✅ ID Orden: {selector}")
                        break
            except:
                pass
        
        # 4. Buscar montos
        amount_candidates = [
            'text=/[0-9,]+\\s*USDT/',
            'text=/[0-9,]+\\s*Bs/',
            '[class*="amount"]',
            '[class*="Amount"]',
        ]
        
        for selector in amount_candidates:
            try:
                element = await page.query_selector(selector)
                if element:
                    selectors['monto'] = selector
                    print(f"✅ Monto: {selector}")
                    break
            except:
                pass
        
        # 5. Buscar estado
        status_candidates = [
            'text=/Esperando|Pending|Pagado|Paid/',
            '[class*="status"]',
            '[class*="Status"]',
        ]
        
        for selector in status_candidates:
            try:
                element = await page.query_selector(selector)
                if element:
                    selectors['estado'] = selector
                    print(f"✅ Estado: {selector}")
                    break
            except:
                pass
        
        # 6. Buscar botón "Pago recibido"
        pago_recibido_candidates = [
            'text=Pago recibido',
            'text=Released',
            'button:has-text("recibido")',
            '[class*="release"]',
        ]
        
        for selector in pago_recibido_candidates:
            try:
                element = await page.query_selector(selector)
                if element:
                    selectors['boton_pago_recibido'] = selector
                    print(f"✅ Botón Pago Recibido: {selector}")
                    break
            except:
                pass
        
        # === EXTRAER TODO EL HTML ===
        print("\n📄 Extrayendo HTML completo...")
        html_content = await page.content()
        
        # Guardar HTML
        with open('binance_p2p_page.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        print("✅ HTML guardado en: binance_p2p_page.html")
        
        # === GUARDAR SELECTORES ===
        with open('selectores_descubiertos.json', 'w', encoding='utf-8') as f:
            json.dump(selectors, f, indent=2, ensure_ascii=False)
        
        print("\n📝 Selectores guardados en: selectores_descubiertos.json")
        print("\n" + "=" * 60)
        print("SELECTORES DESCUBIERTOS:")
        print("=" * 60)
        for key, value in selectors.items():
            print(f"{key}: {value}")
        
        # === ANÁLISIS CON OLLAMA ===
        print("\n🤖 Analizando con Ollama...")
        
        import ollama
        
        # Extraer fragmento relevante del HTML
        html_snippet = html_content[:50000]  # Primeros 50k caracteres
        
        try:
            response = ollama.generate(
                model='llama3.2:3b',
                prompt=f"""
                Analiza este HTML de Binance P2P.
                Identifica selectores CSS para:
                1. Lista de órdenes
                2. ID de orden
                3. Monto en USDT
                4. Monto en VES/Bs
                5. Nombre del comprador
                6. Estado de la orden
                7. Botón "Pago recibido"
                
                HTML (fragmento):
                {html_snippet}
                
                Responde en JSON:
                {{
                    "orden_lista": "selector",
                    "orden_id": "selector",
                    "monto_usdt": "selector",
                    "monto_ves": "selector",
                    "comprador": "selector",
                    "estado": "selector",
                    "boton_liberar": "selector"
                }}
                """
            )
            
            print("\n📊 Respuesta de Ollama:")
            print(response['response'])
            
            # Guardar respuesta
            with open('ollama_analysis.txt', 'w', encoding='utf-8') as f:
                f.write(response['response'])
            
        except Exception as e:
            print(f"⚠️ Error con Ollama: {e}")
        
        print("\n✅ PROCESO COMPLETADO")
        print("\nArchivos generados:")
        print("  - selectores_descubiertos.json")
        print("  - binance_p2p_page.html")
        print("  - ollama_analysis.txt")
        
        input("\nPresiona Enter para cerrar el navegador...")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(discover_binance_selectors())
