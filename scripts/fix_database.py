#!/usr/bin/env python
"""Script para corrigir a estrutura do banco de dados"""

import sqlite3
import os

DB_PATH = "acessos.db"

def fix_database():
    """Corrige a estrutura do banco de dados"""
    
    print("🔧 Corrigindo banco de dados...")
    
    # Fazer backup se o banco existir
    if os.path.exists(DB_PATH):
        import shutil
        backup = f"{DB_PATH}.backup"
        shutil.copy(DB_PATH, backup)
        print(f"✅ Backup criado: {backup}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Verificar estrutura atual
    cursor.execute("PRAGMA table_info(solicitacoes)")
    colunas = cursor.fetchall()
    print("\n📊 Estrutura atual da tabela solicitacoes:")
    for col in colunas:
        print(f"   - {col[1]} ({col[2]})")
    
    # Verificar se a coluna 'status' existe
    colunas_nomes = [col[1] for col in colunas]
    
    if 'status' not in colunas_nomes:
        print("\n⚠️ Coluna 'status' não encontrada. Adicionando...")
        try:
            cursor.execute("ALTER TABLE solicitacoes ADD COLUMN status TEXT DEFAULT 'pendente'")
            print("✅ Coluna 'status' adicionada")
        except sqlite3.OperationalError as e:
            print(f"❌ Erro: {e}")
    
    conn.commit()
    conn.close()
    
    print("\n✅ Banco de dados corrigido com sucesso!")

if __name__ == "__main__":
    fix_database()