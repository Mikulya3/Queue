# Generated by Django 4.2.2 on 2023-06-13 13:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("talon", "0002_ticket_failed_attempts"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="ticket",
            options={"ordering": ["id"]},
        ),
    ]
