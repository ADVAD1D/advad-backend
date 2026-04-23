from cryptography.fernet import Fernet
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent.parent

def load_key():

    key_path = BASE_DIR / "secret.key"
    return key_path.read_bytes()

def encrypt_file(file_path):
    key = load_key()
    f = Fernet(key)

    path_obj = Path(file_path)

    data_file = path_obj.read_bytes()
    encrypted_data = f.encrypt(data_file)
    
    encrypted_file_path = path_obj.with_suffix(path_obj.suffix + ".enc")
    encrypted_file_path.write_bytes(encrypted_data)

    print(f"File {path_obj.name} has been encrypted successfully as {encrypted_file_path.name}")

if __name__ == "__main__":
    env_file = PROJECT_ROOT / ".env"
    
    if env_file.exists():
        encrypt_file(env_file)
    else:
        print(f"Error: No se encontró el archivo en {env_file}")
