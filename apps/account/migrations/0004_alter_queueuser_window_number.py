# Generated by Django 4.1.7 on 2023-06-14 06:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "account",
            "0003_remove_queueuser_auth_mode_remove_queueuser_blocked_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="queueuser",
            name="window_number",
            field=models.CharField(max_length=100, verbose_name="window number"),
        ),
    ]
