import pyotp
from vault import SecureVault

vault = SecureVault()
creds = vault.load_credentials()

totp = pyotp.TOTP(creds['binance']['totp_secret'])
print(f"Código TOTP Binance: {totp.now()}")
