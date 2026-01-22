import MySQLdb
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestaoTi.settings')
django.setup()

from django.conf import settings

db = settings.DATABASES['default']
conn = MySQLdb.connect(
    host=db['HOST'],
    user=db['USER'],
    passwd=db['PASSWORD'],
    db=db['NAME']
)

c = conn.cursor()
c.execute('ALTER TABLE boletos_boleto MODIFY COLUMN codigo_barras VARCHAR(100)')
c.execute('ALTER TABLE boletos_boleto MODIFY COLUMN linha_digitavel VARCHAR(100)')
conn.commit()
print('✓ Campos alterados para VARCHAR(100)')
conn.close()
