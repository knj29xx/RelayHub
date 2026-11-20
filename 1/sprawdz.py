#!/usr/bin/env python3
"""Local dependency check. Does not connect to Instagram or inspect credentials."""
import sys, platform, importlib
from importlib import metadata
print('Python:', sys.version.split()[0], '| Platforma:', platform.system(), platform.machine())
if sys.version_info < (3,11):
    print('BRAK: Python >= 3.11 jest potrzebny dla nowego instagrapi. Nie mieszaj repozytoriow Alpine.')
    raise SystemExit(2)
missing=[]
for mod,dist in [('instagrapi','instagrapi'),('curl_cffi','curl_cffi'),('pydantic','pydantic'),('PIL','Pillow'),('Cryptodome','pycryptodomex'),('requests','requests'),('socks','PySocks')]:
    try:
        importlib.import_module(mod)
        try: v=metadata.version(dist)
        except metadata.PackageNotFoundError: v='(pakiet systemowy)'
        print('OK', mod, v)
    except Exception as exc:
        missing.append(mod)
        print('BRAK', mod, type(exc).__name__)
if missing:
    print('BRAK BIBLIOTEK:', ', '.join(missing))
    print('Jesli brakuje curl_cffi na iSH x86, nie instaluj edge/testing do starego Alpine.')
    print('Ten iPhone nie ma obecnie zgodnego srodowiska do logowania. Nie wpisuj hasla.')
    raise SystemExit(2)
try:
    from instagrapi import Client
    cl=Client()
except Exception as exc:
    print('Klient nie uruchamia sie:', type(exc).__name__)
    raise SystemExit(2)
print('KLUCZOWE MODULY DZIALAJA. Mozesz uruchomic login_iphone.py.')
print('To NIE potwierdza, ze Instagram zaakceptuje logowanie i 2FA.')
