#!/usr/bin/env python
"""Verifica e corrige a expiração das chaves no banco"""

import sqlite3
from datetime import datetime, timedelta

def check_and_fix_keys():
    conn = sqlite3.connect("acessos.db")
    cursor = conn.cursor()
    
    print("🔍 Verificando chaves no banco...")
    print("=" * 50)
    
    # Listar todas as chaves
    cursor.execute('''
        SELECT id, email, key, created_at, expires_at, used 
        FROM access_keys 
        ORDER BY created_at DESC
    ''')
    
    keys = cursor.fetchall()
    now = datetime.now()
    
    print(f"\n📊 Total de chaves: {len(keys)}")
    print("\n🔑 Chaves encontradas:")
    
    for key in keys:
        key_id, email, chave, created_str, expires_str, used = key
        created = datetime.fromisoformat(created_str)
        expires = datetime.fromisoformat(expires_str)
        
        status = "✅ ATIVA" if not used and now < expires else "❌ EXPIRADA/Usada"
        horas_restantes = (expires - now).total_seconds() / 3600 if now < expires else 0
        
        print(f"   {chave} | {email} | {status} | expira em: {horas_restantes:.1f}h | usada: {used}")
    
    print("\n" + "=" * 50)
    print("✅ Verificação concluída!")
    
    conn.close()

if __name__ == "__main__":
    check_and_fix_keys()