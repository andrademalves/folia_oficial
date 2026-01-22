# Script de Deploy Automatizado para Servidor Ubuntu
# Servidor: 72.60.139.167
# Data: 22/01/2026

$servidor = "root@72.60.139.167"
$senha = "Andrade20262"

Write-Host "=== Deploy do Projeto Folia Oficial ===" -ForegroundColor Green
Write-Host ""

# Criar script temporário para execução remota
$scriptRemoto = @'
#!/bin/bash
set -e

echo "=== 1. Atualizando sistema ==="
apt update
DEBIAN_FRONTEND=noninteractive apt upgrade -y

echo ""
echo "=== 2. Instalando dependências básicas ==="
apt install -y build-essential python3 python3-pip python3-venv git curl wget

echo ""
echo "=== 3. Instalando MySQL Server ==="
DEBIAN_FRONTEND=noninteractive apt install -y mysql-server mysql-client libmysqlclient-dev

echo ""
echo "=== 4. Configurando MySQL ==="
systemctl start mysql
systemctl enable mysql

# Criar database e usuário
mysql -e "CREATE DATABASE IF NOT EXISTS folia_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -e "CREATE USER IF NOT EXISTS 'folia_user'@'localhost' IDENTIFIED BY 'Folia2026@DB';"
mysql -e "GRANT ALL PRIVILEGES ON folia_db.* TO 'folia_user'@'localhost';"
mysql -e "FLUSH PRIVILEGES;"

echo ""
echo "=== 5. Clonando projeto do GitHub ==="
cd /root
if [ -d "folia_oficial" ]; then
    rm -rf folia_oficial
fi
git clone https://github.com/andrademalves/folia_oficial.git
cd folia_oficial

echo ""
echo "=== 6. Criando ambiente virtual Python ==="
python3 -m venv venv
source venv/bin/activate

echo ""
echo "=== 7. Atualizando pip ==="
pip install --upgrade pip

echo ""
echo "=== 8. Instalando dependências Python ==="
pip install -r requirements.txt
pip install mysqlclient

echo ""
echo "=== 9. Configurando settings.py para MySQL ==="
# Fazer backup do settings original
cp gestaoTi/settings.py gestaoTi/settings.py.bak

# Adicionar configuração do MySQL
cat > /tmp/db_config.txt << 'EOF'

# Configuração do Banco de Dados MySQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'folia_db',
        'USER': 'folia_user',
        'PASSWORD': 'Folia2026@DB',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# Configuração de hosts permitidos
ALLOWED_HOSTS = ['72.60.139.167', 'localhost', '127.0.0.1', '*']

# Debug para produção (alterar para False depois)
DEBUG = True
EOF

echo ""
echo "=== 10. Executando migrations ==="
python manage.py makemigrations
python manage.py migrate

echo ""
echo "=== 11. Coletando arquivos estáticos ==="
python manage.py collectstatic --noinput || true

echo ""
echo "=== 12. Criando superusuário ==="
python manage.py shell << 'PYEOF'
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='adm_folia').exists():
    User.objects.create_superuser('adm_folia', 'admin@folia.com', 'Folia2026@')
    print('Superusuário criado com sucesso!')
else:
    print('Superusuário já existe!')
PYEOF

echo ""
echo "=== Deploy Concluído! ==="
echo ""
echo "Informações do Sistema:"
echo "- Usuário: adm_folia"
echo "- Senha: Folia2026@"
echo "- Database: folia_db"
echo "- Servidor: http://72.60.139.167:8000"
echo ""
echo "Para iniciar o servidor, execute:"
echo "cd /root/folia_oficial"
echo "source venv/bin/activate"
echo "python manage.py runserver 0.0.0.0:8000"
'@

# Salvar script temporário
$scriptRemoto | Out-File -FilePath "deploy_remote.sh" -Encoding UTF8

Write-Host "Script de deploy criado. Execute manualmente no servidor:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Conecte-se ao servidor:" -ForegroundColor Cyan
Write-Host "   ssh root@72.60.139.167" -ForegroundColor White
Write-Host ""
Write-Host "2. Copie o conteúdo do arquivo 'deploy_remote.sh' para o servidor" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Execute no servidor:" -ForegroundColor Cyan
Write-Host "   chmod +x deploy_remote.sh" -ForegroundColor White
Write-Host "   ./deploy_remote.sh" -ForegroundColor White
Write-Host ""
Write-Host "Ou use este comando direto:" -ForegroundColor Yellow
Write-Host 'ssh root@72.60.139.167 "bash -s" < deploy_remote.sh' -ForegroundColor White
