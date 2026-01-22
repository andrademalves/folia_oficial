with open('TESTE_WEB_20251228_200738.REM', 'rb') as f:
    content = f.read()

print(f'Total bytes: {len(content)}')

lines = content.decode('ascii').split('\r\n')
print(f'\nTotal linhas após split: {len(lines)}')

for i, line in enumerate(lines[:12], 1):
    print(f'Linha {i}: {len(line)} chars')
    
# Ver últimos bytes
print(f'\nÚltimos 100 bytes:')
print(content[-100:])
