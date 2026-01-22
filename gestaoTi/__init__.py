# Patch para usar PyMySQL ao invés de mysqlclient
import pymysql
pymysql.install_as_MySQLdb()

# Corrigir versão reportada do PyMySQL para compatibilidade com Django
pymysql.version_info = (2, 2, 1, "final", 0)
