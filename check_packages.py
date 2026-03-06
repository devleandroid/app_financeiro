# check_packages.py
packages = [
    ('streamlit', 'st'),
    ('requests', None),
    ('pandas', 'pd'),
    ('plotly.express', 'px'),
    ('plotly.graph_objects', 'go'),
    ('fastapi', None),
    ('uvicorn', None),
]

print("🔍 Verificando pacotes instalados:\n")

for package, alias in packages:
    try:
        if alias:
            exec(f"import {package} as {alias}")
            print(f"✅ {package:<20} -> OK (importado como {alias})")
        else:
            exec(f"import {package}")
            print(f"✅ {package:<20} -> OK")
    except ImportError as e:
        print(f"❌ {package:<20} -> FALTA: {e}")

print("\n📦 Lista completa de pacotes instalados:")
!pip list