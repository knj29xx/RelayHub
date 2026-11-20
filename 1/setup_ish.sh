#!/bin/sh
# RelayHub iPhone: attempt local installation, no mixing Alpine repositories.
set -eu
cd "$(dirname "$0")"
printf '\n=== RelayHub iSH: sprawdzanie systemu ===\n'
if ! command -v apk >/dev/null 2>&1; then
  echo 'To nie jest Alpine/iSH. Uzyj instrukcji dla innego systemu.'; exit 2
fi
printf 'Alpine: '; cat /etc/alpine-release || true
printf 'Architektura: '; uname -m
# Do not reconfigure iSH repositories or install from edge/testing.
echo 'Instaluję biblioteki dostępne w TWOJEJ wersji Alpine...'
apk update
if ! apk add python3 py3-pip py3-virtualenv ca-certificates py3-requests py3-pysocks py3-pydantic py3-pillow py3-pycryptodomex py3-cffi; then
  echo 'Biblioteka niedostępna w repozytoriach iSH. Nie zmieniaj /etc/apk/repositories na edge.'
  exit 3
fi
if ! python3 -c 'import sys; assert sys.version_info >= (3,11)' 2>/dev/null; then
  echo 'Python w iSH jest zbyt stary (<3.11). Nie da się bezpiecznie zainstalować współczesnego instagrapi.'
  exit 3
fi
if [ ! -d .venv ]; then
  if command -v virtualenv >/dev/null 2>&1; then virtualenv --system-site-packages .venv
  else python3 -m venv --system-site-packages .venv
  fi
fi
# Try to install curl_cffi only from matching Alpine repos or a binary wheel.
if ! .venv/bin/python -c 'import curl_cffi' >/dev/null 2>&1; then
  if apk search -x py3-curl-cffi 2>/dev/null | grep -q 'py3-curl-cffi'; then
    apk add py3-curl-cffi
  else
    echo 'curl_cffi nie jest w repozytoriach tego Alpine; próbuję gotowej paczki pip.'
    .venv/bin/python -m pip install --only-binary=:all: 'curl_cffi>=0.15,<1' || true
  fi
fi
# Choose a release compatible with Alpine-provided Pillow 12 if present.
PIL_MAJOR=$(.venv/bin/python -c 'from PIL import __version__; print(__version__.split(".")[0])' 2>/dev/null || echo 0)
case "$PIL_MAJOR" in
  13|14) IG_VERSION=3.2.19 ;;
  12) IG_VERSION=3.1.0 ;;
  *) echo 'Pillow w tym Alpine jest za stary. Nie zalecam niesprawdzonych upgrade w iSH.'; exit 3 ;;
esac
.venv/bin/python -m pip install --only-binary=:all: --no-deps "instagrapi==$IG_VERSION"
echo '=== DIAGNOSTYKA ==='
.venv/bin/python sprawdz.py || {
  echo 'iSH nie spelnia wymagan; nie próbuj jeszcze logowania. Zobacz README.'
  exit 4
}
echo 'Instalacja zależności zakończona. Teraz: sh start.sh'
