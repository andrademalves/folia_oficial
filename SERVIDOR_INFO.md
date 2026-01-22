# 🚀 SISTEMA EM EXECUÇÃO

## ✅ Status do Servidor

**Servidor Django iniciado com sucesso!**

- **URL Local:** http://127.0.0.1:8000
- **URL Rede:** http://0.0.0.0:8000
- **Status:** ✅ Rodando
- **Django Version:** 6.0
- **Python Version:** 3.14.2

---

## 🔐 Credenciais de Acesso

### Superusuário Criado

```
Usuário: admin
Senha: adm1234@
Email: admin@gestao.local
```

**Permissões:**
- ✅ Superusuário (acesso total ao sistema)
- ✅ Acesso ao Django Admin
- ✅ Acesso a TODOS os módulos do sistema

---

## 🌐 URLs de Acesso

### Aplicação Principal
**http://127.0.0.1:8000/**

### Painel Administrativo Django
**http://127.0.0.1:8000/admin/**

Login com:
- Usuário: `admin`
- Senha: `adm1234@`

---

## 📋 Módulos do Sistema

O superusuário `admin` tem acesso completo aos seguintes módulos:

1. **Boletos** - `/boletos/`
2. **Cadastros** - `/cadastros/`
3. **Contas a Receber** - `/contas_receber/`
4. **Financeiro** - `/financeiro/`
5. **Importações** - `/importacoes/`
6. **Usuários** - `/usuarios/`

---

## 🛠️ Gerenciamento do Servidor

### Para Parar o Servidor
Pressione no terminal: **`CTRL + C`** ou **`CTRL + BREAK`**

### Para Reiniciar o Servidor
```powershell
cd "C:\1.3 Gestao"
.\venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000
```

### Para Rodar em Outra Porta
```powershell
.\venv\Scripts\python.exe manage.py runserver 0.0.0.0:9000
```

---

## 📊 Banco de Dados

- **Tipo:** MySQL
- **Nome:** gestao_ti
- **Usuário:** root
- **Senha:** F0li@2026!
- **Encoding:** utf8mb4 (suporte completo a português)
- **Status:** ✅ Conectado

---

## ⚠️ Avisos Importantes

### Servidor de Desenvolvimento
O servidor atual é para **DESENVOLVIMENTO** apenas. Para produção, use:
- Gunicorn (Linux)
- mod_wsgi (Apache)
- wfastcgi (IIS)

### Segurança
- 🔒 Altere `DEBUG = False` em produção
- 🔒 Gere nova `SECRET_KEY` em produção
- 🔒 Configure `ALLOWED_HOSTS` adequadamente
- 🔒 Use HTTPS em produção

---

## 📝 Logs do Servidor

Os logs aparecem em tempo real no terminal onde o servidor está rodando.

Para ver requisições:
- Requisições GET/POST aparecem no terminal
- Formato: `[data] "MÉTODO /url/ HTTP/1.1" STATUS`

---

## 🔧 Comandos Úteis

### Criar Novo Usuário (via shell)
```powershell
.\venv\Scripts\python.exe manage.py createsuperuser
```

### Verificar Sistema
```powershell
.\venv\Scripts\python.exe manage.py check
```

### Aplicar Migrações
```powershell
.\venv\Scripts\python.exe manage.py migrate
```

### Coletar Arquivos Estáticos
```powershell
.\venv\Scripts\python.exe manage.py collectstatic
```

### Abrir Shell Django
```powershell
.\venv\Scripts\python.exe manage.py shell
```

---

## 🎯 Próximos Passos

1. ✅ **Servidor rodando** - http://127.0.0.1:8000
2. ✅ **Superusuário criado** - admin / adm1234@
3. ⬜ Testar login no sistema
4. ⬜ Verificar todos os módulos
5. ⬜ Configurar dados iniciais (se necessário)
6. ⬜ Ajustar configurações de produção

---

## 📞 Acesso Rápido

**Sistema Principal:** http://127.0.0.1:8000  
**Admin Django:** http://127.0.0.1:8000/admin  
**User:** admin  
**Pass:** adm1234@

---

**Data/Hora de Início:** 11/01/2026 - 17:11:53  
**Status:** 🟢 ONLINE
