# Key Locker

A lightweight encrypted password vault built in Python.  
All your credentials are stored in a single encrypted file on your Desktop — nothing goes online.

---

## Features

- AES encryption via the `cryptography` library
- Master password protects everything
- Vault saved as `key_locker_vault.dat` on your Desktop
- GUI window for everyday use
- CLI mode for terminal usage
- Copy password to clipboard
- Add, view, and delete entries

---

## Project Structure

```
key_locker/
├── key_locker/
│   ├── __init__.py
│   ├── core.py       # encryption + vault logic
│   ├── cli.py        # terminal interface
│   └── gui.py        # window interface
├── tests/
│   └── test_core.py
├── main.py
├── requirements.txt
└── README.md
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## How to Run

### GUI (default)
```bash
python main.py
```

### CLI
```bash
# add an entry
python main.py --cli add gmail --username you@gmail.com

# get an entry
python main.py --cli get gmail

# list all entries
python main.py --cli list

# delete an entry
python main.py --cli delete gmail

# change master password
python main.py --cli change-master
```

---

## Run Tests

```bash
python -m unittest discover tests/ -v
```

---

## Security Notes

- The vault file is encrypted with Fernet (AES-128-CBC + HMAC)
- The master password is never stored anywhere
- A random 16-byte salt is generated per vault
- Wrong password = decryption fails immediately

---

## Requirements

- Python 3.8+
- cryptography (`pip install cryptography`)
