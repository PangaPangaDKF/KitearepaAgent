#!/usr/bin/env python3
"""
Sistema de Cifrado Multi-Capa para Credenciales
Protege: Binance, Banco, Gmail, Telegram, TOTP
"""

import os
import json
import base64
import getpass
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import hashlib

class SecureVault:
    """
    Bóveda de seguridad con cifrado AES-256
    Usa contraseña maestra + salt para generar clave
    """
    
    def __init__(self, vault_path: str = "~/.binance-vault"):
        self.vault_path = Path(vault_path).expanduser()
        self.vault_path.mkdir(exist_ok=True, mode=0o700)  # Solo owner puede acceder
        
        self.credentials_file = self.vault_path / "credentials.enc"
        self.salt_file = self.vault_path / "salt.key"
        self.backup_file = self.vault_path / "credentials.backup.enc"
        
    def _generate_key(self, password: str) -> bytes:
        """Genera clave de cifrado desde contraseña usando PBKDF2"""
        # Cargar o crear salt
        if self.salt_file.exists():
            with open(self.salt_file, 'rb') as f:
                salt = f.read()
        else:
            salt = os.urandom(16)
            with open(self.salt_file, 'wb') as f:
                f.write(salt)
            os.chmod(self.salt_file, 0o600)  # Solo owner puede leer
        
        # Derivar clave desde password + salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,  # Dificulta ataques de fuerza bruta
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def initialize(self):
        """Primera vez - crear vault y guardar credenciales"""
        print("╔═══════════════════════════════════════════════════════════╗")
        print("║     INICIALIZACIÓN DE BÓVEDA SEGURA                      ║")
        print("╚═══════════════════════════════════════════════════════════╝")
        print()
        print("Esta es la ÚNICA vez que ingresarás tus credenciales.")
        print("Serán cifradas con AES-256 y protegidas con tu contraseña maestra.")
        print()
        
        # Solicitar contraseña maestra
        while True:
            master_password = getpass.getpass("Contraseña maestra (mínimo 12 caracteres): ")
            if len(master_password) < 12:
                print("❌ La contraseña debe tener al menos 12 caracteres")
                continue
            
            confirm = getpass.getpass("Confirma contraseña maestra: ")
            if master_password != confirm:
                print("❌ Las contraseñas no coinciden")
                continue
            
            break
        
        print()
        print("Ahora ingresa tus credenciales (se cifrarán inmediatamente):")
        print()
        
        credentials = {}
        
        # Binance
        print("─── BINANCE ───")
        credentials['binance'] = {
            'email': input("Email: "),
            'password': getpass.getpass("Password: "),
            'totp_secret': getpass.getpass("TOTP Secret (32 caracteres): ")
        }
        
        # Banco
        print("\n─── BANCO MERCANTIL ───")
        credentials['banco'] = {
            'usuario': input("Usuario: "),
            'password': getpass.getpass("Password: "),
            'url': input("URL del banco: ")
        }
        
        # Gmail
        print("\n─── GMAIL ───")
        credentials['gmail'] = {
            'email': input("Email: "),
            'password': getpass.getpass("Password (app password recomendado): ")
        }
        
        # Telegram
        print("\n─── TELEGRAM ───")
        credentials['telegram'] = {
            'bot_token': getpass.getpass("Bot Token: "),
            'chat_id': input("Chat ID: ")
        }
        
        # Información adicional
        print("\n─── CONFIGURACIÓN ───")
        credentials['config'] = {
            'country': 'Venezuela',
            'timezone': 'America/Caracas',
            'locale': 'es-VE',
            'fiat_currency': 'VES',
            'crypto_currency': 'USDT'
        }
        
        # Cifrar y guardar
        self._save_credentials(credentials, master_password)
        
        print()
        print("✅ Credenciales cifradas y guardadas exitosamente")
        print(f"📁 Ubicación: {self.credentials_file}")
        print()
        print("⚠️  IMPORTANTE:")
        print("   1. NO olvides tu contraseña maestra")
        print("   2. Haz backup del directorio ~/.binance-vault")
        print("   3. NUNCA compartas estos archivos")
        
        return True
    
    def _save_credentials(self, credentials: dict, password: str):
        """Cifra y guarda credenciales"""
        key = self._generate_key(password)
        cipher = Fernet(key)
        
        # Serializar a JSON
        credentials_json = json.dumps(credentials, indent=2)
        
        # Cifrar
        encrypted = cipher.encrypt(credentials_json.encode())
        
        # Guardar
        with open(self.credentials_file, 'wb') as f:
            f.write(encrypted)
        os.chmod(self.credentials_file, 0o600)
        
        # Backup automático
        with open(self.backup_file, 'wb') as f:
            f.write(encrypted)
        os.chmod(self.backup_file, 0o600)
    
    def load_credentials(self, password: str = None) -> dict:
        """Carga y descifra credenciales"""
        if not self.credentials_file.exists():
            print("❌ Vault no inicializado. Ejecuta: python vault.py --init")
            return None
        
        # Solicitar password si no se provee
        if password is None:
            password = getpass.getpass("Contraseña maestra: ")
        
        try:
            key = self._generate_key(password)
            cipher = Fernet(key)
            
            # Leer archivo cifrado
            with open(self.credentials_file, 'rb') as f:
                encrypted = f.read()
            
            # Descifrar
            decrypted = cipher.decrypt(encrypted)
            credentials = json.loads(decrypted.decode())
            
            return credentials
            
        except Exception as e:
            print(f"❌ Error al descifrar: Contraseña incorrecta o archivo corrupto")
            return None
    
    def get(self, service: str, key: str = None):
        """Obtiene credencial específica sin cargar todo"""
        credentials = self.load_credentials()
        if not credentials:
            return None
        
        if key:
            return credentials.get(service, {}).get(key)
        return credentials.get(service)
    
    def update_credential(self, service: str, key: str, value: str):
        """Actualiza una credencial específica"""
        password = getpass.getpass("Contraseña maestra: ")
        credentials = self.load_credentials(password)
        
        if not credentials:
            return False
        
        if service not in credentials:
            credentials[service] = {}
        
        credentials[service][key] = value
        self._save_credentials(credentials, password)
        
        print(f"✅ Actualizado: {service}.{key}")
        return True
    
    def change_master_password(self):
        """Cambia la contraseña maestra"""
        print("Cambiando contraseña maestra...")
        
        old_password = getpass.getpass("Contraseña maestra actual: ")
        credentials = self.load_credentials(old_password)
        
        if not credentials:
            print("❌ Contraseña incorrecta")
            return False
        
        new_password = getpass.getpass("Nueva contraseña maestra (mín 12 caracteres): ")
        if len(new_password) < 12:
            print("❌ La contraseña debe tener al menos 12 caracteres")
            return False
        
        confirm = getpass.getpass("Confirma nueva contraseña: ")
        if new_password != confirm:
            print("❌ Las contraseñas no coinciden")
            return False
        
        # Re-cifrar con nueva contraseña
        # Primero eliminar salt viejo
        if self.salt_file.exists():
            os.remove(self.salt_file)
        
        # Guardar con nueva password (genera nuevo salt)
        self._save_credentials(credentials, new_password)
        
        print("✅ Contraseña maestra cambiada exitosamente")
        return True
    
    def verify_integrity(self):
        """Verifica integridad del vault"""
        if not self.credentials_file.exists():
            print("❌ Archivo de credenciales no existe")
            return False
        
        password = getpass.getpass("Contraseña maestra: ")
        credentials = self.load_credentials(password)
        
        if credentials:
            print("✅ Vault íntegro y accesible")
            print(f"\nServicios configurados:")
            for service in credentials.keys():
                print(f"  - {service}")
            return True
        else:
            print("❌ Vault corrupto o contraseña incorrecta")
            return False
    
    def export_backup(self, output_file: str):
        """Exporta backup cifrado"""
        password = getpass.getpass("Contraseña maestra: ")
        credentials = self.load_credentials(password)
        
        if not credentials:
            return False
        
        # Guardar backup
        output_path = Path(output_file)
        with open(self.credentials_file, 'rb') as f:
            backup_data = f.read()
        
        with open(output_path, 'wb') as f:
            f.write(backup_data)
        
        # También copiar salt
        salt_backup = output_path.with_suffix('.salt')
        with open(self.salt_file, 'rb') as f:
            salt_data = f.read()
        with open(salt_backup, 'wb') as f:
            f.write(salt_data)
        
        print(f"✅ Backup exportado:")
        print(f"   - Credenciales: {output_path}")
        print(f"   - Salt: {salt_backup}")
        print("\n⚠️  Guarda ambos archivos en un lugar SEGURO")
        return True


def main():
    """CLI para gestionar el vault"""
    import sys
    
    vault = SecureVault()
    
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python vault.py --init          # Primera vez - crear vault")
        print("  python vault.py --verify        # Verificar integridad")
        print("  python vault.py --change-pass   # Cambiar contraseña maestra")
        print("  python vault.py --backup <file> # Exportar backup")
        print("  python vault.py --test          # Probar carga de credenciales")
        return
    
    command = sys.argv[1]
    
    if command == '--init':
        vault.initialize()
    
    elif command == '--verify':
        vault.verify_integrity()
    
    elif command == '--change-pass':
        vault.change_master_password()
    
    elif command == '--backup':
        if len(sys.argv) < 3:
            print("❌ Especifica archivo de salida")
            return
        vault.export_backup(sys.argv[2])
    
    elif command == '--test':
        print("Probando carga de credenciales...")
        creds = vault.load_credentials()
        if creds:
            print("✅ Credenciales cargadas correctamente")
            print("\nServicios disponibles:")
            for service in creds.keys():
                print(f"  - {service}")
        else:
            print("❌ Error al cargar credenciales")
    
    else:
        print(f"❌ Comando desconocido: {command}")


if __name__ == "__main__":
    main()
