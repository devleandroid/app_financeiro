#/usr/bin/env python
"""Verifica se todas as dependências estão instaladas"""
import sys

deps = [
    ('numpy', 'numpy'),
    ('pandas', 'pandas'),
    ('plotly', 'plotly'),
    ('plotly.express', 'plotly.express'),
    ('fastapi', 'fastapi'),
    ('uvicorn', 'uvicorn'),
    ('streamlit', 'streamlit'),
    ('requests', 'requests'),
    ('dotenv', 'dotenv'),
]

print("🔍 Verificando dependências:")
print("=" * 40)

all_ok = True
for dep_name, import_name in deps:
    try:
        module = __import__(import_name.split('.')[0])
        version = getattr(module, '__version__', 'desconhecida')
        print(f"✅ {dep_name:<20} {version}")
    except ImportError as e:
        print(f"❌ {dep_name:<20} Não encontrado")
        all_ok = False

print("=" * 40)
if all_ok:
    print("✅ Todas as dependências estão OK!")
    sys.exit(0)
else:
    print("❌ Faltam dependências. Verifique seu shell.nix")
    sys.exit(1)