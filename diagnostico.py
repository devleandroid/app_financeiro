# diagnostico.py - Versão melhorada
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import time
from datetime import datetime

# Cores para output (opcional)
class cores:
    VERDE = '\033[92m'
    AMARELO = '\033[93m'
    VERMELHO = '\033[91m'
    AZUL = '\033[94m'
    RESET = '\033[0m'

def print_ok(msg):
    print(f"{cores.VERDE}✅ {msg}{cores.RESET}")

def print_warn(msg):
    print(f"{cores.AMARELO}⚠️  {msg}{cores.RESET}")

def print_erro(msg):
    print(f"{cores.VERMELHO}❌ {msg}{cores.RESET}")

def print_info(msg):
    print(f"{cores.AZUL}ℹ️  {msg}{cores.RESET}")

print(f"\n{cores.AZUL}{'='*60}{cores.RESET}")
print(f"{cores.AZUL}🔍 DIAGNÓSTICO COMPLETO DO SISTEMA{cores.RESET}")
print(f"{cores.AZUL}{'='*60}{cores.RESET}\n")

# ============================================
# 1. INFORMAÇÕES DO AMBIENTE
# ============================================
print_info("INFORMAÇÕES DO AMBIENTE")
print(f"   Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
print(f"   Python: {sys.version.split()[0]}")
print(f"   Executável: {sys.executable}")
print(f"   Plataforma: {sys.platform}")
print(f"   Diretório atual: {os.getcwd()}")
print(f"   PID: {os.getpid()}")
print()

# ============================================
# 2. VERIFICAR MÓDULOS INSTALADOS
# ============================================
print_info("VERIFICANDO MÓDULOS")

modulos = [
    ("requests", None),
    ("numpy", "np"),
    ("pandas", "pd"),
    ("fastapi", None),
    ("uvicorn", None),
    ("streamlit", "st"),
    ("plotly", None),
    ("dotenv", None),
    ("sqlite3", None),
]

for modulo, alias in modulos:
    try:
        if alias:
            exec(f"import {modulo} as {alias}")
        else:
            exec(f"import {modulo}")
        # Pegar versão se possível
        try:
            if modulo == "requests":
                versao = requests.__version__
            elif modulo == "numpy":
                versao = np.__version__
            elif modulo == "pandas":
                versao = pd.__version__
            elif modulo == "fastapi":
                versao = fastapi.__version__
            elif modulo == "streamlit":
                versao = st.__version__
            elif modulo == "plotly":
                import plotly
                versao = plotly.__version__
            else:
                versao = "✓"
            print_ok(f"{modulo:<12} {versao}")
        except:
            print_ok(f"{modulo:<12}")
    except ImportError as e:
        print_erro(f"{modulo:<12} Não instalado")
    except Exception as e:
        print_warn(f"{modulo:<12} Erro: {str(e)[:50]}")

print()

# ============================================
# 3. VERIFICAR CONEXÃO COM BACKEND
# ============================================
print_info("TESTANDO CONEXÃO COM BACKEND")

# Tentar importar requests (se não estiver instalado, não testa)
try:
    import requests
    
    # Teste 1: Ping simples
    try:
        start = time.time()
        r = requests.get("http://localhost:8000/api/ping", timeout=2)
        if r.status_code == 200:
            print_ok(f"Backend ping OK ({time.time()-start:.2f}s)")
        else:
            print_warn(f"Backend ping retornou status {r.status_code}")
    except requests.exceptions.ConnectionError:
        print_erro("Backend não está respondendo na porta 8000")
        print_warn("   Verifique se o backend está rodando: python main.py")
    except requests.exceptions.Timeout:
        print_warn("Backend ping timeout (2s)")
    except Exception as e:
        print_erro(f"Erro no ping: {e}")
    
    # Teste 2: Health check
    try:
        start = time.time()
        r = requests.get("http://localhost:8000/api/health", timeout=2)
        if r.status_code == 200:
            dados = r.json()
            print_ok(f"Health check OK ({time.time()-start:.2f}s)")
            if 'cache_valido' in dados:
                print(f"   Cache válido: {dados.get('cache_valido')}")
        else:
            print_warn(f"Health check retornou {r.status_code}")
    except Exception as e:
        print_warn(f"Health check: {e}")
    
    # Teste 3: Endpoint de dados (rápido)
    try:
        start = time.time()
        r = requests.get(
            "http://localhost:8000/api/dados-completos?moedas=BRL,USD",
            timeout=5
        )
        if r.status_code == 200:
            dados = r.json()
            if dados.get('sucesso'):
                print_ok(f"Endpoint dados OK ({time.time()-start:.2f}s)")
                # Mostrar algumas moedas
                if 'dados_brutos' in dados:
                    cambio = dados['dados_brutos'].get('cambio', {})
                    if 'BRL' in cambio:
                        print(f"   USD/BRL: {cambio['BRL']:.2f}")
                    if 'USD' in cambio:
                        print(f"   USD/USD: {cambio['USD']}")
            else:
                print_warn(f"Endpoint retornou erro: {dados.get('mensagem', 'desconhecido')}")
        else:
            print_warn(f"Endpoint dados retornou {r.status_code}")
    except Exception as e:
        print_warn(f"Endpoint dados: {e}")
        
except ImportError:
    print_warn("Módulo 'requests' não instalado - pulando testes de rede")
    print("   Para instalar: adicione 'requests' ao shell.nix")

print()

# ============================================
# 4. VERIFICAR ARQUIVOS DO PROJETO
# ============================================
print_info("VERIFICANDO ARQUIVOS DO PROJETO")

arquivos = [
    "main.py",
    "app.py",
    "admin.py",
    "database.py",
    "email_service.py",
    "services/fixer_service.py",
    "services/bitcoin_service.py",
    "logic/recomendador.py",
    ".env",
    "acessos.db"
]

for arquivo in arquivos:
    if os.path.exists(arquivo):
        tamanho = os.path.getsize(arquivo)
        if tamanho == 0:
            print_warn(f"{arquivo:<25} (vazio)")
        else:
            print_ok(f"{arquivo:<25} ({tamanho} bytes)")
    else:
        if arquivo == ".env":
            print_warn(f"{arquivo:<25} (não encontrado - crie com suas chaves)")
        elif arquivo == "acessos.db":
            print_warn(f"{arquivo:<25} (não encontrado - será criado ao usar)")
        else:
            print_erro(f"{arquivo:<25} (não encontrado)")

print()

# ============================================
# 5. VERIFICAR BANCO DE DADOS
# ============================================
print_info("VERIFICANDO BANCO DE DADOS")

if os.path.exists("acessos.db"):
    try:
        import sqlite3
        conn = sqlite3.connect("acessos.db")
        cursor = conn.cursor()
        
        # Listar tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tabelas = cursor.fetchall()
        print_ok(f"Banco de dados encontrado com {len(tabelas)} tabelas:")
        for tabela in tabelas:
            cursor.execute(f"SELECT COUNT(*) FROM {tabela[0]}")
            count = cursor.fetchone()[0]
            print(f"   - {tabela[0]}: {count} registros")
        
        conn.close()
    except Exception as e:
        print_warn(f"Erro ao ler banco: {e}")
else:
    print_warn("Banco de dados não encontrado (será criado na primeira solicitação)")

print()

# ============================================
# 6. VERIFICAR PORTA 8000
# ============================================
print_info("VERIFICANDO PORTA 8000")

import subprocess
try:
    result = subprocess.run(
        ["ss", "-tulpn", "|", "grep", ":8000"],
        capture_output=True,
        text=True,
        shell=True
    )
    if result.stdout:
        print_ok("Porta 8000 em uso:")
        print(result.stdout.strip())
    else:
        print_warn("Nenhum processo ouvindo na porta 8000")
        print_warn("   Execute: python main.py")
except Exception as e:
    print_warn(f"Não foi possível verificar porta: {e}")

print()

# ============================================
# 7. VERIFICAR ARQUIVO .ENV
# ============================================
print_info("VERIFICANDO CONFIGURAÇÕES")

if os.path.exists(".env"):
    with open(".env", "r") as f:
        linhas = f.readlines()
        chaves = []
        for linha in linhas:
            if '=' in linha and not linha.startswith('#'):
                chave = linha.split('=')[0].strip()
                chaves.append(chave)
        print_ok(f"Arquivo .env encontrado com {len(chaves)} variáveis:")
        for chave in chaves:
            print(f"   - {chave}")
else:
    print_warn("Arquivo .env não encontrado")
    print_warn("   Crie com: ADMIN_USER, ADMIN_PASS, EMAIL_*, FIXER_API_KEY")

print(f"\n{cores.AZUL}{'='*60}{cores.RESET}")
print(f"{cores.AZUL}✅ DIAGNÓSTICO CONCLUÍDO{cores.RESET}")
print(f"{cores.AZUL}{'='*60}{cores.RESET}\n")