# Generated by Django 5.1.7 on 2025-03-20 22:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('policies', '0009_alter_policy_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='policy',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to='policies/files/'),
        ),
    ]
