# Generated by Django 4.2 on 2023-05-12 20:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='pricetypes',
            options={'ordering': ('price',), 'verbose_name': 'Тип цен', 'verbose_name_plural': 'Типы цен'},
        ),
        migrations.AlterField(
            model_name='berths',
            name='berths',
            field=models.CharField(blank=True, max_length=100, null=True, unique=True, verbose_name='Причал'),
        ),
    ]
