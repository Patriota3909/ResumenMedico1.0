# Generated by Django 5.0.6 on 2024-06-19 16:23

import django_summernote.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Medico', '0002_alter_resumen_medico_adscrito_alter_resumen_texto_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='MyModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('content', django_summernote.fields.SummernoteTextField()),
            ],
        ),
    ]
