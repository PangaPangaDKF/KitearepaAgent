#!/usr/bin/env python3
"""
Ejemplo de cómo usar el Vault en tu bot
NUNCA expone credenciales en logs o errores
"""

import asyncio
from vault import SecureVault

class BinanceBot:
    """Bot que usa credenciales cifradas"""
    
    def __init__(self):
        self.vault = SecureVault()
        self.credentials = None
        
    async def initialize(self):
        """Carga credenciales al iniciar"""
        print("🔐 Cargando credenciales cifradas...")
        
        # Cargar credenciales (pide password)
        self.credentials = self.vault.load_credentials()
        
        if not self.credentials:
            print("❌ No se pudieron cargar credenciales")
            print("   Ejecuta: python vault.py --init")
            return False
        
        print("✅ Credenciales cargadas")
        return True
    
    async def login_binance(self):
        """Login a Binance usando credenciales del vault"""
        if not self.credentials:
            print("❌ Credenciales no cargadas")
            return False
        
        # Obtener credenciales de Binance
        binance_creds = self.credentials['binance']
        
        # NUNCA hagas print de credenciales reales
        print(f"🔑 Iniciando sesión en Binance como: {binance_creds['email'][:3]}***")
        
        # Aquí usarías Playwright con las credenciales
        # await page.fill('input[name="email"]', binance_creds['email'])
        # await page.fill('input[name="password"]', binance_creds['password'])
        
        # Para TOTP
        import pyotp
        totp = pyotp.TOTP(binance_creds['totp_secret'])
        code = totp.now()
        
        print(f"🔢 Código TOTP generado: {code[:2]}****")
        # await page.fill('input[name="totp"]', code)
        
        return True
    
    async def login_banco(self):
        """Login al banco usando credenciales del vault"""
        banco_creds = self.credentials['banco']
        
        print(f"🏦 Conectando a: {banco_creds['url']}")
        print(f"👤 Usuario: {banco_creds['usuario'][:3]}***")
        
        # Aquí usarías Playwright
        # await page.goto(banco_creds['url'])
        # await page.fill('input[name="usuario"]', banco_creds['usuario'])
        # etc...
        
        return True
    
    async def send_telegram(self, message: str):
        """Envía notificación por Telegram"""
        telegram_creds = self.credentials['telegram']
        
        # NUNCA logees el token completo
        token_preview = telegram_creds['bot_token'][:10] + "***"
        print(f"📱 Enviando via Telegram (token: {token_preview})")
        
        # Aquí usarías python-telegram-bot
        # bot = telegram.Bot(token=telegram_creds['bot_token'])
        # await bot.send_message(chat_id=telegram_creds['chat_id'], text=message)
        
        return True
    
    def get_config(self, key: str):
        """Obtiene configuración sin exponer credenciales"""
        return self.credentials.get('config', {}).get(key)


async def main():
    """Ejemplo de uso"""
    bot = BinanceBot()
    
    # Inicializar (pide password UNA vez)
    if not await bot.initialize():
        return
    
    # Ahora puedes usar las credenciales sin volverlas a pedir
    await bot.login_binance()
    await bot.login_banco()
    await bot.send_telegram("Bot iniciado correctamente")
    
    # Obtener configuración
    country = bot.get_config('country')
    print(f"🌍 País configurado: {country}")


if __name__ == "__main__":
    asyncio.run(main())
