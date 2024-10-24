# Generated by Django 5.1.2 on 2024-10-20 17:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_alter_workout_options_userprofile_created_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='gender',
            field=models.CharField(blank=True, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='workout',
            name='intensity',
            field=models.CharField(choices=[('low', 'Low'), ('moderate', 'Moderate'), ('high', 'High')], default='moderate', max_length=20),
        ),
    ]
