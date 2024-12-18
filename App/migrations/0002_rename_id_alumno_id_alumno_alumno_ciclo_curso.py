# Generated by Django 5.1.1 on 2024-10-02 14:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='alumno',
            old_name='id',
            new_name='id_alumno',
        ),
        migrations.AddField(
            model_name='alumno',
            name='ciclo',
            field=models.IntegerField(default=1),
        ),
        migrations.CreateModel(
            name='Curso',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('codigo', models.CharField(max_length=10)),
                ('nombre_curso', models.CharField(max_length=100)),
                ('creditos', models.IntegerField()),
                ('turno', models.CharField(choices=[('M', 'M'), ('T', 'T'), ('N', 'N')], max_length=1)),
                ('seccion', models.CharField(choices=[('A', 'A'), ('B', 'B'), ('C', 'C')], max_length=1)),
                ('prerrequisito', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cursos_dependientes', to='App.curso')),
            ],
        ),
    ]
