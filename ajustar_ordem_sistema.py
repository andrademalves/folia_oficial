#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestaoTi.settings')
django.setup()

from usuarios.models import Modulo

m = Modulo.objects.get(nome='Sistema')
m.ordem = 6
m.save()
print(f'✓ Ordem do módulo Sistema alterada para {m.ordem}')
print('✓ Agora o módulo aparecerá após Importações')
