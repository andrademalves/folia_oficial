# COMANDOS PARA INICIAR O SERVIDOR DJANGO

## Opção 1: Usando o Script Batch (MAIS FÁCIL)
```
Duplo clique no arquivo: INICIAR_SERVIDOR.bat
```

## Opção 2: Via PowerShell (linha por linha)

### Passo 1: Navegar até a pasta
```powershell
cd "C:\1.3 Gestao"
```

### Passo 2: Iniciar o servidor
```powershell
.\venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000
```

## Opção 3: Comando único (copiar e colar no PowerShell)
```powershell
cd "C:\1.3 Gestao"; .\venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000
```

---

## Se der erro na VENV

### Verificar se a venv existe:
```powershell
cd "C:\1.3 Gestao"
Test-Path "venv\Scripts\python.exe"
```

Se retornar `False`, a venv não existe. Crie novamente:

```powershell
cd "C:\1.3 Gestao"
python -m venv venv
```

### Reinstalar dependências:
```powershell
cd "C:\1.3 Gestao"
.\venv\Scripts\python.exe -m pip install --upgrade pip
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe -m pip install pymysql
```

---

## Se der erro ao iniciar Python

### Verificar versão do Python instalado:
```powershell
python --version
```

Deve retornar Python 3.10 ou superior.

### Se Python não for reconhecido:
Instale o Python 3.10+ de: https://www.python.org/downloads/

Durante a instalação, marque:
- ✅ Add Python to PATH

---

## Resolver problema "venv corrompido"

### Deletar venv antiga:
```powershell
cd "C:\1.3 Gestao"
Remove-Item -Recurse -Force venv
```

### Criar nova venv:
```powershell
python -m venv venv
```

### Reinstalar tudo:
```powershell
.\venv\Scripts\python.exe -m pip install --upgrade pip
.\venv\Scripts\python.exe -m pip install django pymysql pillow reportlab
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

---

## Após o servidor iniciar

### URLs de Acesso:
- **Local:** http://127.0.0.1:8000
- **Rede:** http://192.168.10.8:8000

### Credenciais:
- **Usuário:** admin
- **Senha:** adm1234@

### Parar o servidor:
Pressione `CTRL + C` no terminal

---

## Comandos Úteis

### Ver se o servidor está rodando:
```powershell
Get-Process | Where-Object {$_.ProcessName -eq "python"}
```

### Matar processo do Python (se travou):
```powershell
Stop-Process -Name python -Force
```

### Testar conexão com banco:
```powershell
cd "C:\1.3 Gestao"
.\venv\Scripts\python.exe manage.py check --database default
```

### Aplicar migrations:
```powershell
cd "C:\1.3 Gestao"
.\venv\Scripts\python.exe manage.py migrate
```

### Criar novo superusuário:
```powershell
cd "C:\1.3 Gestao"
.\venv\Scripts\python.exe manage.py createsuperuser
```
