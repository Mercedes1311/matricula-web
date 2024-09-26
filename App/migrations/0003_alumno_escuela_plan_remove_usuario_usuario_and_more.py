# Generated by Django 5.1.1 on 2024-09-25 20:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0002_alter_usuario_password_alter_usuario_usuario'),
    ]

    operations = [
        migrations.CreateModel(
            name='Alumno',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nombres', models.CharField(max_length=100)),
                ('apellido_paterno', models.CharField(max_length=100)),
                ('apellido_materno', models.CharField(max_length=100)),
                ('dni', models.IntegerField(max_length=8)),
                ('correo', models.EmailField(max_length=100)),
                ('celular', models.IntegerField(max_length=9)),
            ],
        ),
        migrations.CreateModel(
            name='Escuela',
            fields=[
                ('id_escuela', models.AutoField(primary_key=True, serialize=False)),
                ('nombre_plan', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('id_plan', models.AutoField(primary_key=True, serialize=False)),
                ('nombre_plan', models.CharField(max_length=100)),
            ],
        ),
        migrations.RemoveField(
            model_name='usuario',
            name='usuario',
        ),
        migrations.AlterField(
            model_name='usuario',
            name='password',
            field=models.CharField(max_length=128, verbose_name='password'),
        ),
        migrations.AddField(
            model_name='usuario',
            name='alumno',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='App.alumno'),
        ),
        migrations.AddField(
            model_name='alumno',
            name='escuela',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='App.escuela'),
        ),
        migrations.AddField(
            model_name='alumno',
            name='plan',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='App.plan'),
        ),
    ]
