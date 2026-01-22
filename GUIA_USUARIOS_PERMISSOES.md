# GUIA DE GESTÃO DE USUÁRIOS E PERMISSÕES

## ✅ Status do Módulo Sistema

O módulo **Sistema** está agora **ATIVO** e aparece no painel inicial!

---

## 👥 Como Criar Novos Usuários

### 1. Acesse o Módulo Sistema

Faça login como **admin** e clique no módulo **Sistema** no painel inicial.

### 2. Acesse Gestão de Usuários

No módulo Sistema, clique em **"Gestão de Usuários"**

URL direta: http://127.0.0.1:8000/usuarios/usuarios/

### 3. Criar Novo Usuário

Clique no botão **"Criar Usuário"** e preencha:
- Nome de usuário
- Email
- Senha
- Confirmar senha

### 4. Configurar Permissões

Após criar o usuário, clique no botão **"Permissões"** ao lado do usuário.

Você verá todos os módulos do sistema. Para cada módulo, marque:

- ☑️ **Visualizar** - Usuário pode ver o módulo e seus menus
- ☑️ **Criar** - Usuário pode criar novos registros
- ☑️ **Editar** - Usuário pode editar registros
- ☑️ **Excluir** - Usuário pode deletar registros

**Importante:** As permissões são por MENU, não por módulo inteiro.

---

## 🔐 Como Funcionam as Permissões

### Para Superusuários (admin)
- ✅ Veem **TODOS** os módulos automaticamente
- ✅ Têm **TODAS** as permissões em todos os módulos
- ✅ Não precisam de configuração de permissões

### Para Usuários Normais
- ⚠️ Veem **APENAS** os módulos que você liberar
- ⚠️ Têm **APENAS** as permissões que você marcar
- ⚠️ Precisam ter permissões configuradas manualmente

---

## 📋 Exemplo Prático

### Cenário: Criar usuário apenas para Financeiro

**Passo 1:** Criar usuário
```
Usuário: joao
Senha: joao123
```

**Passo 2:** Configurar permissões

Na tela de permissões, marque:

**Módulo Financeiro:**
- ☑️ Dashboard - Visualizar
- ☑️ Contas a Pagar - Visualizar, Criar, Editar
- ☑️ Dar Baixa - Visualizar, Criar
- ☑️ Conta Corrente - Visualizar
- ☑️ Relatórios - Visualizar

**Resultado:**
- João verá APENAS o módulo Financeiro
- Poderá criar e editar contas a pagar
- Poderá dar baixa em contas
- Poderá ver relatórios mas não editar

---

## 🎯 Módulos Disponíveis para Permissões

1. **Cadastros** (5 menus)
   - Dashboard, Plano de Contas, Contas Financeiras, Métodos, Relatórios

2. **Financeiro** (5 menus)
   - Dashboard, Contas a Pagar, Dar Baixa, Conta Corrente, Relatórios

3. **Contas a Receber** (7 menus)
   - Dashboard, Notas Fiscais, Parcelas, Negociações, Créditos, Aprovações, Relatórios

4. **Boletos** (5 menus)
   - Dashboard, Lista de Boletos, Gerar Boletos, Remessas, Configurações

5. **Importações** (6 menus)
   - Dashboard, Cadastro Geral, Notas Fiscais, Parcelas, Logs, Configurações

6. **Sistema** (5 menus)
   - Gestão de Usuários, Criar Usuário, Módulos, Menus, Admin Django

---

## 🧪 Usuário de Teste Criado

Foi criado um usuário de exemplo para você testar:

**Credenciais:**
- Usuário: `teste`
- Senha: `teste1234`

**Permissões configuradas:**
- ✅ **Financeiro:** Visualizar, Criar, Editar (todos os menus)
- ✅ **Cadastros:** Apenas Visualizar (todos os menus)

**Teste:**
1. Faça logout do admin
2. Faça login com `teste` / `teste1234`
3. Verá apenas 2 módulos: Financeiro e Cadastros
4. No Financeiro poderá criar/editar
5. Nos Cadastros poderá apenas visualizar

---

## 🔧 Ações Disponíveis para Usuários

Na tela de **Gestão de Usuários** você pode:

| Ação | Descrição |
|------|-----------|
| ➕ Criar | Criar novo usuário |
| ✏️ Editar | Editar dados do usuário |
| 🔐 Permissões | Configurar permissões por módulo |
| 🔄 Ativar/Desativar | Bloquear/desbloquear acesso do usuário |

---

## ⚙️ Gerenciamento Avançado

### Via Admin Django

Acesse: http://127.0.0.1:8000/admin/

Lá você pode:
- Criar grupos de permissões
- Atribuir permissões por grupo
- Gerenciar módulos e menus
- Ver logs de ações

### Via Interface do Sistema

Use a interface em `/usuarios/usuarios/` para:
- Gestão simplificada de usuários
- Configuração visual de permissões
- Ativação/desativação rápida

---

## 📝 Comandos Úteis

### Criar usuário via script Python:
```python
from django.contrib.auth.models import User
user = User.objects.create_user('nome', 'email@exemplo.com', 'senha')
```

### Dar permissão a um módulo inteiro:
```python
from usuarios.models import Modulo, Menu, PermissaoMenu

modulo = Modulo.objects.get(nome='Financeiro')
menus = Menu.objects.filter(modulo=modulo)

for menu in menus:
    PermissaoMenu.objects.create(
        tipo='usuario',
        usuario=user,
        menu=menu,
        pode_visualizar=True,
        pode_criar=True,
        pode_editar=True,
        pode_excluir=False
    )
```

---

## 🎓 Boas Práticas

1. **Sempre dê apenas as permissões necessárias**
   - Princípio do menor privilégio

2. **Use grupos para permissões comuns**
   - Crie grupos como "Financeiro", "Gerente", etc.
   - Atribua usuários aos grupos

3. **Desative usuários ao invés de deletar**
   - Mantém histórico de ações
   - Pode reativar depois

4. **Teste com usuário de teste primeiro**
   - Valide as permissões antes de criar usuário real

5. **Documente quem tem acesso a quê**
   - Use campo "observações" no perfil

---

## ❓ Resolução de Problemas

### Usuário não vê nenhum módulo
**Causa:** Nenhuma permissão configurada
**Solução:** Acesse Permissões e marque pelo menos "Visualizar" em algum menu

### Usuário vê módulo mas não consegue fazer nada
**Causa:** Só tem permissão de visualizar
**Solução:** Marque "Criar" ou "Editar" conforme necessário

### Alterações não aparecem
**Causa:** Cache do navegador
**Solução:** Faça logout e login novamente, ou CTRL+SHIFT+R

---

## 📞 URLs Importantes

- **Gestão de Usuários:** http://127.0.0.1:8000/usuarios/usuarios/
- **Criar Usuário:** http://127.0.0.1:8000/usuarios/usuarios/criar/
- **Admin Django:** http://127.0.0.1:8000/admin/
- **Módulos:** http://127.0.0.1:8000/admin/usuarios/modulo/
- **Menus:** http://127.0.0.1:8000/admin/usuarios/menu/

---

**Tudo pronto para gerenciar usuários e permissões!** 🎉
