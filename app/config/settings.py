import os
import io
from pathlib import Path
from cryptography.fernet import Fernet
from dotenv import load_dotenv

def get_secret_key():
    render_key = os.getenv("SECRET_KEY")
    if render_key:
        return render_key.encode('utf-8')
    
    BASE_DIR = Path(__file__).resolve().parent.parent 
    key_file = BASE_DIR / "security" / "secret.key"
    if key_file.exists():
        return key_file.read_bytes()
    
    print("⚠️  No SECRET_KEY found in environment or local file.")
    return None

def load_encrypted_env():
    key = get_secret_key()
    if not key:
        # Fallback to standard dotenv if no key is present
        load_dotenv()
        return

    try:
        f = Fernet(key)
    except Exception as e:
        print(f"⚠️  Error initializing Fernet: {e}")
        load_dotenv()
        return
    
    # Render's docker env Secret File path
    render_path = Path("/etc/secrets/.env.enc")
    # Local fallback path
    local_path = Path(__file__).resolve().parent.parent.parent / ".env.enc"
    
    enc_path = render_path if render_path.exists() else local_path

    if enc_path.exists():
        try:
            encrypted_data = enc_path.read_bytes()
            decrypted_bytes = f.decrypt(encrypted_data)
            decrypted_text = decrypted_bytes.decode('utf-8')
            load_dotenv(stream=io.StringIO(decrypted_text))
            print(f"✅ Variables cargadas exitosamente desde {enc_path}")
        except Exception as e:
            print(f"⚠️  Error decrypting {enc_path}: {e}")
            load_dotenv() # Fallback
    else:
        print("⚠️  No se encontró .env.enc. Procediendo con variables de entorno estándar.")
        load_dotenv()

# Execute before Settings class initialization
load_encrypted_env()

class Settings:
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
    APP_TOKEN: str = os.getenv("APP_TOKEN")
    ADMIN_SECRET_KEY: str = os.getenv("ADMIN_SECRET_KEY")
    PORT: int = int(os.getenv("PORT", 10000))
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")

settings = Settings()
