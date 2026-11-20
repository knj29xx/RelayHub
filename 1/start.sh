#!/bin/sh
set -eu
cd "$(dirname "$0")"
[ -x .venv/bin/python ] || { echo 'Najpierw: sh setup_ish.sh'; exit 2; }
.venv/bin/python sprawdz.py || exit 3
exec .venv/bin/python login_iphone.py
