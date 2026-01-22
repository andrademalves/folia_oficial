import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

print("=" * 80)
print("MENUS DO FINANCEIRO NO WINDOWS")
print("=" * 80)

cursor.execute("""
    SELECT me.nome, me.url, me.ativo 
    FROM usuarios_menu me 
    JOIN usuarios_modulo mu ON me.modulo_id = mu.id 
    WHERE mu.nome='Financeiro' 
    ORDER BY me.ordem
""")

rows = cursor.fetchall()
print(f'\nTotal de menus: {len(rows)}\n')
for nome, url, ativo in rows:
    status = "✓" if ativo else "✗"
    print(f'  {status} {nome:30} {url}')

conn.close()
