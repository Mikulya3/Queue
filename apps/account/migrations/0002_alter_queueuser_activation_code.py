# Generated by Django 4.2.2 on 2023-06-07 19:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='queueuser',
            name='activation_code',
            field=models.CharField(blank=True, max_length=40),
        ),
    ]
