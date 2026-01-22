beneficiario_original = '0123456'
print(f'Original: "{beneficiario_original}" (tamanho: {len(beneficiario_original)})')

# Método atual
ajustado1 = str(beneficiario_original).zfill(6)
print(f'zfill(6): "{ajustado1}" (tamanho: {len(ajustado1)})')

# Com [-6:]
ajustado2 = str(beneficiario_original).zfill(6)[-6:]
print(f'zfill(6)[-6:]: "{ajustado2}" (tamanho: {len(ajustado2)})')

# Correto: primeiro limitar tamanho, depois zfill
ajustado3 = str(beneficiario_original)[-6:].zfill(6)
print(f'[-6:].zfill(6): "{ajustado3}" (tamanho: {len(ajustado3)})')

print('\n✅ Solução correta: primeiro pegar últimos 6, depois preencher se necessário')
