import os
import django
import MySQLdb

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestaoTi.settings')
django.setup()

from django.conf import settings

# Conecta ao MySQL
db_settings = settings.DATABASES['default']
conn = MySQLdb.connect(
    host=db_settings['HOST'],
    user=db_settings['USER'],
    passwd=db_settings['PASSWORD'],
    db=db_settings['NAME']
)

cursor = conn.cursor()

print("=== Verificando estrutura da tabela boletos_boleto ===\n")

# Verifica estrutura atual
cursor.execute("DESCRIBE boletos_boleto")
columns = cursor.fetchall()

print("Campos relevantes:")
for col in columns:
    if 'codigo_barras' in col[0] or 'linha_digitavel' in col[0]:
        print(f"  {col[0]}: {col[1]}")

print("\n=== Corrigindo tamanhos ===\n")

# Altera o tamanho das colunas
try:
    print("Alterando codigo_barras para VARCHAR(44)...")
    cursor.execute("ALTER TABLE boletos_boleto MODIFY COLUMN codigo_barras VARCHAR(44)")
    print("✓ codigo_barras alterado com sucesso!")
    
    print("Alterando linha_digitavel para VARCHAR(54)...")
    cursor.execute("ALTER TABLE boletos_boleto MODIFY COLUMN linha_digitavel VARCHAR(54)")
    print("✓ linha_digitavel alterado com sucesso!")
    
    conn.commit()
    print("\n✓ Correções aplicadas com sucesso!")
    
except Exception as e:
    print(f"✗ Erro: {e}")
    conn.rollback()

# Verifica novamente
print("\n=== Estrutura após correção ===\n")
cursor.execute("DESCRIBE boletos_boleto")
columns = cursor.fetchall()

for col in columns:
    if 'codigo_barras' in col[0] or 'linha_digitavel' in col[0]:
        print(f"  {col[0]}: {col[1]}")

cursor.close()
conn.close()

print("\n=== Concluído ===")
