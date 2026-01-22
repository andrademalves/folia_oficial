codigo = '104931041100001272351234569000100000000000014'
print(f'Código completo: {codigo}')
print(f'Tamanho: {len(codigo)}')
print()

campo_livre = codigo[19:]
print(f'Campo livre (pos 20+): {campo_livre}')
print(f'Tamanho: {len(campo_livre)}')
print()

print('Análise do campo livre:')
print(f'  Pos 01-06 (benef): {campo_livre[:6]}')
print(f'  Pos 07-07 (DV): {campo_livre[6:7]}')
print(f'  Pos 08-10 (3NN): {campo_livre[7:10]}')
print(f'  Pos 11-11 (cart): {campo_livre[10:11]}')
print(f'  Pos 12-23 (12NN): {campo_livre[11:23]}')
print(f'  Pos 24-25 (modal): {campo_livre[23:25]}')
if len(campo_livre) > 25:
    print(f'  Pos 26 (EXTRA!): {campo_livre[25:26]}')
