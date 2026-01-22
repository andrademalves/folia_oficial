from django.core.management.base import BaseCommand, CommandError
from django.db import connections
from cadastros.models import PlanoConta

class Command(BaseCommand):
    help = (
        "Importa Plano de Contas de uma tabela existente no mesmo banco (compatível: id, nome, codigo, ativo, pai_id).\n"
        "Por padrão usa a conexão 'default' (gestao_ti).\n"
        "Use --table para especificar a tabela (padrão: plano_contas). Opcionalmente --schema para schema/database." 
    )

    def add_arguments(self, parser):
        parser.add_argument('--table', type=str, default='plano_contas', help='Nome da tabela de origem (default: plano_contas)')
        parser.add_argument('--schema', type=str, default=None, help='Schema/Database opcional (ex.: outro_db)')
        parser.add_argument('--truncate', action='store_true', help='Apaga registros atuais antes de importar')
        parser.add_argument('--batch', type=int, default=1000, help='Tamanho de lote para bulk_create (default: 1000)')

    def handle(self, *args, **options):
        table = options['table']
        schema = options.get('schema')
        batch = options['batch']

        full_table = f"{schema}.{table}" if schema else table

        self.stdout.write(self.style.WARNING(f"Lendo da conexão 'default', tabela '{full_table}'..."))

        try:
            with connections['default'].cursor() as cursor:
                cursor.execute(f"SELECT id, nome, codigo, ativo, pai_id FROM {full_table}")
                rows = cursor.fetchall()
        except Exception as exc:
            raise CommandError(
                f"Falha ao consultar tabela '{full_table}': {exc}.\n"
                "Verifique se a tabela existe no banco 'gestao_ti' e se possui as colunas id, nome, codigo, ativo, pai_id."
            )

        total = len(rows)
        if total == 0:
            self.stdout.write(self.style.WARNING('Nenhuma linha encontrada no Futura.'))
            return

        # Limpa dados se solicitado
        if options['truncate']:
            self.stdout.write(self.style.WARNING('Apagando registros atuais de PlanoConta...'))
            PlanoConta.objects.all().delete()

        self.stdout.write(self.style.SUCCESS(f"Importando {total} registros..."))

        # 1ª fase: insere registros sem pai
        objs = []
        for r in rows:
            # r = (id, nome, codigo, ativo, pai_id)
            id_val, nome, codigo, ativo, pai_id = r
            objs.append(PlanoConta(
                id=id_val,
                nome=nome or '',
                codigo=str(codigo) if codigo is not None else '',
                ativo=bool(ativo) if ativo is not None else True,
                pai=None
            ))

        # bulk em lotes
        created = 0
        for i in range(0, len(objs), batch):
            PlanoConta.objects.bulk_create(objs[i:i+batch], ignore_conflicts=True)
            created += len(objs[i:i+batch])

        self.stdout.write(self.style.SUCCESS(f"Registros inseridos/atualizados: {created}"))

        # 2ª fase: atualiza pai_id
        # Usa um mapa id->pai_id a partir das linhas
        id_to_pai = {int(r[0]): (int(r[4]) if r[4] is not None else None) for r in rows}

        # Atualiza em blocos para evitar N consultas
        to_update = []
        pais_cache = {}
        for rec_id, pai_id in id_to_pai.items():
            if pai_id:
                # cache de parent
                if pai_id not in pais_cache:
                    try:
                        pais_cache[pai_id] = PlanoConta.objects.get(pk=pai_id)
                    except PlanoConta.DoesNotExist:
                        pais_cache[pai_id] = None
                parent = pais_cache[pai_id]
                if parent:
                    to_update.append((rec_id, parent))

        # Executa updates
        updated = 0
        for i in range(0, len(to_update), batch):
            chunk = to_update[i:i+batch]
            ids = [rid for rid, _ in chunk]
            items = {rid: p for rid, p in chunk}
            for pc in PlanoConta.objects.filter(pk__in=ids):
                pc.pai = items.get(pc.id)
                pc.save(update_fields=['pai'])
                updated += 1

        self.stdout.write(self.style.SUCCESS(f"Pais atualizados: {updated}"))
        self.stdout.write(self.style.SUCCESS('Importação concluída com sucesso.'))
