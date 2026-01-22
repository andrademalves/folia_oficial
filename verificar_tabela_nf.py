import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestaoTi.settings')
django.setup()

from django.db import connection

def show_table_structure(table_name):
    with connection.cursor() as cursor:
        cursor.execute(f'DESCRIBE {table_name}')
        columns = cursor.fetchall()
        
        print(f"\n{'='*80}")
        print(f"TABELA: {table_name}")
        print(f"{'='*80}")
        print(f"{'Campo':<30} {'Tipo':<25} {'Null':<8} {'Key':<8} {'Default':<15}")
        print(f"{'-'*80}")
        
        for col in columns:
            field = col[0]
            type_val = col[1]
            null_val = col[2]
            key = col[3]
            default = col[4] if col[4] else ''
            
            print(f"{field:<30} {type_val:<25} {null_val:<8} {key:<8} {default:<15}")

# Mostrar estrutura das tabelas principais
show_table_structure('contas_receber_notafiscal')
show_table_structure('contas_receber_parcela')
show_table_structure('contas_receber_cliente')

print(f"\n{'='*80}\n")
cursor.execute("DESCRIBE contas_receber_notafiscal")
columns = cursor.fetchall()

print("\nColunas existentes:")
for col in columns:
    print(f"  - {col[0]} ({col[1]})")

# Verificar se nro_nota existe
column_names = [col[0] for col in columns]
if 'nro_nota' in column_names:
    print("\n✓ Coluna nro_nota já existe!")
else:
    print("\n✗ Coluna nro_nota NÃO existe. Precisa ser adicionada.")
    print("\nAdicionar coluna? (s/n)")
    resposta = input()
    if resposta.lower() == 's':
        cursor.execute("ALTER TABLE contas_receber_notafiscal ADD COLUMN nro_nota INTEGER NOT NULL UNIQUE AFTER id")
        db.commit()
        print("✓ Coluna adicionada com sucesso!")

cursor.close()
db.close()
