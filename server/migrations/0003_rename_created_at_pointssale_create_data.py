# Generated by Django 4.2 on 2023-05-24 19:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0002_alter_pointssale_created_at'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pointssale',
            old_name='created_at',
            new_name='create_data',
        ),
    ]
