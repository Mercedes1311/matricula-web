# Generated by Django 5.1.1 on 2024-10-02 14:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0003_curso_ciclo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='curso',
            name='prerrequisito',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
