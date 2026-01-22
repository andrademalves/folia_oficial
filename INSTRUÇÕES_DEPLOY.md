# Instruções de Deploy - Servidor Linux

## 🚀 Deploy Rápido (Automatizado)

### Pré-requisitos no Servidor Linux
- Ubuntu 20.04+ ou Debian 10+
- Acesso root (sudo)
- Conexão com a internet

### Passo a Passo

#### 1. Transferir arquivos para o servidor

**Opção A: Via SCP (do Windows para Linux)**
```powershell
# No Windows (PowerShell), navegue até o diretório do projeto
cd "C:\HD_Antigo\01- Projetos Dev\1.3 Gestao"

# Comprimir projeto
Compress-Archive -Path * -DestinationPath gestao_ti.zip

# Transferir para o servidor (substitua IP e usuário)
scp gestao_ti.zip usuario@IP_SERVIDOR:/tmp/
```

**Opção B: Via WinSCP/FileZilla**
- Usar WinSCP ou FileZilla para transferir todos os arquivos
- Destino: `/tmp/gestao_ti/`

#### 2. No Servidor Linux

```bash
# Conectar via SSH
ssh usuario@IP_SERVIDOR

# Descompactar arquivos (se usou ZIP)
cd /tmp
unzip gestao_ti.zip -d gestao_ti
cd gestao_ti

# Ou se transferiu direto
cd /tmp/gestao_ti

# Dar permissão de execução ao script
chmod +x deploy_producao.sh

# Executar script de instalação
sudo bash deploy_producao.sh
```

#### 3. Durante a Instalação

O script irá solicitar:

1. **Diretório de instalação** (padrão: `/var/www/gestao_ti`)
2. **Domínio** (ex: `gestao.empresa.com.br`) ou IP do servidor
3. **Nome do banco de dados** (padrão: `gestao_ti_prod`)
4. **Usuário do banco** (padrão: `gestao_user`)
5. **Senha do banco** (criar uma senha forte)
6. **Senha root do MySQL** (usar a senha do root)
7. **Configurar email?** (opcional - s/n)
8. **Configurar SSL?** (recomendado - s/n)

#### 4. Após a Instalação

```bash
# Verificar status dos serviços
sudo systemctl status gestao_ti
sudo systemctl status nginx

# Ver logs em tempo real
sudo journalctl -u gestao_ti -f

# Acessar o sistema
# http://SEU_DOMINIO ou https://SEU_DOMINIO (se configurou SSL)
```

## 📋 O que o Script Faz Automaticamente

✅ Atualiza o sistema operacional  
✅ Instala Python 3, MySQL, Nginx e dependências  
✅ Cria e configura banco de dados MySQL  
✅ Configura ambiente virtual Python  
✅ Instala todas as dependências do projeto  
✅ Cria arquivo `.env` com configurações de produção  
✅ Gera SECRET_KEY segura automaticamente  
✅ Executa migrações do Django  
✅ Coleta arquivos estáticos  
✅ Configura Gunicorn como serviço systemd  
✅ Configura Nginx como proxy reverso  
✅ Configura firewall (UFW)  
✅ Opcionalmente configura SSL com Let's Encrypt  
✅ Ajusta permissões de arquivos  
✅ Configura backup automático diário  
✅ Popular dados iniciais (se disponível)

## 🔧 Ajustes Pós-Instalação

### 1. Revisar settings.py

```bash
sudo nano /var/www/gestao_ti/gestaoTi/settings.py
```

Verificar se estas configurações estão corretas:
- `ALLOWED_HOSTS` (pode precisar adicionar mais domínios)
- `STATIC_ROOT` e `MEDIA_ROOT`
- Configurações específicas do Firebird (se aplicável)

### 2. Configurar Firebird (se necessário)

```bash
# Editar arquivo de configuração do Firebird
sudo nano /var/www/gestao_ti/importacoes/firebird_utils.py
```

Ajustar parâmetros de conexão conforme seu ambiente.

### 3. Testar o Sistema

- Acessar a página inicial
- Fazer login com superusuário
- Testar cada módulo:
  - Cadastros
  - Financeiro
  - Contas a Receber
  - Boletos
  - Importações

## 📊 Monitoramento

### Ver Logs

```bash
# Logs da aplicação
sudo journalctl -u gestao_ti -f

# Logs do Nginx
sudo tail -f /var/log/nginx/gestao_ti_access.log
sudo tail -f /var/log/nginx/gestao_ti_error.log

# Logs de backup
sudo tail -f /var/log/gestao_ti_backup.log
```

### Status dos Serviços

```bash
# Status geral
sudo systemctl status gestao_ti
sudo systemctl status nginx
sudo systemctl status mysql

# Reiniciar serviços
sudo systemctl restart gestao_ti
sudo systemctl restart nginx
```

## 🔄 Atualizações Futuras

```bash
# 1. Parar aplicação
sudo systemctl stop gestao_ti

# 2. Navegar até o diretório
cd /var/www/gestao_ti

# 3. Ativar ambiente virtual
source venv/bin/activate

# 4. Fazer backup
sudo /usr/local/bin/backup_gestao_ti.sh

# 5. Atualizar arquivos (transferir novos arquivos via SCP)

# 6. Instalar novas dependências
pip install -r requirements.txt

# 7. Executar migrações
python manage.py migrate

# 8. Coletar estáticos
python manage.py collectstatic --noinput

# 9. Reiniciar aplicação
sudo systemctl start gestao_ti
```

## 🆘 Resolução de Problemas

### Erro 502 Bad Gateway

```bash
# Verificar se Gunicorn está rodando
sudo systemctl status gestao_ti

# Ver logs de erro
sudo journalctl -u gestao_ti -n 50

# Reiniciar serviço
sudo systemctl restart gestao_ti
```

### Arquivos estáticos não carregam

```bash
cd /var/www/gestao_ti
source venv/bin/activate
python manage.py collectstatic --noinput
sudo systemctl restart nginx
```

### Erro de conexão com banco de dados

```bash
# Testar conexão MySQL
mysql -u gestao_user -p gestao_ti_prod

# Verificar credenciais no .env
sudo cat /var/www/gestao_ti/.env

# Verificar se MySQL está rodando
sudo systemctl status mysql
```

### Permissões negadas

```bash
# Ajustar permissões
sudo chown -R www-data:www-data /var/www/gestao_ti
sudo chmod -R 755 /var/www/gestao_ti
sudo chmod -R 775 /var/www/gestao_ti/media
sudo chmod -R 775 /var/www/gestao_ti/staticfiles
```

## 📞 Informações Importantes

### Arquivos de Configuração

- **Aplicação**: `/var/www/gestao_ti/`
- **Ambiente**: `/var/www/gestao_ti/.env`
- **Gunicorn**: `/etc/systemd/system/gestao_ti.service`
- **Nginx**: `/etc/nginx/sites-available/gestao_ti`
- **Backup**: `/usr/local/bin/backup_gestao_ti.sh`

### Backups

- **Local**: `/var/backups/gestao_ti/`
- **Frequência**: Diário às 02:00
- **Retenção**: 30 dias
- **Manual**: `sudo /usr/local/bin/backup_gestao_ti.sh`

### Portas Utilizadas

- **HTTP**: 80
- **HTTPS**: 443 (se SSL configurado)
- **MySQL**: 3306 (localhost apenas)

## 🔒 Segurança

### Checklist de Segurança

- [ ] `DEBUG=False` no .env
- [ ] `SECRET_KEY` única e forte
- [ ] Senha forte do banco de dados
- [ ] Firewall (UFW) ativo
- [ ] SSL/HTTPS configurado
- [ ] Permissões de arquivo corretas
- [ ] Backup automático funcionando
- [ ] `.env` protegido (chmod 600)

### Fortalecer Segurança

```bash
# Instalar fail2ban
sudo apt install fail2ban

# Configurar fail2ban para SSH
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Desabilitar login root via SSH
sudo nano /etc/ssh/sshd_config
# Alterar: PermitRootLogin no
sudo systemctl restart sshd
```

## 📚 Recursos Adicionais

- Documentação completa: [ROTEIRO_PRODUCAO.md](ROTEIRO_PRODUCAO.md)
- Informações da instalação: `/var/www/gestao_ti/INSTALACAO_INFO.txt`
- Django Docs: https://docs.djangoproject.com/
- Nginx Docs: https://nginx.org/en/docs/

---

**Data**: Janeiro 2026  
**Versão**: 1.0  
**Suporte**: Consultar documentação ou logs do sistema
