# Generated by Django 5.0.6 on 2024-08-29 19:05

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Medico', '0007_resumen_fecha_nacimiento_resumen_genero'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Comentario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comentario', models.TextField()),
                ('fecha_de_creacion', models.DateTimeField(auto_now_add=True)),
                ('resumen', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comentarios', to='Medico.resumen')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]