# Generated by Django 4.2 on 2023-06-08 20:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0002_terminal_alter_shops_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='terminal',
            name='name',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='terminal',
            name='store_uuid',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='UUID магазина'),
        ),
        migrations.AlterField(
            model_name='terminal',
            name='timezone_offset',
            field=models.IntegerField(blank=True, null=True, verbose_name='Смещение часового пояса'),
        ),
        migrations.AlterField(
            model_name='terminal',
            name='uuid',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='UUID'),
        ),
    ]