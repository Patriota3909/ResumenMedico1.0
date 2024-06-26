# Generated by Django 5.0.6 on 2024-06-18 21:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Medico', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resumen',
            name='medico_adscrito',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='resumenes_por_adscrito', to='Medico.doctor'),
        ),
        migrations.AlterField(
            model_name='resumen',
            name='texto',
            field=models.TextField(blank=True),
        ),
        migrations.CreateModel(
            name='Asignacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_medico', models.CharField(choices=[('Residente', 'Residente'), ('Becario', 'Becario'), ('Adscrito', 'Adscrito')], max_length=10)),
                ('especialidad', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Medico.especialidad')),
                ('ultimo_medico', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='Medico.doctor')),
            ],
        ),
    ]
