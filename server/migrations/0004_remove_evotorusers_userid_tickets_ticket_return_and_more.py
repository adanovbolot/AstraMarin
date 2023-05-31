# Generated by Django 4.2 on 2023-05-31 17:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0003_evotorusers_delete_terminal'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='evotorusers',
            name='userid',
        ),
        migrations.AddField(
            model_name='tickets',
            name='ticket_return',
            field=models.BooleanField(default=False, verbose_name='Возрат билета'),
        ),
        migrations.AlterField(
            model_name='evotorusers',
            name='token',
            field=models.CharField(blank=True, max_length=250, null=True, unique=True, verbose_name='Токен'),
        ),
        migrations.AddField(
            model_name='evotorusers',
            name='userId',
            field=models.CharField(default=1, max_length=100, unique=True, verbose_name='UserID'),
            preserve_default=False,
        ),
    ]