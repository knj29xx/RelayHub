#!/usr/bin/env python3
"""One-time Instagram login for RelayHub PS5 v15.

This script never sends credentials to RelayHub or any other service. It
uses the installed instagrapi client to speak to Instagram. Only after the
client confirms its own login does it export a MOBILE SESSION for importing
through the PS5 WebGUI. The JSON contains session credentials: keep private.
"""
import base64
import getpass
import json
import os
from pathlib import Path
import sys


def private_json_write(path: Path, value):
    flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
    fd = os.open(path, flags, 0o600)
    os.fchmod(fd, 0o600)
    with os.fdopen(fd, 'w', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, separators=(',', ':'))


def main():
    try:
        from instagrapi import Client
        from instagrapi.exceptions import TwoFactorRequired, ChallengeRequired
    except ImportError:
        raise SystemExit('Najpierw zainstaluj wymagania: python -m pip install -r requirements.txt')

    username = input('Login Instagram: ').strip()
    if not username or not all(c.isalnum() or c in '._' for c in username):
        raise SystemExit('Niepoprawna nazwa konta.')
    password = getpass.getpass('Haslo (niewidoczne): ')
    if not password:
        raise SystemExit('Haslo jest wymagane.')
    client = Client()
    # Keep the same device profile on subsequent attempts.
    profile_path = Path.home() / '.relayhub_instagram_device.json'
    if profile_path.is_file():
        try:
            client.set_settings(json.loads(profile_path.read_text()))
        except (ValueError, OSError) as exc:
            raise SystemExit(f'Nie mozna wczytac profilu urzadzenia: {exc}')
    def code_handler(username, choice):
        # Instagrapi will choose the channel supported by Instagram.
        # WhatsApp cannot be forced if unavailable to the account.
        print('Instagram wymaga kodu 2FA; sprawdz WhatsApp/SMS/aplikacje.')
        return input('Kod otrzymany od Instagrama: ').strip()
    client.challenge_code_handler = code_handler
    try:
        client.login(username, password)
    except TwoFactorRequired:
        print('Instagram wymaga kodu 2FA. Wybierz metode dostepna w Instagramie.')
        code = input('Kod z WhatsApp/SMS/aplikacji: ').strip()
        if not code.isdigit() or len(code) not in (6, 8, 10):
            raise SystemExit('Kod ma nieobslugiwany format.')
        client.login(username, password, verification_code=code)
    except ChallengeRequired as exc:
        raise SystemExit('Instagram wymaga potwierdzenia w oficjalnej aplikacji. Zrob to tam; potem ponow proces.') from exc
    finally:
        password = None

    try:
        settings = client.get_settings()
        private_json_write(profile_path, settings)
        cookies = settings.get('cookies', {})
        authorization = (
            client.private.headers.get('Authorization', '')
            or settings.get('authorization', '')
        )
        if not authorization and settings.get('authorization_data'):
            # Instagram's standard private mobile token encodes authorization_data.
            blob = json.dumps(settings['authorization_data'], separators=(',', ':')).encode()
            authorization = 'IGT:2:' + base64.urlsafe_b64encode(blob).decode().rstrip('=')
        if authorization.startswith('Bearer '):
            authorization = authorization[7:]
        if not authorization:
            raise RuntimeError('Klient nie zwrocil tokenu autoryzacji do mobilnego API.')
        data = {
            'username': username,
            'sessionid': str(cookies.get('sessionid') or client.sessionid or settings.get('authorization_data', {}).get('sessionid', '') or ''),
            'csrftoken': cookies.get('csrftoken') or client.token,
            'ds_user_id': str(client.user_id or ''),
            'authorization': authorization,
            'user_agent': settings.get('user_agent') or client.user_agent,
            'android_device_id': str(settings.get('uuids', {}).get('android_device_id', '')),
            'device_id': str(settings.get('uuids', {}).get('uuid', '')),
        }
        if any(not isinstance(value, str) or (not value and key not in ('sessionid', 'csrftoken', 'android_device_id', 'device_id')) for key, value in data.items()):
            raise RuntimeError('W sesji brakuje wymaganych danych. Nie utworzono eksportu.')
        destination = Path.home() / 'relayhub-mobile-session.json'
        private_json_write(destination, data)
        print('Sesja przygotowana lokalnie. Importuj plik do WebGUI:', destination)
        print('Po imporcie usun plik i nie udostepniaj go innym. Import moze zostac odrzucony przez IG.')
    except Exception as exc:
        raise SystemExit(f'Nie udalo sie wyeksportowac mobilnej sesji: {type(exc).__name__}: {exc}')


if __name__ == '__main__':
    main()
