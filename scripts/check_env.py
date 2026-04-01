#!/usr/bin/env python
"""Verifica se o ambiente está configurado corretamente"""

import sys
import os
import importlib

print("🔍 Verificando ambiente...\n")

# Verificar Python
print(f"🐍 Python: {sys.version}")

# Verificar módulos
modules = ['fastapi', 'uvicorn', 'streamlit', 'pandas', 'numpy', 'plotly', 'requests']
print("\n📦 Módulos:")
for mod in modules:
    try:
        version = importlib.import_module(mod).__version__
        print(f"   ✅ {mod}: {version}")
    except ImportError:
        print(f"   ❌ {mod}: não encontrado")

# Verificar variáveis de ambiente
print("\n🔧 Variáveis de ambiente:")
env_vars = ['API_URL', 'ADMIN_USER', 'FIXER_API_KEY']
for var in env_vars:
    value = os.getenv(var)
    if value:
        print(f"   ✅ {var}: {value[:20]}..." if len(value) > 20 else f"   ✅ {var}: {value}")
    else:
        print(f"   ⚠️ {var}: não configurado")

print("\n✅ Verificação concluída!")