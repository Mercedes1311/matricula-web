# Generated by Django 5.1.1 on 2024-10-09 00:26

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0013_matricula_mensaje_aprobacion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='matricula',
            name='fecha_matricula',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
