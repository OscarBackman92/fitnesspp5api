# Generated by Django 5.1.2 on 2024-10-20 20:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_userprofile_profile_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='profile_picture',
            field=models.ImageField(blank=True, default='default_profile_ylwpgw', upload_to='images'),
        ),
    ]
