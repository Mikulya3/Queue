# Generated by Django 4.1.7 on 2023-06-16 13:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Bank",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("address", models.CharField(max_length=200)),
                ("contact_number", models.CharField(max_length=15)),
                ("email", models.EmailField(max_length=254)),
                ("established_date", models.DateField()),
                ("description", models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name="Branch",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("address", models.CharField(max_length=200)),
                ("contact_number", models.CharField(max_length=15)),
                ("email", models.EmailField(max_length=254)),
                ("branch_director_name", models.CharField(max_length=100)),
                ("branch_director_name_number", models.CharField(max_length=15)),
                ("status", models.CharField(max_length=50)),
                ("opening_time", models.TimeField()),
                ("closing_time", models.TimeField()),
                ("description", models.TextField()),
                (
                    "bank",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="bank.bank"
                    ),
                ),
            ],
        ),
    ]
