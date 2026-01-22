#!/bin/bash
set -e

echo "=== 1. Atualizando sistema ==="
apt update
DEBIAN_FRONTEND=noninteractive apt upgrade -y

echo ""
echo "=== 2. Instalando dependÃªncias bÃ¡sicas ==="
apt install -y build-essential python3 python3-pip python3-venv git curl wget

echo ""
echo "=== 3. Instalando MySQL Server ==="
DEBIAN_FRONTEND=noninteractive apt install -y mysql-server mysql-client libmysqlclient-dev pkg-config

echo ""
echo "=== 4. Configurando MySQL ==="
systemctl start mysql
systemctl enable mysql

# Criar database e usuÃ¡rio
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
echo "=== 8. Instalando dependÃªncias Python ==="
pip install -r requirements.txt
pip install mysqlclient

echo ""
echo "=== 9. Executando migrations ==="
python manage.py makemigrations
python manage.py migrate

echo ""
echo "=== 10. Coletando arquivos estÃ¡ticos ==="
python manage.py collectstatic --noinput || true

echo ""
echo "=== 11. Criando superusuÃ¡rio ==="
python manage.py shell << 'PYEOF'
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='adm_folia').exists():
    User.objects.create_superuser('adm_folia', 'admin@folia.com', 'Folia2026@')
    print('SuperusuÃ¡rio criado com sucesso!')
else:
    print('SuperusuÃ¡rio jÃ¡ existe!')
PYEOF

echo ""
echo "=== Deploy ConcluÃ­do! ==="
echo ""
echo "InformaÃ§Ãµes do Sistema:"
echo "- UsuÃ¡rio: adm_folia"
echo "- Senha: Folia2026@"
echo "- Database: folia_db"
echo "- Servidor: http://72.60.139.167:8000"
echo ""
echo "Para iniciar o servidor, execute:"
echo "cd /root/folia_oficial"
echo "source venv/bin/activate"
echo "python manage.py runserver 0.0.0.0:8000"
