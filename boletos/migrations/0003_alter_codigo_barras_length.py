# Generated manually on 2025-12-28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boletos', '0002_configuracaobancaria_conta_financeira_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='boleto',
            name='codigo_barras',
            field=models.CharField(blank=True, max_length=44, verbose_name='Código de Barras'),
        ),
        migrations.AlterField(
            model_name='boleto',
            name='linha_digitavel',
            field=models.CharField(blank=True, max_length=54, verbose_name='Linha Digitável'),
        ),
    ]
