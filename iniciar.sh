#!/usr/bin/env bash
# Inicia a Loja Didática 2 (Linux/macOS) procurando um Python 3.9+ que funcione.
# Ignora "python" quebrado (ex.: venv ativado cuja pasta foi apagada).
cd "$(dirname "$0")" || exit 1
for py in python3 python /usr/bin/python3 /usr/local/bin/python3 /opt/homebrew/bin/python3; do
  if "$py" -c "import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)" >/dev/null 2>&1; then
    exec "$py" loja_didatica_2_v2.py "$@"
  fi
done
echo "Python 3.9+ nao encontrado. Instale com: sudo apt install python3 python3-venv (Debian/Ubuntu)"
exit 1
