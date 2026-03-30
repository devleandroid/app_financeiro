#!/usr/bin/env python
"""Reseta o campo 'used' das chaves para permitir reuso"""

import sqlite3

conn = sqlite3.connect("acessos.db")
cursor = conn.cursor()

# Resetar todas as chaves para não usadas
cursor.execute("UPDATE access_keys SET used = 0")
conn.commit()

# Verificar
cursor.execute("SELECT COUNT(*) FROM access_keys WHERE used = 1")
count = cursor.fetchone()[0]
print(f"✅ {count} chaves marcadas como usadas (deveria ser 0)")

cursor.execute("SELECT COUNT(*) FROM access_keys")
total = cursor.fetchone()[0]
print(f"📊 Total de chaves no banco: {total}")

conn.close()