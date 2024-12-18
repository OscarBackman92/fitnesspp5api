# Generated by Django 5.1.2 on 2024-12-18 22:02

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_alter_userprofile_bio_alter_userprofile_height_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='height',
            field=models.FloatField(blank=True, default=0.0, null=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='weight',
            field=models.FloatField(blank=True, default=0.0, null=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]
