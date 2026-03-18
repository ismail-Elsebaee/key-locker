import os
import json
import base64
import hashlib
from pathlib import Path
from cryptography.fernet import Fernet, InvalidToken


VAULT_FILENAME = "key_locker_vault.dat"


def get_vault_path():
    desktop = Path.home() / "Desktop"
    desktop.mkdir(exist_ok=True)
    return desktop / VAULT_FILENAME


def derive_key(master_password: str, salt: bytes) -> bytes:
    # stretch the master password into a 32-byte key using SHA-256 + salt
    raw = master_password.encode() + salt
    digest = hashlib.sha256(raw).digest()
    return base64.urlsafe_b64encode(digest)


def load_vault(master_password: str) -> dict:
    path = get_vault_path()

    if not path.exists():
        return {}

    with open(path, "rb") as f:
        data = f.read()

    # first 16 bytes are the salt
    salt = data[:16]
    encrypted = data[16:]

    key = derive_key(master_password, salt)
    fernet = Fernet(key)

    try:
        decrypted = fernet.decrypt(encrypted)
    except InvalidToken:
        raise ValueError("Wrong master password.")

    return json.loads(decrypted.decode())


def save_vault(master_password: str, vault: dict):
    path = get_vault_path()

    # reuse existing salt or create a new one
    if path.exists():
        with open(path, "rb") as f:
            salt = f.read(16)
    else:
        salt = os.urandom(16)

    key = derive_key(master_password, salt)
    fernet = Fernet(key)

    encrypted = fernet.encrypt(json.dumps(vault).encode())

    with open(path, "wb") as f:
        f.write(salt + encrypted)


def vault_exists() -> bool:
    return get_vault_path().exists()


def add_entry(master_password: str, name: str, username: str, password: str, note: str = ""):
    name = name.strip().lower()
    if not name:
        raise ValueError("Entry name cannot be empty.")

    vault = load_vault(master_password)

    vault[name] = {
        "username": username,
        "password": password,
        "note": note,
    }

    save_vault(master_password, vault)


def get_entry(master_password: str, name: str) -> dict:
    name = name.strip().lower()
    vault = load_vault(master_password)

    if name not in vault:
        raise KeyError(f"No entry found for '{name}'.")

    return vault[name]


def delete_entry(master_password: str, name: str):
    name = name.strip().lower()
    vault = load_vault(master_password)

    if name not in vault:
        raise KeyError(f"No entry found for '{name}'.")

    del vault[name]
    save_vault(master_password, vault)


def list_entries(master_password: str) -> list:
    vault = load_vault(master_password)
    return sorted(vault.keys())


def change_master_password(old_password: str, new_password: str):
    vault = load_vault(old_password)

    # delete old vault and rewrite with new password + new salt
    path = get_vault_path()
    if path.exists():
        path.unlink()

    save_vault(new_password, vault)
