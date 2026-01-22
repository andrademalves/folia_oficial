#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de Automação para Configuração de Ambiente de Produção Django
Autor: DevOps Automation  
Data: 2026-01-11
Versão: FINAL
"""

import os
import sys
import subprocess
import re
import platform
from datetime import datetime
from pathlib import Path

# ============================================================================
# CONFIGURAÇÕES GLOBAIS
# ============================================================================
PROJECT_DIR = r"C:\1.3 Gestao"
DB_PASSWORD = "F0li@2026!"
LOG_FILE = os.path.join(PROJECT_DIR, f"setup_log_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.txt")

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def log_message(message, is_error=False):
    """Registra mensagens no console e no arquivo de log"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    prefix = "[ERRO]" if is_error else "[INFO]"
    full_message = f"{timestamp} {prefix} {message}"
    
    # Printar no console com encoding seguro
    try:
        print(full_message)
    except UnicodeEncodeError:
        # Fallback para ASCII se houver problemas de encoding
        print(full_message.encode('ascii', 'replace').decode('ascii'))
    
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(full_message + "\n")


def run_command(command, description, critical=True, shell=False, timeout=300):
    """Executa um comando e registra o resultado"""
    log_message(f"Executando: {description}")
    log_message(f"Comando: {' '.join(command) if isinstance(command, list) else command}")
    
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            shell=shell,
            cwd=PROJECT_DIR,
            timeout=timeout
        )
        
        if result.returncode == 0:
            log_message(f"[OK] Sucesso: {description}")
            if result.stdout:
                log_message(f"Output: {result.stdout[:500]}")
            return True
        else:
            error_msg = f"Falha: {description}\nErro: {result.stderr}"
            log_message(error_msg, is_error=True)
            if critical:
                raise Exception(error_msg)
            return False
            
    except subprocess.TimeoutExpired:
        error_msg = f"Timeout ao executar {description} (>{timeout}s)"
        log_message(error_msg, is_error=True)
        if critical:
            raise Exception(error_msg)
        return False
    except Exception as e:
        error_msg = f"Exceção ao executar {description}: {str(e)}"
        log_message(error_msg, is_error=True)
        if critical:
            raise
        return False


def find_settings_file():
    """Busca o arquivo settings.py no projeto"""
    # Busca recursiva
    for root, dirs, files in os.walk(PROJECT_DIR):
        if 'settings.py' in files and 'venv' not in root and '__pycache__' not in root:
            return os.path.join(root, 'settings.py')
    
    return None


# ============================================================================
# ETAPAS DE CONFIGURAÇÃO
# ============================================================================

def step_1_verify_directory():
    """Etapa 1: Verificar e mudar para o diretório do projeto"""
    log_message("=" * 80)
    log_message("ETAPA 1: Verificação do Diretório do Projeto")
    log_message("=" * 80)
    
    if not os.path.exists(PROJECT_DIR):
        log_message(f"ERRO FATAL: Diretório {PROJECT_DIR} não encontrado!", is_error=True)
        sys.exit(1)
    
    os.chdir(PROJECT_DIR)
    log_message(f"Diretório de trabalho alterado para: {os.getcwd()}")
    

def step_2_verify_files():
    """Etapa 2: Verificar arquivos críticos"""
    log_message("=" * 80)
    log_message("ETAPA 2: Verificação de Arquivos Críticos")
    log_message("=" * 80)
    
    critical_files = {
        'manage.py': os.path.join(PROJECT_DIR, 'manage.py'),
        'requirements.txt': os.path.join(PROJECT_DIR, 'requirements.txt')
    }
    
    missing_files = []
    
    for name, path in critical_files.items():
        if os.path.exists(path):
            log_message(f"[OK] Arquivo encontrado: {name}")
        else:
            missing_files.append(name)
            log_message(f"[X] Arquivo NAO encontrado: {name}", is_error=True)
    
    # Verificar settings.py
    settings_path = find_settings_file()
    if settings_path:
        log_message(f"[OK] settings.py encontrado em: {settings_path}")
    else:
        missing_files.append('settings.py')
        log_message("[X] settings.py NAO encontrado!", is_error=True)
    
    if missing_files:
        log_message(f"ERRO FATAL: Arquivos críticos ausentes: {', '.join(missing_files)}", is_error=True)
        sys.exit(1)
    
    return settings_path


def step_3_setup_venv():
    """Etapa 3: Configurar ambiente virtual"""
    log_message("=" * 80)
    log_message("ETAPA 3: Configuração do Ambiente Virtual")
    log_message("=" * 80)
    
    venv_dir = os.path.join(PROJECT_DIR, 'venv')
    
    # Identificar executáveis da venv
    if platform.system() == 'Windows':
        python_venv = os.path.join(venv_dir, 'Scripts', 'python.exe')
        pip_venv = os.path.join(venv_dir, 'Scripts', 'pip.exe')
    else:
        python_venv = os.path.join(venv_dir, 'bin', 'python')
        pip_venv = os.path.join(venv_dir, 'bin', 'pip')
    
    # Verificar se a venv existe e está funcional
    venv_is_valid = False
    if os.path.exists(venv_dir):
        log_message("Ambiente virtual encontrado. Verificando integridade...")
        # Testar se o python da venv funciona
        try:
            result = subprocess.run(
                [python_venv, '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                log_message(f"[OK] Ambiente virtual está funcional: {result.stdout.strip()}")
                venv_is_valid = True
            else:
                log_message("[X] Ambiente virtual está corrompido.", is_error=True)
        except Exception as e:
            log_message(f"[X] Ambiente virtual está corrompido: {str(e)}", is_error=True)
    
    # Recriar venv se não existir ou estiver corrompida
    if not venv_is_valid:
        if os.path.exists(venv_dir):
            log_message("Removendo ambiente virtual corrompido...")
            import shutil
            try:
                shutil.rmtree(venv_dir)
                log_message("[OK] Ambiente virtual antigo removido.")
            except Exception as e:
                log_message(f"Erro ao remover venv: {str(e)}", is_error=True)
        
        log_message("Criando novo ambiente virtual...")
        run_command(
            [sys.executable, '-m', 'venv', 'venv'],
            "Criar ambiente virtual",
            critical=True
        )
    
    if not os.path.exists(python_venv):
        log_message(f"ERRO: Python da venv não encontrado em {python_venv}", is_error=True)
        sys.exit(1)
    
    log_message(f"Python da venv: {python_venv}")
    log_message(f"Pip da venv: {pip_venv}")
    
    return python_venv, pip_venv


def step_4_install_dependencies(python_venv):
    """Etapa 4: Instalar dependências"""
    log_message("=" * 80)
    log_message("ETAPA 4: Instalação de Dependências")
    log_message("=" * 80)
    
    # Atualizar pip
    run_command(
        [python_venv, '-m', 'pip', 'install', '--upgrade', 'pip'],
        "Atualizar pip",
        critical=False
    )
    
    # Instalar Django
    run_command(
        [python_venv, '-m', 'pip', 'install', 'django'],
        "Instalar Django",
        critical=False
    )
    
    # Desinstalar mysqlclient se existir e instalar PyMySQL (melhor para Windows)
    log_message("Configurando driver MySQL (PyMySQL para compatibilidade Windows)...")
    run_command(
        [python_venv, '-m', 'pip', 'uninstall', '-y', 'mysqlclient'],
        "Desinstalar mysqlclient (se existir)",
        critical=False
    )
    
    run_command(
        [python_venv, '-m', 'pip', 'install', 'pymysql'],
        "Instalar PyMySQL",
        critical=True
    )
    
    # Instalar requirements.txt
    requirements_file = os.path.join(PROJECT_DIR, 'requirements.txt')
    if os.path.exists(requirements_file):
        run_command(
            [python_venv, '-m', 'pip', 'install', '-r', requirements_file],
            "Instalar requirements.txt",
            critical=False,
            timeout=600  # 10 minutos para instalação completa
        )


def step_5_configure_pymysql_patches():
    """Etapa 5: Configurar patches do PyMySQL"""
    log_message("=" * 80)
    log_message("ETAPA 5: Configuração de Patches PyMySQL")
    log_message("=" * 80)
    
    # Patch 1: manage.py
    manage_py_path = os.path.join(PROJECT_DIR, 'manage.py')
    with open(manage_py_path, 'r', encoding='utf-8') as f:
        manage_content = f.read()
    
    if 'pymysql.install_as_MySQLdb()' not in manage_content:
        # Adicionar após imports
        lines = manage_content.split('\n')
        # Encontrar a linha do import sys
        for i, line in enumerate(lines):
            if 'import sys' in line:
                lines.insert(i + 1, '')
                lines.insert(i + 2, '# Patch para usar PyMySQL ao invés de mysqlclient')
                lines.insert(i + 3, 'import pymysql')
                lines.insert(i + 4, 'pymysql.install_as_MySQLdb()')
                break
        
        with open(manage_py_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        log_message("[OK] Patch do PyMySQL adicionado ao manage.py")
    else:
        log_message("[OK] Patch do PyMySQL já existe no manage.py")
    
    # Patch 2: __init__.py do projeto
    settings_dir = os.path.dirname(find_settings_file())
    init_path = os.path.join(settings_dir, '__init__.py')
    
    pymysql_patch = """# Patch para usar PyMySQL ao invés de mysqlclient
import pymysql
pymysql.install_as_MySQLdb()

# Corrigir versão reportada do PyMySQL para compatibilidade com Django
pymysql.version_info = (2, 2, 1, "final", 0)
"""
    
    if os.path.exists(init_path):
        with open(init_path, 'r', encoding='utf-8') as f:
            init_content = f.read()
        
        if 'pymysql.install_as_MySQLdb()' not in init_content:
            with open(init_path, 'w', encoding='utf-8') as f:
                f.write(pymysql_patch + '\n' + init_content)
            log_message(f"[OK] Patch do PyMySQL adicionado ao {init_path}")
        else:
            log_message(f"[OK] Patch do PyMySQL já existe no {init_path}")
    else:
        with open(init_path, 'w', encoding='utf-8') as f:
            f.write(pymysql_patch)
        log_message(f"[OK] Arquivo {init_path} criado com patch do PyMySQL")


def step_6_configure_database(settings_path):
    """Etapa 6: Configurar banco de dados"""
    log_message("=" * 80)
    log_message("ETAPA 6: Configuração do Banco de Dados")
    log_message("=" * 80)
    
    # Ler settings.py
    with open(settings_path, 'r', encoding='utf-8') as f:
        settings_content = f.read()
    
    # Extrair nome do banco
    db_name_match = re.search(r"'NAME'\s*:\s*['\"]([^'\"]+)['\"]", settings_content)
    if db_name_match:
        db_name = db_name_match.group(1)
        log_message(f"Nome do banco de dados identificado: {db_name}")
    else:
        db_name = "gestao_ti"
        log_message(f"Nome do banco não encontrado. Usando padrão: {db_name}", is_error=True)
    
    # Alterar senha no settings.py
    log_message("Atualizando senha do banco de dados no settings.py...")
    
    # Padrão para encontrar a configuração de PASSWORD
    password_pattern = r"('PASSWORD'\s*:\s*['\"])([^'\"]*?)(['\"])"
    
    if re.search(password_pattern, settings_content):
        new_settings_content = re.sub(
            password_pattern,
            rf"\g<1>{DB_PASSWORD}\g<3>",
            settings_content
        )
        
        # Salvar arquivo modificado
        backup_path = settings_path + '.backup_setup'
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(settings_content)
        log_message(f"Backup do settings.py criado em: {backup_path}")
        
        with open(settings_path, 'w', encoding='utf-8') as f:
            f.write(new_settings_content)
        log_message("[OK] Senha do banco atualizada no settings.py")
    else:
        log_message("Aviso: Padrão de PASSWORD não encontrado em settings.py", is_error=True)
    
    # Verificar/adicionar STATIC_ROOT
    if 'STATIC_ROOT' not in settings_content:
        log_message("Adicionando STATIC_ROOT ao settings.py...")
        # Adicionar após STATIC_URL
        new_settings_content = re.sub(
            r"(STATIC_URL\s*=\s*['\"][^'\"]+['\"])",
            r"\1\nSTATIC_ROOT = BASE_DIR / 'staticfiles'",
            new_settings_content if 'new_settings_content' in locals() else settings_content
        )
        with open(settings_path, 'w', encoding='utf-8') as f:
            f.write(new_settings_content)
        log_message("[OK] STATIC_ROOT adicionado ao settings.py")
    
    # Criar banco de dados MySQL
    log_message(f"Criando banco de dados: {db_name}")
    
    # Tentar criar o banco
    mysql_commands = [
        f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    ]
    
    # Tentar múltiplos caminhos do MySQL
    mysql_paths = [
        'mysql',  # No PATH
        r'C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe',
        r'C:\Program Files\MySQL\MySQL Server 5.7\bin\mysql.exe',
        r'C:\xampp\mysql\bin\mysql.exe',
    ]
    
    mysql_success = False
    for mysql_path in mysql_paths:
        try:
            cmd = [
                mysql_path,
                '-u', 'root',
                f'--password={DB_PASSWORD}',
                '-e', mysql_commands[0]
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=PROJECT_DIR,
                timeout=10
            )
            
            if result.returncode == 0:
                log_message(f"[OK] Banco de dados {db_name} criado/verificado com sucesso (UTF-8 Brasil)")
                mysql_success = True
                break
            elif 'Access denied' in result.stderr:
                log_message(f"Erro de autenticação MySQL. Verifique a senha.", is_error=True)
            else:
                log_message(f"Tentativa com {mysql_path} falhou: {result.stderr}", is_error=True)
                
        except FileNotFoundError:
            continue
        except Exception as e:
            log_message(f"Erro ao tentar {mysql_path}: {str(e)}", is_error=True)
            continue
    
    if not mysql_success:
        log_message(
            "AVISO: Não foi possível criar o banco automaticamente. "
            "Você precisará criá-lo manualmente com o comando:\n"
            f"CREATE DATABASE {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
            is_error=True
        )
    
    return db_name


def step_7_django_setup(python_venv):
    """Etapa 7: Executar comandos Django"""
    log_message("=" * 80)
    log_message("ETAPA 7: Setup do Django")
    log_message("=" * 80)
    
    manage_py = os.path.join(PROJECT_DIR, 'manage.py')
    
    # makemigrations
    run_command(
        [python_venv, manage_py, 'makemigrations'],
        "Django makemigrations",
        critical=False
    )
    
    # migrate
    run_command(
        [python_venv, manage_py, 'migrate'],
        "Django migrate",
        critical=True,
        timeout=600  # 10 minutos para migrations complexas
    )
    
    # collectstatic
    run_command(
        [python_venv, manage_py, 'collectstatic', '--noinput'],
        "Django collectstatic",
        critical=False
    )


def step_8_final_tests(python_venv):
    """Etapa 8: Testes finais"""
    log_message("=" * 80)
    log_message("ETAPA 8: Testes Finais")
    log_message("=" * 80)
    
    manage_py = os.path.join(PROJECT_DIR, 'manage.py')
    
    # Django check
    run_command(
        [python_venv, manage_py, 'check'],
        "Django check (system)",
        critical=False
    )


# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def main():
    """Função principal de execução"""
    print("\n" + "=" * 80)
    print(" SCRIPT DE AUTOMACAO - CONFIGURACAO DE AMBIENTE DE PRODUCAO DJANGO")
    print("=" * 80 + "\n")
    
    log_message("Iniciando processo de configuração...")
    log_message(f"Sistema Operacional: {platform.system()} {platform.release()}")
    log_message(f"Python Global: {sys.version}")
    
    try:
        # Executar etapas sequencialmente
        step_1_verify_directory()
        settings_path = step_2_verify_files()
        python_venv, pip_venv = step_3_setup_venv()
        step_4_install_dependencies(python_venv)
        step_5_configure_pymysql_patches()
        step_6_configure_database(settings_path)
        step_7_django_setup(python_venv)
        step_8_final_tests(python_venv)
        
        # Sucesso
        log_message("=" * 80)
        log_message("[OK][OK][OK] CONFIGURACAO CONCLUIDA COM SUCESSO! [OK][OK][OK]")
        log_message("=" * 80)
        log_message(f"Log completo salvo em: {LOG_FILE}")
        log_message("\nProximos passos:")
        log_message("1. Verifique o arquivo de log para avisos")
        log_message("2. Configure variaveis de ambiente de producao (DEBUG=False, SECRET_KEY, etc.)")
        log_message("3. Configure o servidor web (Gunicorn/Nginx ou IIS)")
        log_message(f"4. Para iniciar o servidor de desenvolvimento: venv\\Scripts\\python.exe manage.py runserver")
        log_message("\nAmbiente configurado com sucesso!")
        print("\n[OK] Setup completo! Verifique o log para detalhes.\n")
        
    except Exception as e:
        log_message("=" * 80, is_error=True)
        log_message("[X][X][X] ERRO FATAL - CONFIGURACAO INTERROMPIDA [X][X][X]", is_error=True)
        log_message("=" * 80, is_error=True)
        log_message(f"Erro: {str(e)}", is_error=True)
        log_message(f"Verifique o log completo em: {LOG_FILE}", is_error=True)
        print(f"\n[X] Erro durante setup. Verifique: {LOG_FILE}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
