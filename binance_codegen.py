#!/usr/bin/env python3
"""
Playwright CodeGen Configurado para Binance C2C
Con zoom 75% y viewport correcto
"""

import asyncio
from playwright.async_api import async_playwright

async def open_binance_codegen():
    """Abre Binance C2C con Playwright Inspector configurado correctamente"""
    
    async with async_playwright() as p:
        print("=" * 60)
        print("PLAYWRIGHT INSPECTOR - BINANCE C2C")
        print("=" * 60)
        print()
        print("✅ Configuración:")
        print("   - URL: https://c2c.binance.com/es-LA/myads")
        print("   - Zoom: 75%")
        print("   - Viewport: 1920x1080")
        print("   - User Agent: Chrome Linux")
        print()
        print("📋 INSTRUCCIONES:")
        print("   1. Se abrirá el navegador con Playwright Inspector")
        print("   2. Haz login en Binance manualmente")
        print("   3. Navega normal (clicks, scroll, etc)")
        print("   4. Playwright Inspector GRABA TODO")
        print("   5. Copia el código Python generado")
        print()
        
        # Configuración correcta
        browser = await p.chromium.launch(
            headless=False,
            args=[
                '--start-maximized',
                '--disable-blink-features=AutomationControlled'
            ]
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            locale='es-VE',
            timezone_id='America/Caracas',
            user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            extra_http_headers={
                'Accept-Language': 'es-VE,es;q=0.9,en;q=0.8'
            }
        )
        
        page = await context.new_page()
        
        # Configurar zoom al 75%
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            document.body.style.zoom = '0.75';
        """)
        
        # Ir a la URL correcta
        print("🌐 Abriendo Binance C2C...")
        await page.goto('https://c2c.binance.com/es-LA/myads?type=normal&code=default')
        
        # Aplicar zoom después de cargar
        await page.wait_for_load_state('networkidle')
        await page.evaluate('document.body.style.zoom = "0.75"')
        
        print("✅ Página cargada con zoom 75%")
        print()
        print("👉 Ahora:")
        print("   1. Haz login manualmente")
        print("   2. Ve a 'Mis anuncios' si no estás ahí")
        print("   3. Click en 'Órdenes' (arriba)")
        print("   4. Observa el Inspector grabando tus acciones")
        print()
        
        # Mantener abierto hasta que el usuario cierre manualmente
        try:
            await page.wait_for_timeout(3600000)  # 1 hora
        except:
            pass
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(open_binance_codegen())
