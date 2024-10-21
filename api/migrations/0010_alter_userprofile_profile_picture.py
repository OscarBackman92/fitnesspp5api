# Generated by Django 5.1.2 on 2024-10-21 18:33

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_delete_workout'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='profile_picture',
            field=cloudinary.models.CloudinaryField(blank=True, default='default_profile_ylwpgw', max_length=255, null=True, verbose_name='image'),
        ),
    ]
