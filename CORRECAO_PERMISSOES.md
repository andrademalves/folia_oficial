# Correção de Permissões - Problema "Menu não encontrado"

## 🔴 PROBLEMA

Quando você cria um usuário pelo painel admin e atribui permissões:
- O usuário consegue **ver o módulo** na tela inicial
- Mas ao clicar no menu, aparece **"Menu não encontrado"**
- Mesmo com todas as permissões marcadas

### Por que isso acontece?

O modelo `PermissaoMenu` tem um campo obrigatório chamado `tipo` que pode ser:
- `'usuario'` - para permissões diretas de um usuário
- `'grupo'` - para permissões de um grupo

Quando você cria permissões pelo **Admin do Django**, se esse campo não for preenchido corretamente, o sistema não consegue localizar as permissões.

---

## ✅ SOLUÇÕES

### 1️⃣ Correção Automática (RECOMENDADO)

Execute o script de correção completa:

```bash
python setup_producao_permissoes.py
```

Este script:
- ✅ Corrige o campo `tipo` em todas as permissões existentes
- ✅ Garante consistência entre usuários e grupos
- ✅ Identifica e reporta problemas

### 2️⃣ Diagnóstico Detalhado

Para ver exatamente o que está errado com um usuário específico:

```bash
python diagnosticar_permissoes.py
```

Digite o username do usuário quando solicitado. O script mostrará:
- Status do usuário (superusuário, ativo, etc)
- Grupos que pertence
- Permissões diretas e seus problemas
- Permissões herdadas de grupos
- Módulos que deveria ver

### 3️⃣ Correção Simples

Se preferir uma correção mais simples apenas do campo `tipo`:

```bash
python corrigir_permissoes_tipo.py
```

---

## 🔧 CORREÇÃO PERMANENTE

O arquivo `usuarios/admin.py` foi atualizado para **prevenir** esse problema no futuro:

```python
def save_model(self, request, obj, form, change):
    # Auto-define o tipo baseado nos campos preenchidos
    if not obj.tipo or obj.tipo == '':
        if obj.usuario is not None:
            obj.tipo = 'usuario'
        elif obj.grupo is not None:
            obj.tipo = 'grupo'
    super().save_model(request, obj, form, change)
```

Agora, quando criar uma permissão pelo admin:
1. Selecione o **Tipo** manualmente OU
2. O sistema define automaticamente baseado se você preencheu Usuário ou Grupo

---

## 📋 COMO USAR CORRETAMENTE O PAINEL

### Criar Permissões para um Usuário

1. Acesse `/admin/usuarios/permissaomenu/`
2. Clique em "Add Permissão menu"
3. **IMPORTANTE**: Configure assim:
   - **Tipo**: Selecione `Usuário`
   - **Usuário**: Selecione o usuário
   - **Grupo**: Deixe em branco
   - **Menu**: Selecione o menu
   - **Permissões**: Marque as que desejar

### Criar Permissões para um Grupo

1. Acesse `/admin/usuarios/permissaomenu/`
2. Clique em "Add Permissão menu"
3. **IMPORTANTE**: Configure assim:
   - **Tipo**: Selecione `Grupo`
   - **Usuário**: Deixe em branco
   - **Grupo**: Selecione o grupo
   - **Menu**: Selecione o menu
   - **Permissões**: Marque as que desejar

---

## 🚀 PARA SERVIDOR DE PRODUÇÃO

### Passo a Passo Completo:

```bash
# 1. Conectar ao servidor
ssh root@72.60.139.167

# 2. Ir para o diretório do projeto
cd /root/folia_oficial

# 3. Ativar ambiente virtual
source venv/bin/activate

# 4. Executar correção
python setup_producao_permissoes.py

# 5. Reiniciar servidor (se estiver rodando)
# Ctrl+C para parar
python manage.py runserver 0.0.0.0:8000
```

### Verificar Funcionamento:

1. Faça logout do sistema
2. Faça login com o usuário que tinha problema
3. Verifique se:
   - Os módulos aparecem
   - Ao clicar, os menus abrem corretamente
   - As ações (criar, editar, excluir) funcionam

---

## 🔍 SCRIPTS DISPONÍVEIS

| Script | Descrição |
|--------|-----------|
| `setup_producao_permissoes.py` | **Correção completa** - 3 etapas de validação e correção |
| `diagnosticar_permissoes.py` | **Diagnóstico detalhado** - Identifica problemas por usuário |
| `corrigir_permissoes_tipo.py` | **Correção simples** - Apenas corrige o campo tipo |

---

## ⚠️ IMPORTANTE

- **Sempre execute a correção** após criar permissões manualmente pelo admin
- **Ou use a tela de "Gerenciar Permissões"** do próprio sistema (já corrige automaticamente)
- O usuário **adm_folia** funciona porque é **superusuário** (bypass de permissões)

---

## 📞 SUPORTE

Se após executar os scripts o problema persistir:

1. Execute `diagnosticar_permissoes.py` com o username do usuário
2. Verifique se o usuário está **ativo** (`is_active=True`)
3. Verifique se o **menu existe** e está **ativo**
4. Verifique se o **módulo** do menu está **ativo**

---

## ✨ EXEMPLO DE USO

```bash
# Cenário: Usuário "joao" não consegue acessar módulo Financeiro

# 1. Diagnosticar
python diagnosticar_permissoes.py
# Digite: joao

# 2. Corrigir
python setup_producao_permissoes.py

# 3. Reiniciar servidor
python manage.py runserver 0.0.0.0:8000

# 4. Usuário "joao" faz logout e login novamente
# ✅ Problema resolvido!
```
