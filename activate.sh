##!/bin/bash
# Ativar ambiente Nix
nix-shell --run "bash -c '
  # Criar venv se não existir
  if [ ! -d ".venv" ]; then
    python -m venv .venv --system-site-packages
  fi
  # Ativar venv
  source .venv/bin/activate
  # Instalar pacotes se necessário
  pip install plotly 2>/dev/null || true
  # Iniciar shell
  exec $SHELL
'"
