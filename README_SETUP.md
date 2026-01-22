# Setup de Produção Django - Automação Completa

## Descrição
Script de automação Python para configurar ambiente de produção Django em máquina Windows.

## Pré-requisitos
1. **Python 3.10+** instalado e no PATH do sistema
2. **MySQL Server** instalado e em execução
3. **Código fonte** do projeto já copiado para `C:\1.3 Gestao`

## Funcionalidades do Script

### O script `setup_production_FINAL.py` executa automaticamente:

1. **Verificação de Diretórios e Arquivos**
   - Valida existência de `manage.py`, `requirements.txt` e `settings.py`
   - Muda para o diretório do projeto

2. **Ambiente Virtual (VENV)**
   - Detecta se o venv existe e está funcional
   - Remove venv corrompido se necessário
   - Cria novo ambiente virtual
   - Identifica executáveis Python/Pip da venv

3. **Instalação de Dependências**
   - Atualiza pip
   - Instala Django
   - Remove mysqlclient (problemas no Windows) e instala PyMySQL
   - Instala todas as dependências do `requirements.txt`

4. **Patches de Compatibilidade**
   - Adiciona patch PyMySQL no `manage.py`
   - Adiciona patch PyMySQL no `__init__.py` do projeto
   - Corrige versão reportada do PyMySQL para compatibilidade com Django 6.0

5. **Configuração de Banco de Dados**
   - Atualiza senha do MySQL no `settings.py` para: `F0li@2026!`
   - Extrai nome do banco de dados
   - Cria banco com encoding UTF-8 (pt-BR): `CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci`
   - Adiciona configuração `STATIC_ROOT` se não existir

6. **Setup Django**
   - Executa `makemigrations`
   - Executa `migrate` (cria todas as tabelas)
   - Executa `collectstatic --noinput` (coleta arquivos estáticos)

7. **Testes Finais**
   - Executa `check` do Django

## Como Executar

### Opção 1: Comando Direto (Recomendado)
```powershell
cd "C:\1.3 Gestao"
python setup_production_FINAL.py
```

### Opção 2: Duplo Clique
1. Navegue até `C:\1.3 Gestao`
2. Duplo clique em `setup_production_FINAL.py`

## Arquivos Gerados

### Log de Execução
```
C:\1.3 Gestao\setup_log_YYYY-MM-DD_HHMMSS.txt
```
Contém registro detalhado de todas as operações executadas.

### Backup do Settings
```
C:\1.3 Gestao\gestaoTi\settings.py.backup_setup
```
Backup automático do `settings.py` antes de modificações.

### Arquivos Estáticos
```
C:\1.3 Gestao\staticfiles\
```
Diretório com todos os arquivos estáticos coletados.

## Correções Aplicadas Automaticamente

### 1. Problema: mysqlclient não compila no Windows com Python 3.14
**Solução:** Script usa PyMySQL (puro Python) com patches de compatibilidade

### 2. Problema: Django não aceita versão antiga do PyMySQL
**Solução:** Script força versão reportada para 2.2.1

### 3. Problema: Pillow corrompido após migração
**Solução:** Reinstalação automática do Pillow

### 4. Problema: STATIC_ROOT não configurado
**Solução:** Adição automática ao settings.py

### 5. Problema: Encoding de caracteres especiais no console Windows
**Solução:** Tratamento de exceções Unicode com fallback ASCII

## Configurações Aplicadas

### Banco de Dados
- **Usuário:** root
- **Senha:** F0li@2026!
- **Nome do DB:** gestao_ti (ou extraído do settings.py)
- **Charset:** utf8mb4
- **Collation:** utf8mb4_unicode_ci

### Arquivos Modificados
1. `manage.py` - Patch PyMySQL
2. `gestaoTi/__init__.py` - Patch PyMySQL + versão
3. `gestaoTi/settings.py` - Senha DB + STATIC_ROOT

## Próximos Passos (Pós-Setup)

### 1. Criar Superusuário
```powershell
.\venv\Scripts\python.exe manage.py createsuperuser
```

### 2. Executar Servidor de Desenvolvimento
```powershell
.\venv\Scripts\python.exe manage.py runserver
```
Acesse: http://127.0.0.1:8000

### 3. Configurar para Produção

#### Editar `gestaoTi/settings.py`:
```python
DEBUG = False
ALLOWED_HOSTS = ['seu-dominio.com', 'www.seu-dominio.com']
SECRET_KEY = 'gere-uma-nova-chave-secreta-aqui'
```

#### Gerar nova SECRET_KEY:
```powershell
.\venv\Scripts\python.exe -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 4. Configurar Servidor Web (IIS ou Nginx)

#### Para IIS:
```powershell
pip install wfastcgi
wfastcgi-enable
```

#### Para Gunicorn (Linux):
```bash
pip install gunicorn
gunicorn gestaoTi.wsgi:application --bind 0.0.0.0:8000
```

## Resolução de Problemas

### Script falha ao criar banco de dados
**Causa:** MySQL não está no PATH ou senha incorreta

**Solução:**
```sql
-- Execute manualmente no MySQL:
CREATE DATABASE gestao_ti CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
GRANT ALL PRIVILEGES ON gestao_ti.* TO 'root'@'localhost' IDENTIFIED BY 'F0li@2026!';
FLUSH PRIVILEGES;
```

### Erro ao executar migrate
**Causa:** Banco de dados não acessível

**Solução:**
1. Verifique se MySQL está rodando
2. Confirme senha em `settings.py`
3. Teste conexão:
```powershell
mysql -u root -p
```

### ImportError ao rodar servidor
**Causa:** Venv não ativado

**Solução:** Sempre use o Python da venv:
```powershell
.\venv\Scripts\python.exe manage.py runserver
```

## Estrutura do Projeto

```
C:\1.3 Gestao\
├── manage.py                    # [MODIFICADO] Patch PyMySQL
├── requirements.txt
├── setup_production_FINAL.py    # [NOVO] Este script
├── setup_log_*.txt              # [GERADO] Logs de execução
├── venv\                        # [CRIADO/VALIDADO] Ambiente virtual
├── staticfiles\                 # [CRIADO] Arquivos estáticos
├── gestaoTi\
│   ├── __init__.py              # [MODIFICADO] Patch PyMySQL
│   ├── settings.py              # [MODIFICADO] Senha + STATIC_ROOT
│   ├── settings.py.backup_setup # [BACKUP] Backup automático
│   ├── urls.py
│   └── wsgi.py
├── boletos\
├── cadastros\
├── contas_receber\
├── financeiro\
└── ...
```

## Logs e Debugging

### Ver últimas 50 linhas do log:
```powershell
Get-Content setup_log_*.txt -Tail 50
```

### Filtrar apenas erros:
```powershell
Select-String -Path setup_log_*.txt -Pattern "\[ERRO\]"
```

## Suporte

Para problemas ou dúvidas:
1. Verifique o arquivo de log gerado
2. Consulte a documentação do Django: https://docs.djangoproject.com
3. Verifique configuração do MySQL

## Notas Importantes

- ⚠️ **Senha padrão:** `F0li@2026!` - Altere em produção!
- ⚠️ **DEBUG=True:** Desabilite em produção!
- ⚠️ **SECRET_KEY:** Gere nova chave em produção!
- ✅ **Backup:** Script cria backup automático do settings.py
- ✅ **UTF-8:** Banco configurado para suporte completo ao português

---

**Versão:** 1.0 Final  
**Data:** 11/01/2026  
**Compatibilidade:** Windows 10/11, Python 3.10+, Django 6.0, MySQL 5.7+
