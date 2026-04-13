from vault import SecureVault

vault = SecureVault()
creds = vault.load_credentials()

if creds:
    print("✅ Vault cargado correctamente")
    print(f"Email Binance: {creds['binance']['email']}")
    print(f"Email Gmail: {creds['gmail']['email']}")
    print(f"Usuario Banco: {creds['banco']['usuario']}")
    print(f"Bot Token (primeros 10): {creds['telegram']['bot_token'][:10]}...")
    print(f"Chat ID: {creds['telegram']['chat_id']}")
    
    # Probar TOTP
    import pyotp
    totp = pyotp.TOTP(creds['binance']['totp_secret'])
    print(f"Código TOTP actual: {totp.now()}")
else:
    print("❌ Error al cargar vault")
