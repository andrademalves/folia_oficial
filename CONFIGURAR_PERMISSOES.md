# Como Configurar Permissões no Sistema

## 1. Acessar o Admin do Django

1. Acesse: http://127.0.0.1:8000/admin/
2. Faça login com seu usuário **superuser** (admin)

---

## 2. Criar Grupos de Usuários

### Passo a Passo:

1. No admin, clique em **"Groups"** (Grupos)
2. Clique em **"Add Group"** (Adicionar grupo)
3. Crie os seguintes grupos:

   **Grupo: Diretoria**
   - Nome: `Diretoria`
   - Permissions: (selecione as permissões que achar necessário)

   **Grupo: Administrativo**
   - Nome: `Administrativo`
   - Permissions: (selecione as permissões que achar necessário)

4. Clique em **"Save"** (Salvar)

---

## 3. Atribuir Permissões aos Módulos

### Passo a Passo:

1. No admin, navegue até **"Usuarios"** → **"Permissão menus"**
2. Clique em **"Add Permissão menu"**
3. Configure as permissões para o módulo **Aprovações**:

   **Configuração:**
   - **Menu**: Selecione "Créditos Pendentes"
   - **Grupos permitidos**: Selecione "Diretoria" e/ou "Administrativo"
   - Deixe **"Users permitidos"** vazio (ou adicione usuários específicos se necessário)

4. Clique em **"Save"**

---

## 4. Adicionar Usuários aos Grupos

### Passo a Passo:

1. No admin, clique em **"Users"** (Usuários)
2. Clique no **usuário** que você quer dar permissão
3. Role até a seção **"Permissions"**
4. Na lista **"Groups"**, selecione os grupos:
   - `Diretoria` (para diretores)
   - `Administrativo` (para gerentes administrativos)
5. Clique em **"Save"**

---

## 5. Como Funciona o Sistema de Permissões

### Estrutura:
```
Módulo (ex: Aprovações)
  └── Menu (ex: Créditos Pendentes)
       └── PermissaoMenu
            ├── Grupos permitidos (Diretoria, Administrativo, etc.)
            └── Usuários permitidos (usuários específicos)
```

### Lógica de Verificação:
- O decorator `@verificar_permissao_menu('/contas-receber/aprovacoes/')` verifica:
  1. Se o usuário é **superuser** → ✅ Acesso liberado
  2. Se existe um registro **PermissaoMenu** para essa URL
  3. Se o **usuário** está na lista de "users permitidos" → ✅ Acesso liberado
  4. Se algum **grupo do usuário** está na lista de "grupos permitidos" → ✅ Acesso liberado
  5. Caso contrário → ❌ Acesso negado

---

## 6. Comandos Úteis (Terminal)

### Criar os grupos via comando Python:

```bash
python manage.py shell
```

Depois execute:

```python
from django.contrib.auth.models import Group
from usuarios.models import Modulo, Menu, PermissaoMenu

# Criar grupos
diretoria, _ = Group.objects.get_or_create(name='Diretoria')
administrativo, _ = Group.objects.get_or_create(name='Administrativo')

# Buscar o menu de aprovações
menu_aprovacoes = Menu.objects.get(url='/contas-receber/aprovacoes/')

# Criar permissão
permissao, created = PermissaoMenu.objects.get_or_create(menu=menu_aprovacoes)
permissao.grupos_permitidos.add(diretoria, administrativo)
permissao.save()

print("✅ Permissões configuradas com sucesso!")
```

---

## 7. Testar as Permissões

1. **Crie um usuário de teste**:
   - No admin: Users → Add user
   - Username: `aprovador_teste`
   - Senha: `senha123`
   - **NÃO** marque "Superuser"
   - Adicione ao grupo "Diretoria"
   - Salve

2. **Faça logout do admin**

3. **Faça login com o usuário teste**

4. **Acesse a home**: http://127.0.0.1:8000/
   - ✅ Deve aparecer o módulo "Aprovações"

5. **Clique em "Créditos Pendentes"**
   - ✅ Deve abrir a lista de aprovações

6. **Clique em "Visualizar"**
   - ✅ Deve abrir a página de detalhes
   - Se for o próprio crédito: campos desabilitados com aviso
   - Se for crédito de outro usuário: botões de Aprovar/Rejeitar funcionando

---

## 8. Resumo de Onde Configurar

| **O que configurar** | **Onde** |
|---------------------|----------|
| Criar grupos | Admin → Groups → Add Group |
| Adicionar usuário ao grupo | Admin → Users → (selecionar usuário) → Groups |
| Dar permissão ao módulo | Admin → Usuarios → Permissão menus → Add |
| Ver quem pode acessar | Admin → Usuarios → Permissão menus → (filtrar por menu) |

---

## 9. Dicas de Segurança

✅ **Boas práticas:**
- Não dê permissão de superuser para todos
- Use grupos para organizar permissões (Diretoria, Financeiro, Operacional, etc.)
- Um usuário **NÃO PODE** aprovar seu próprio crédito (validação já implementada)
- Superusers têm acesso a tudo (use com cuidado)

❌ **Evite:**
- Dar acesso de superuser para usuários operacionais
- Deixar módulos sem permissão configurada (qualquer um acessa)
- Usar o mesmo usuário para solicitar e aprovar créditos
