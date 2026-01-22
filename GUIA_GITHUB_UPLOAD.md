# Guia: Subir Projeto Gestão para GitHub

## 📋 Passo a Passo Completo

### **1. Instalar Git for Windows**

1. Baixe o instalador: https://git-scm.com/download/win
2. Execute o instalador baixado
3. Siga as opções padrão (recomendado):
   - ✅ Use Git from the Windows Command Prompt
   - ✅ Use OpenSSH
   - ✅ Use the OpenSSL library
   - ✅ Checkout Windows-style, commit Unix-style line endings
   - ✅ Use MinTTY
   - ✅ Default (fast-forward or merge)
4. Após a instalação, **REINICIE o VS Code** (importante!)

### **2. Configurar Git (primeira vez)**

Abra um terminal PowerShell e execute:

```powershell
# Configurar seu nome
git config --global user.name "Seu Nome"

# Configurar seu email (use o mesmo do GitHub)
git config --global user.email "seu.email@example.com"

# Verificar configurações
git config --list
```

### **3. Configurar SSH Key para GitHub** (Recomendado)

#### 3.1. Gerar chave SSH:
```powershell
ssh-keygen -t ed25519 -C "seu.email@example.com"
```
- Pressione Enter para aceitar o local padrão
- Pressione Enter para senha vazia (ou defina uma senha)

#### 3.2. Copiar a chave pública:
```powershell
Get-Content ~/.ssh/id_ed25519.pub | clip
```

#### 3.3. Adicionar no GitHub:
1. Acesse: https://github.com/settings/keys
2. Clique em "New SSH key"
3. Cole a chave (Ctrl+V)
4. Dê um nome (ex: "PC Trabalho")
5. Clique em "Add SSH key"

#### 3.4. Testar conexão:
```powershell
ssh -T git@github.com
```
Deve retornar: "Hi andrademalves! You've successfully authenticated..."

### **4. Preparar o Repositório Local**

```powershell
# Navegar para o diretório do projeto
cd "c:\1.3 Gestao"

# Inicializar repositório Git
git init

# Verificar status
git status
```

### **5. Criar arquivo .gitignore**

O arquivo `.gitignore` já será criado automaticamente com:
- Arquivos Python compilados (`__pycache__/`, `*.pyc`, `*.pyo`)
- Ambientes virtuais (`venv/`, `env/`)
- Banco de dados local (`*.db`, `*.sqlite3`, `*.FDB`)
- Variáveis de ambiente (`.env`, `.env.local`)
- Cache do Django (`staticfiles/`)
- Arquivos de log (`*.log`)
- Arquivos do sistema (`.DS_Store`, `Thumbs.db`)

### **6. Verificar o Repositório GitHub**

Certifique-se de que o repositório existe:
- URL: https://github.com/andrademalves/folia_oficial
- Se não existir, crie em: https://github.com/new
  - Nome: `folia_oficial`
  - Visibilidade: Público ou Privado (sua escolha)
  - **NÃO** inicialize com README, .gitignore ou licença

### **7. Conectar ao Repositório Remoto**

```powershell
# Adicionar repositório remoto
git remote add origin git@github.com:andrademalves/folia_oficial.git

# Verificar remote
git remote -v
```

### **8. Adicionar e Commitar Arquivos**

```powershell
# Adicionar todos os arquivos
git add .

# Ver o que será commitado
git status

# Fazer o primeiro commit
git commit -m "feat: commit inicial do projeto Gestão - sistema completo com módulos de boletos, contas a receber e NFS"
```

### **9. Fazer Push para GitHub**

```powershell
# Renomear branch para main (se necessário)
git branch -M main

# Push inicial
git push -u origin main
```

### **10. Verificar no GitHub**

Acesse: https://github.com/andrademalves/folia_oficial

Você deve ver todos os arquivos do projeto!

---

## 🔧 Comandos Úteis para o Futuro

### Adicionar mudanças:
```powershell
git add .
git commit -m "Descrição da mudança"
git push
```

### Ver histórico:
```powershell
git log --oneline
```

### Ver mudanças não commitadas:
```powershell
git status
git diff
```

### Puxar mudanças do GitHub:
```powershell
git pull
```

### Criar e mudar de branch:
```powershell
git checkout -b nova-feature
git push -u origin nova-feature
```

---

## ⚠️ Arquivos que NÃO devem ir para o GitHub

- ❌ Senhas e credenciais (`.env`)
- ❌ Banco de dados com dados reais (`*.FDB`, `*.db`)
- ❌ Arquivos de cache (`__pycache__/`)
- ❌ Ambientes virtuais (`venv/`)
- ❌ Chaves privadas e certificados

Estes já estão incluídos no `.gitignore`!

---

## 📞 Problemas Comuns

### "Permission denied (publickey)"
- Verifique se a chave SSH foi adicionada ao GitHub
- Teste: `ssh -T git@github.com`

### "Repository not found"
- Verifique se o repositório existe no GitHub
- Verifique se você tem permissão (se for privado)

### "Fatal: not a git repository"
- Certifique-se de estar no diretório correto
- Execute `git init` primeiro

---

## ✅ Checklist Final

- [ ] Git instalado e configurado
- [ ] Chave SSH configurada no GitHub
- [ ] Repositório `folia_oficial` criado no GitHub
- [ ] `.gitignore` criado
- [ ] Primeiro commit realizado
- [ ] Push para GitHub bem-sucedido
- [ ] Arquivos visíveis em https://github.com/andrademalves/folia_oficial

---

**Data de criação:** 21 de Janeiro de 2026  
**Projeto:** Sistema de Gestão - Folia Oficial
