# Generated by Django 5.1.1 on 2024-10-12 17:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0014_alter_matricula_fecha_matricula'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='matricula',
            name='boucher',
        ),
        migrations.AddField(
            model_name='matricula',
            name='boucher',
            field=models.ManyToManyField(to='App.boucher'),
        ),
    ]
