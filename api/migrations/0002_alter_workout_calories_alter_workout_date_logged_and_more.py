# Generated by Django 5.1.2 on 2024-10-15 19:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workout',
            name='calories',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='workout',
            name='date_logged',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='workout',
            name='duration',
            field=models.IntegerField(),
        ),
    ]
