# Generated by Django 5.1.1 on 2024-09-25 20:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0004_rename_nombre_plan_escuela_nombre_escuela'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alumno',
            name='id',
            field=models.CharField(max_length=10, primary_key=True, serialize=False),
        ),
    ]