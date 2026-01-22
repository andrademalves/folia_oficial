#!/bin/bash

###############################################################################
# Script de Deploy - Sistema de Gestão TI
# Versão: 1.0
# Data: 09/01/2026
# Uso: sudo bash deploy_producao.sh
###############################################################################

set -e  # Parar em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funções auxiliares
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_header() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE} $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
    echo ""
}

# Verificar se está rodando como root
if [[ $EUID -ne 0 ]]; then
   print_error "Este script precisa ser executado como root (use sudo)"
   exit 1
fi

# Obter usuário real (não root)
REAL_USER=${SUDO_USER:-$USER}

clear
echo -e "${GREEN}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║         INSTALADOR - SISTEMA DE GESTÃO TI                    ║"
echo "║         Versão 1.0 - Deploy Automatizado                     ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# Confirmação
read -p "Deseja iniciar a instalação em ambiente de PRODUÇÃO? (s/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[SsYy]$ ]]; then
    print_warning "Instalação cancelada pelo usuário"
    exit 1
fi

###############################################################################
# PASSO 1: Coleta de Informações
###############################################################################

print_header "PASSO 1: Configurações Iniciais"

# Diretório de instalação
read -p "Diretório de instalação [/var/www/gestao_ti]: " INSTALL_DIR
INSTALL_DIR=${INSTALL_DIR:-/var/www/gestao_ti}

# Domínio
read -p "Domínio do servidor (ex: gestao.exemplo.com.br): " DOMAIN
if [ -z "$DOMAIN" ]; then
    read -p "IP do servidor: " SERVER_IP
    DOMAIN=$SERVER_IP
fi

# Banco de Dados
read -p "Nome do banco de dados [gestao_ti_prod]: " DB_NAME
DB_NAME=${DB_NAME:-gestao_ti_prod}

read -p "Usuário do banco de dados [gestao_user]: " DB_USER
DB_USER=${DB_USER:-gestao_user}

read -sp "Senha do banco de dados: " DB_PASSWORD
echo ""

read -sp "Senha do MySQL root: " MYSQL_ROOT_PASSWORD
echo ""

# Email (opcional)
read -p "Configurar email para notificações? (s/n): " -n 1 -r CONFIG_EMAIL
echo ""

if [[ $CONFIG_EMAIL =~ ^[SsYy]$ ]]; then
    read -p "Host SMTP [smtp.gmail.com]: " EMAIL_HOST
    EMAIL_HOST=${EMAIL_HOST:-smtp.gmail.com}
    
    read -p "Porta SMTP [587]: " EMAIL_PORT
    EMAIL_PORT=${EMAIL_PORT:-587}
    
    read -p "Email remetente: " EMAIL_USER
    read -sp "Senha do email: " EMAIL_PASSWORD
    echo ""
fi

# SSL
read -p "Configurar SSL com Let's Encrypt? (s/n): " -n 1 -r SETUP_SSL
echo ""

print_success "Configurações coletadas!"

###############################################################################
# PASSO 2: Atualizar Sistema
###############################################################################

print_header "PASSO 2: Atualizando Sistema"

apt update
apt upgrade -y
print_success "Sistema atualizado"

###############################################################################
# PASSO 3: Instalar Dependências
###############################################################################

print_header "PASSO 3: Instalando Dependências"

print_info "Instalando Python e ferramentas..."
apt install -y python3 python3-pip python3-venv python3-dev

print_info "Instalando MySQL..."
apt install -y mysql-server default-libmysqlclient-dev

print_info "Instalando Nginx..."
apt install -y nginx

print_info "Instalando ferramentas adicionais..."
apt install -y build-essential git curl wget ufw certbot python3-certbot-nginx

print_success "Todas as dependências instaladas"

###############################################################################
# PASSO 4: Configurar MySQL
###############################################################################

print_header "PASSO 4: Configurando Banco de Dados"

# Criar banco de dados
mysql -uroot -p"$MYSQL_ROOT_PASSWORD" <<MYSQL_SCRIPT
CREATE DATABASE IF NOT EXISTS $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASSWORD';
GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'localhost';
FLUSH PRIVILEGES;
MYSQL_SCRIPT

print_success "Banco de dados configurado"

###############################################################################
# PASSO 5: Criar Estrutura de Diretórios
###############################################################################

print_header "PASSO 5: Criando Estrutura de Diretórios"

# Verificar se o diretório já existe
if [ -d "$INSTALL_DIR" ]; then
    print_warning "Diretório $INSTALL_DIR já existe"
    read -p "Deseja fazer backup e continuar? (s/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[SsYy]$ ]]; then
        BACKUP_DIR="${INSTALL_DIR}_backup_$(date +%Y%m%d_%H%M%S)"
        mv "$INSTALL_DIR" "$BACKUP_DIR"
        print_success "Backup criado em $BACKUP_DIR"
    else
        print_error "Instalação cancelada"
        exit 1
    fi
fi

mkdir -p $INSTALL_DIR
mkdir -p /var/log/gestao_ti
mkdir -p /var/backups/gestao_ti

print_success "Diretórios criados"

###############################################################################
# PASSO 6: Copiar Arquivos do Projeto
###############################################################################

print_header "PASSO 6: Copiando Arquivos do Projeto"

# Assumindo que os arquivos estão no diretório atual
CURRENT_DIR=$(dirname "$(readlink -f "$0")")

print_info "Copiando arquivos de $CURRENT_DIR para $INSTALL_DIR..."
rsync -av --progress "$CURRENT_DIR/" "$INSTALL_DIR/" \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.git' \
    --exclude='db.sqlite3' \
    --exclude='.env' \
    --exclude='staticfiles' \
    --exclude='media'

print_success "Arquivos copiados"

###############################################################################
# PASSO 7: Configurar Ambiente Virtual Python
###############################################################################

print_header "PASSO 7: Configurando Ambiente Virtual Python"

cd $INSTALL_DIR

print_info "Criando ambiente virtual..."
python3 -m venv venv

print_info "Instalando dependências Python..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn python-dotenv

print_success "Ambiente Python configurado"

###############################################################################
# PASSO 8: Criar Arquivo .env
###############################################################################

print_header "PASSO 8: Criando Arquivo de Configuração"

# Gerar SECRET_KEY
SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")

cat > $INSTALL_DIR/.env <<EOF
# Configurações de Produção - Gestão TI
# Gerado em: $(date)

# Django Settings
DEBUG=False
SECRET_KEY=$SECRET_KEY
ALLOWED_HOSTS=$DOMAIN,localhost,127.0.0.1

# Database
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
DB_HOST=localhost
DB_PORT=3306
EOF

if [[ $CONFIG_EMAIL =~ ^[SsYy]$ ]]; then
cat >> $INSTALL_DIR/.env <<EOF

# Email Configuration
EMAIL_HOST=$EMAIL_HOST
EMAIL_PORT=$EMAIL_PORT
EMAIL_USE_TLS=True
EMAIL_HOST_USER=$EMAIL_USER
EMAIL_HOST_PASSWORD=$EMAIL_PASSWORD
EOF
fi

chmod 600 $INSTALL_DIR/.env
print_success "Arquivo .env criado"

###############################################################################
# PASSO 9: Atualizar settings.py
###############################################################################

print_header "PASSO 9: Atualizando Configurações Django"

# Criar backup do settings.py
cp $INSTALL_DIR/gestaoTi/settings.py $INSTALL_DIR/gestaoTi/settings.py.backup

# Adicionar suporte a .env no início do settings.py
sed -i '1i import os' $INSTALL_DIR/gestaoTi/settings.py
sed -i '2i from pathlib import Path' $INSTALL_DIR/gestaoTi/settings.py
sed -i '3i from dotenv import load_dotenv' $INSTALL_DIR/gestaoTi/settings.py
sed -i '4i load_dotenv()' $INSTALL_DIR/gestaoTi/settings.py

# Nota: As configurações específicas precisarão ser ajustadas manualmente
# ou via script Python adicional

print_success "Settings.py atualizado (verificar ajustes manuais)"

###############################################################################
# PASSO 10: Executar Migrações
###############################################################################

print_header "PASSO 10: Executando Migrações do Banco"

cd $INSTALL_DIR
source venv/bin/activate

python manage.py migrate

print_success "Migrações executadas"

###############################################################################
# PASSO 11: Criar Superusuário
###############################################################################

print_header "PASSO 11: Criando Superusuário"

print_info "Por favor, crie o superusuário para administração:"
python manage.py createsuperuser

###############################################################################
# PASSO 12: Coletar Arquivos Estáticos
###############################################################################

print_header "PASSO 12: Coletando Arquivos Estáticos"

python manage.py collectstatic --noinput

print_success "Arquivos estáticos coletados"

###############################################################################
# PASSO 13: Configurar Gunicorn
###############################################################################

print_header "PASSO 13: Configurando Gunicorn"

cat > /etc/systemd/system/gestao_ti.service <<EOF
[Unit]
Description=Gestao TI Django Application
After=network.target mysql.service
Requires=mysql.service

[Service]
Type=notify
User=www-data
Group=www-data
RuntimeDirectory=gunicorn
WorkingDirectory=$INSTALL_DIR
Environment="PATH=$INSTALL_DIR/venv/bin"
ExecStart=$INSTALL_DIR/venv/bin/gunicorn \\
          --workers 3 \\
          --timeout 120 \\
          --bind unix:/run/gunicorn/gestao_ti.sock \\
          --access-logfile /var/log/gestao_ti/access.log \\
          --error-logfile /var/log/gestao_ti/error.log \\
          gestaoTi.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable gestao_ti
systemctl start gestao_ti

print_success "Gunicorn configurado e iniciado"

###############################################################################
# PASSO 14: Configurar Nginx
###############################################################################

print_header "PASSO 14: Configurando Nginx"

cat > /etc/nginx/sites-available/gestao_ti <<EOF
server {
    listen 80;
    server_name $DOMAIN;

    client_max_body_size 20M;

    access_log /var/log/nginx/gestao_ti_access.log;
    error_log /var/log/nginx/gestao_ti_error.log;

    location = /favicon.ico { 
        access_log off; 
        log_not_found off; 
    }
    
    location /static/ {
        alias $INSTALL_DIR/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias $INSTALL_DIR/media/;
        expires 30d;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn/gestao_ti.sock;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header Host \$host;
        proxy_redirect off;
    }
}
EOF

# Ativar site
ln -sf /etc/nginx/sites-available/gestao_ti /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Testar configuração
nginx -t

# Reiniciar Nginx
systemctl restart nginx
systemctl enable nginx

print_success "Nginx configurado"

###############################################################################
# PASSO 15: Configurar Firewall
###############################################################################

print_header "PASSO 15: Configurando Firewall"

ufw allow 'Nginx Full'
ufw allow 22/tcp
ufw --force enable

print_success "Firewall configurado"

###############################################################################
# PASSO 16: Configurar SSL
###############################################################################

if [[ $SETUP_SSL =~ ^[SsYy]$ ]]; then
    print_header "PASSO 16: Configurando SSL (Let's Encrypt)"
    
    # Verificar se o domínio está acessível
    print_info "Certifique-se de que o DNS está apontando para este servidor"
    read -p "Pressione ENTER para continuar..."
    
    certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN
    
    # Configurar renovação automática
    systemctl enable certbot.timer
    
    print_success "SSL configurado"
else
    print_warning "SSL não configurado. Execute manualmente: sudo certbot --nginx -d $DOMAIN"
fi

###############################################################################
# PASSO 17: Configurar Permissões
###############################################################################

print_header "PASSO 17: Ajustando Permissões"

chown -R www-data:www-data $INSTALL_DIR
chmod -R 755 $INSTALL_DIR
chmod -R 775 $INSTALL_DIR/media 2>/dev/null || mkdir -p $INSTALL_DIR/media && chmod -R 775 $INSTALL_DIR/media
chmod -R 775 $INSTALL_DIR/staticfiles
chmod 600 $INSTALL_DIR/.env

print_success "Permissões ajustadas"

###############################################################################
# PASSO 18: Configurar Backup Automático
###############################################################################

print_header "PASSO 18: Configurando Backup Automático"

cat > /usr/local/bin/backup_gestao_ti.sh <<'BACKUP_SCRIPT'
#!/bin/bash

BACKUP_DIR="/var/backups/gestao_ti"
DATE=$(date +%Y%m%d_%H%M%S)
INSTALL_DIR="$INSTALL_DIR"
DB_NAME="$DB_NAME"
DB_USER="$DB_USER"
DB_PASSWORD="$DB_PASSWORD"

# Criar diretório de backup
mkdir -p $BACKUP_DIR

# Backup do banco de dados
mysqldump -u $DB_USER -p"$DB_PASSWORD" $DB_NAME | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Backup dos arquivos de mídia
if [ -d "$INSTALL_DIR/media" ]; then
    tar -czf $BACKUP_DIR/media_$DATE.tar.gz -C $INSTALL_DIR media
fi

# Remover backups com mais de 30 dias
find $BACKUP_DIR -type f -mtime +30 -delete

echo "Backup concluído: $DATE"
BACKUP_SCRIPT

# Substituir variáveis
sed -i "s|\$INSTALL_DIR|$INSTALL_DIR|g" /usr/local/bin/backup_gestao_ti.sh
sed -i "s|\$DB_NAME|$DB_NAME|g" /usr/local/bin/backup_gestao_ti.sh
sed -i "s|\$DB_USER|$DB_USER|g" /usr/local/bin/backup_gestao_ti.sh
sed -i "s|\$DB_PASSWORD|$DB_PASSWORD|g" /usr/local/bin/backup_gestao_ti.sh

chmod +x /usr/local/bin/backup_gestao_ti.sh

# Adicionar ao cron (diário às 2h)
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/backup_gestao_ti.sh >> /var/log/gestao_ti_backup.log 2>&1") | crontab -

print_success "Backup automático configurado (diário às 2h da manhã)"

###############################################################################
# PASSO 19: Popular Dados Iniciais
###############################################################################

print_header "PASSO 19: Populando Dados Iniciais"

cd $INSTALL_DIR
source venv/bin/activate

# Verificar se existe comando para popular dados
if python manage.py help | grep -q "popular_dados"; then
    python manage.py popular_dados
    print_success "Dados iniciais populados"
else
    print_warning "Comando popular_dados não encontrado. Execute manualmente se necessário."
fi

###############################################################################
# FINALIZAÇÃO
###############################################################################

print_header "INSTALAÇÃO CONCLUÍDA!"

echo ""
print_success "Sistema de Gestão TI instalado com sucesso!"
echo ""
print_info "Informações da instalação:"
echo "  - Diretório: $INSTALL_DIR"
echo "  - Domínio: $DOMAIN"
echo "  - Banco de dados: $DB_NAME"
echo "  - Usuário DB: $DB_USER"
echo ""
print_info "Serviços:"
echo "  - Gunicorn: systemctl status gestao_ti"
echo "  - Nginx: systemctl status nginx"
echo ""
print_info "Logs:"
echo "  - Aplicação: /var/log/gestao_ti/"
echo "  - Nginx: /var/log/nginx/"
echo "  - Backup: /var/log/gestao_ti_backup.log"
echo ""
print_info "Comandos úteis:"
echo "  - Ver logs: sudo journalctl -u gestao_ti -f"
echo "  - Reiniciar: sudo systemctl restart gestao_ti"
echo "  - Backup manual: sudo /usr/local/bin/backup_gestao_ti.sh"
echo ""

if [[ $SETUP_SSL =~ ^[SsYy]$ ]]; then
    print_success "Acesse: https://$DOMAIN"
else
    print_warning "Acesse: http://$DOMAIN"
    print_warning "Lembre-se de configurar SSL!"
fi

echo ""
print_warning "IMPORTANTE: Verifique o arquivo $INSTALL_DIR/gestaoTi/settings.py"
print_warning "e ajuste as configurações conforme necessário."
echo ""

# Criar arquivo de resumo
cat > $INSTALL_DIR/INSTALACAO_INFO.txt <<EOF
═══════════════════════════════════════════════════════
INFORMAÇÕES DA INSTALAÇÃO - GESTÃO TI
═══════════════════════════════════════════════════════

Data da Instalação: $(date)
Servidor: $(hostname)

CONFIGURAÇÕES:
- Diretório: $INSTALL_DIR
- Domínio: $DOMAIN
- Banco de dados: $DB_NAME
- Usuário DB: $DB_USER

SERVIÇOS:
- Gunicorn: systemctl status gestao_ti
- Nginx: systemctl status nginx
- MySQL: systemctl status mysql

LOGS:
- Aplicação: /var/log/gestao_ti/
- Nginx: /var/log/nginx/
- Backup: /var/log/gestao_ti_backup.log

BACKUPS:
- Localização: /var/backups/gestao_ti/
- Frequência: Diário às 02:00
- Retenção: 30 dias

COMANDOS ÚTEIS:
- Ver logs em tempo real: sudo journalctl -u gestao_ti -f
- Reiniciar aplicação: sudo systemctl restart gestao_ti
- Reiniciar Nginx: sudo systemctl restart nginx
- Backup manual: sudo /usr/local/bin/backup_gestao_ti.sh

ATUALIZAR SISTEMA:
1. sudo systemctl stop gestao_ti
2. cd $INSTALL_DIR
3. source venv/bin/activate
4. git pull (ou copiar novos arquivos)
5. pip install -r requirements.txt
6. python manage.py migrate
7. python manage.py collectstatic --noinput
8. sudo systemctl start gestao_ti

ARQUIVO DE CONFIGURAÇÃO:
- .env: $INSTALL_DIR/.env (senha protegido)
- Settings: $INSTALL_DIR/gestaoTi/settings.py

═══════════════════════════════════════════════════════
EOF

print_success "Informações salvas em: $INSTALL_DIR/INSTALACAO_INFO.txt"

echo ""
print_success "🎉 Instalação concluída com sucesso! 🎉"
echo ""
