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
    
    # Verificar se a coluna 'usado' existe (se for usar no lugar de status)
    if 'usado' in colunas_nomes:
        print("\n🔄 Convertendo coluna 'usado' para 'status'...")
        cursor.execute("UPDATE solicitacoes SET status = 'usada' WHERE usado = 1")
        cursor.execute("UPDATE solicitacoes SET status = 'pendente' WHERE usado = 0 OR usado IS NULL")
        print("✅ Conversão concluída")
    
    # Verificar acessos table
    cursor.execute("PRAGMA table_info(acessos)")
    colunas_acessos = cursor.fetchall()
    print("\n📊 Estrutura da tabela acessos:")
    for col in colunas_acessos:
        print(f"   - {col[1]} ({col[2]})")
    
    # Commit e fechar
    conn.commit()
    conn.close()
    
    print("\n✅ Banco de dados corrigido com sucesso!")
    
    # Mostrar estatísticas
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM solicitacoes")
    total_solicitacoes = cursor.fetchone()[0]
    print(f"\n📊 Estatísticas:")
    print(f"   Total de solicitações: {total_solicitacoes}")
    
    if total_solicitacoes > 0:
        cursor.execute("SELECT email, chave, status, data_solicitacao FROM solicitacoes LIMIT 5")
        print("\n   Últimas solicitações:")
        for row in cursor.fetchall():
            print(f"     - {row[0]} | {row[1]} | {row[2]} | {row[3]}")
    
    conn.close()

if __name__ == "__main__":
    fix_database()