# Generated by Django 5.1.7 on 2025-03-15 20:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('policies', '0003_alter_policy_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='policy',
            name='category',
            field=models.CharField(choices=[('HR', 'Human Resources'), ('IT', 'Information Technology'), ('Finance', 'Finance'), ('Engineernig', 'Engineering'), ('Private', 'Private Sectors')], max_length=50),
        ),
    ]
