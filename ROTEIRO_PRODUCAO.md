# Roteiro de Implantação em Produção
## Sistema de Gestão TI

---

## 📋 Pré-requisitos

### Software Necessário
- [ ] Python 3.12 ou superior
- [ ] MySQL 5.7+ ou MariaDB 10.3+
- [ ] Git (opcional, para controle de versão)
- [ ] Servidor Web (Apache ou Nginx)
- [ ] Certificado SSL (para HTTPS)

### Informações que você precisará
- [ ] IP/domínio do servidor
- [ ] Credenciais de acesso ao servidor
- [ ] Credenciais do banco de dados MySQL
- [ ] Email para notificações (opcional)

---

## 🚀 Passo 1: Preparar o Servidor

### Windows Server

```powershell
# 1. Instalar Python
# Baixar de: https://www.python.org/downloads/
# Durante instalação, marcar "Add Python to PATH"

# 2. Verificar instalação
python --version
pip --version

# 3. Instalar MySQL
# Baixar de: https://dev.mysql.com/downloads/mysql/
# Anotar senha do root durante instalação
```

### Linux (Ubuntu/Debian)

```bash
# 1. Atualizar sistema
sudo apt update
sudo apt upgrade -y

# 2. Instalar Python e dependências
sudo apt install python3 python3-pip python3-venv -y
sudo apt install python3-dev default-libmysqlclient-dev build-essential -y

# 3. Instalar MySQL
sudo apt install mysql-server -y
sudo mysql_secure_installation

# 4. Instalar Nginx
sudo apt install nginx -y
```

---

## 📦 Passo 2: Transferir Arquivos do Projeto

### Opção A: Via ZIP

```powershell
# No computador de desenvolvimento:
# 1. Criar ZIP do projeto (excluindo arquivos desnecessários)
Compress-Archive -Path "C:\HD_Antigo\01- Projetos Dev\1.3 Gestao\*" `
    -DestinationPath "C:\gestao_ti.zip" `
    -Force

# Excluir manualmente do ZIP:
# - __pycache__/
# - *.pyc
# - db.sqlite3 (se existir)
# - .env (será criado novo)
```

### Opção B: Via Git

```bash
# No servidor de produção:
cd /var/www/
git clone [URL_DO_REPOSITORIO] gestao_ti
cd gestao_ti
```

### Opção C: Via FTP/SCP

```bash
# Usar WinSCP, FileZilla ou SCP para transferir arquivos
# Destino sugerido: /var/www/gestao_ti (Linux) ou C:\inetpub\gestao_ti (Windows)
```

---

## 🔧 Passo 3: Configurar Ambiente Python

### No Servidor de Produção

```bash
# Linux
cd /var/www/gestao_ti
python3 -m venv venv
source venv/bin/activate

# Windows
cd C:\inetpub\gestao_ti
python -m venv venv
.\venv\Scripts\activate
```

### Instalar Dependências

```bash
# Com o ambiente virtual ativado
pip install --upgrade pip
pip install -r requirements.txt

# Instalar servidor WSGI (para produção)
pip install gunicorn  # Linux
pip install waitress  # Windows
```

---

## 🗄️ Passo 4: Configurar Banco de Dados MySQL

### Criar Banco e Usuário

```sql
-- Conectar ao MySQL como root
mysql -u root -p

-- Criar banco de dados
CREATE DATABASE gestao_ti_prod CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Criar usuário (TROQUE A SENHA!)
CREATE USER 'gestao_user'@'localhost' IDENTIFIED BY 'SENHA_FORTE_AQUI';

-- Conceder permissões
GRANT ALL PRIVILEGES ON gestao_ti_prod.* TO 'gestao_user'@'localhost';
FLUSH PRIVILEGES;

-- Sair
EXIT;
```

---

## ⚙️ Passo 5: Configurar Django para Produção

### Criar arquivo de ambiente (.env)

```bash
# Criar arquivo .env na raiz do projeto
nano .env  # Linux
notepad .env  # Windows
```

### Conteúdo do .env:

```ini
# Configurações de Produção
DEBUG=False
SECRET_KEY=sua-chave-secreta-muito-segura-aqui-gere-uma-nova
ALLOWED_HOSTS=seudominio.com.br,www.seudominio.com.br,IP_DO_SERVIDOR

# Database
DB_NAME=gestao_ti_prod
DB_USER=gestao_user
DB_PASSWORD=SENHA_FORTE_AQUI
DB_HOST=localhost
DB_PORT=3306

# Email (opcional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-app
```

### Modificar settings.py

Editar `gestaoTi/settings.py`:

```python
import os
from pathlib import Path

# Carregar variáveis de ambiente
from dotenv import load_dotenv
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-ALTERE-ISSO')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost').split(',')

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME', 'gestao_ti_prod'),
        'USER': os.getenv('DB_USER', 'gestao_user'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '3306'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
    }
}

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Security Settings (Produção)
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
```

### Instalar python-dotenv

```bash
pip install python-dotenv
```

---

## 🔐 Passo 6: Gerar SECRET_KEY Segura

```bash
# Gerar nova SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Copiar o resultado e colar no arquivo .env
```

---

## 📊 Passo 7: Executar Migrações e Coletar Arquivos Estáticos

```bash
# Com ambiente virtual ativado
cd /var/www/gestao_ti  # ou caminho no Windows

# Executar migrações
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Popular dados iniciais (módulos e menus)
python manage.py popular_dados

# Coletar arquivos estáticos
python manage.py collectstatic --noinput
```

---

## 🌐 Passo 8: Configurar Servidor Web

### Opção A: Nginx + Gunicorn (Linux - RECOMENDADO)

#### 1. Criar serviço Systemd para Gunicorn

```bash
sudo nano /etc/systemd/system/gestao_ti.service
```

**Conteúdo:**

```ini
[Unit]
Description=Gestao TI Django Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/gestao_ti
Environment="PATH=/var/www/gestao_ti/venv/bin"
ExecStart=/var/www/gestao_ti/venv/bin/gunicorn \
          --workers 3 \
          --bind unix:/var/www/gestao_ti/gestao_ti.sock \
          gestaoTi.wsgi:application

[Install]
WantedBy=multi-user.target
```

#### 2. Iniciar e habilitar serviço

```bash
sudo systemctl start gestao_ti
sudo systemctl enable gestao_ti
sudo systemctl status gestao_ti
```

#### 3. Configurar Nginx

```bash
sudo nano /etc/nginx/sites-available/gestao_ti
```

**Conteúdo:**

```nginx
server {
    listen 80;
    server_name seudominio.com.br www.seudominio.com.br;

    client_max_body_size 20M;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias /var/www/gestao_ti/staticfiles/;
    }

    location /media/ {
        alias /var/www/gestao_ti/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/gestao_ti/gestao_ti.sock;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### 4. Ativar site

```bash
sudo ln -s /etc/nginx/sites-available/gestao_ti /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 5. Configurar SSL (HTTPS)

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obter certificado SSL
sudo certbot --nginx -d seudominio.com.br -d www.seudominio.com.br

# Renovação automática (já configurado)
sudo certbot renew --dry-run
```

### Opção B: IIS + Waitress (Windows Server)

#### 1. Criar script de inicialização

Criar arquivo `start_server.py`:

```python
from waitress import serve
from gestaoTi.wsgi import application

if __name__ == '__main__':
    serve(application, host='127.0.0.1', port=8000, threads=4)
```

#### 2. Configurar como serviço Windows

Usar `NSSM` (Non-Sucking Service Manager):

```powershell
# Baixar NSSM de https://nssm.cc/download
# Instalar serviço
nssm install GestaoTI "C:\inetpub\gestao_ti\venv\Scripts\python.exe" "C:\inetpub\gestao_ti\start_server.py"
nssm set GestaoTI AppDirectory "C:\inetpub\gestao_ti"
nssm start GestaoTI
```

#### 3. Configurar IIS como proxy reverso

Instalar URL Rewrite e configurar regras de proxy.

---

## 🔒 Passo 9: Configurar Permissões e Segurança

### Linux

```bash
# Ajustar proprietário dos arquivos
sudo chown -R www-data:www-data /var/www/gestao_ti

# Ajustar permissões
sudo chmod -R 755 /var/www/gestao_ti
sudo chmod -R 775 /var/www/gestao_ti/media
sudo chmod -R 775 /var/www/gestao_ti/staticfiles

# Proteger arquivo .env
sudo chmod 600 /var/www/gestao_ti/.env
```

### Firewall

```bash
# Ubuntu/Debian
sudo ufw allow 'Nginx Full'
sudo ufw allow 22/tcp
sudo ufw enable

# Windows
# Configurar Windows Firewall para permitir porta 80 e 443
```

---

## 📝 Passo 10: Configurar Backup Automático

### Script de Backup (Linux)

Criar `/var/www/gestao_ti/backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/gestao_ti"
DATE=$(date +%Y%m%d_%H%M%S)

# Criar diretório de backup
mkdir -p $BACKUP_DIR

# Backup do banco de dados
mysqldump -u gestao_user -p'SENHA' gestao_ti_prod > $BACKUP_DIR/db_$DATE.sql

# Backup dos arquivos de mídia
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /var/www/gestao_ti/media

# Remover backups com mais de 30 dias
find $BACKUP_DIR -type f -mtime +30 -delete

echo "Backup concluído: $DATE"
```

### Agendar backup diário

```bash
sudo chmod +x /var/www/gestao_ti/backup.sh
sudo crontab -e

# Adicionar linha (backup diário às 2h da manhã):
0 2 * * * /var/www/gestao_ti/backup.sh >> /var/log/gestao_ti_backup.log 2>&1
```

---

## 🧪 Passo 11: Testar a Instalação

### Checklist de Testes

- [ ] Acessar o site pelo domínio/IP
- [ ] Testar login com superusuário
- [ ] Verificar se módulos aparecem
- [ ] Criar um registro de teste em cada módulo
- [ ] Testar upload de arquivos
- [ ] Verificar relatórios em PDF/Excel
- [ ] Testar em navegadores diferentes
- [ ] Verificar logs de erro

### Comandos úteis

```bash
# Ver logs do Gunicorn
sudo journalctl -u gestao_ti -f

# Ver logs do Nginx
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

# Reiniciar serviços
sudo systemctl restart gestao_ti
sudo systemctl restart nginx
```

---

## 🔄 Passo 12: Atualizar o Sistema (Após Instalação)

```bash
# 1. Parar serviço
sudo systemctl stop gestao_ti

# 2. Ativar ambiente virtual
cd /var/www/gestao_ti
source venv/bin/activate

# 3. Atualizar código (Git)
git pull origin main

# 4. Instalar novas dependências
pip install -r requirements.txt

# 5. Executar migrações
python manage.py migrate

# 6. Coletar arquivos estáticos
python manage.py collectstatic --noinput

# 7. Reiniciar serviço
sudo systemctl start gestao_ti
```

---

## 📞 Passo 13: Monitoramento e Manutenção

### Ferramentas Recomendadas

1. **Monitoramento de Servidor**
   - Uptime Robot (gratuito)
   - New Relic (pago)
   - Prometheus + Grafana

2. **Logs Centralizados**
   - Sentry (para erros Django)
   - ELK Stack (Elasticsearch, Logstash, Kibana)

3. **Backups**
   - Backup diário automático (configurado no Passo 10)
   - Backup mensal para armazenamento externo

### Manutenção Regular

- [ ] Atualizar dependências mensalmente
- [ ] Verificar logs de erro semanalmente
- [ ] Testar backups mensalmente
- [ ] Atualizar certificado SSL (automático com Certbot)
- [ ] Monitorar uso de disco e memória

---

## ⚠️ Troubleshooting

### Erro: "Bad Gateway 502"
- Verificar se Gunicorn está rodando: `sudo systemctl status gestao_ti`
- Verificar logs: `sudo journalctl -u gestao_ti -f`

### Erro: "Static files not loading"
- Executar: `python manage.py collectstatic --noinput`
- Verificar permissões: `sudo chown -R www-data:www-data /var/www/gestao_ti/staticfiles`

### Erro: "Database connection failed"
- Verificar credenciais no arquivo `.env`
- Testar conexão MySQL: `mysql -u gestao_user -p gestao_ti_prod`

### Erro: "Permission denied"
- Ajustar permissões: `sudo chown -R www-data:www-data /var/www/gestao_ti`

---

## 📋 Checklist Final de Produção

- [ ] DEBUG=False no settings.py
- [ ] SECRET_KEY única e segura
- [ ] ALLOWED_HOSTS configurado corretamente
- [ ] Banco de dados MySQL em produção
- [ ] Migrações executadas
- [ ] Superusuário criado
- [ ] Dados iniciais populados
- [ ] Arquivos estáticos coletados
- [ ] Nginx/IIS configurado
- [ ] SSL/HTTPS ativo
- [ ] Backup automático configurado
- [ ] Firewall configurado
- [ ] Logs funcionando
- [ ] Testes realizados
- [ ] Documentação entregue

---

## 📚 Referências

- [Django Deployment Checklist](https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [MySQL Documentation](https://dev.mysql.com/doc/)
- [Let's Encrypt](https://letsencrypt.org/)

---

## 🆘 Suporte

Para dúvidas ou problemas:
1. Consultar logs do sistema
2. Verificar documentação oficial do Django
3. Contatar desenvolvedor responsável

**Data de criação:** 27/12/2025
**Versão do Sistema:** 1.0
**Django Version:** 6.0
