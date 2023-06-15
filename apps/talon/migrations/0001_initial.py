# Generated by Django 4.1.7 on 2023-06-15 16:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("operators", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="CallCustomerTask",
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
                ("enabled", models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name="Ticket",
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
                ("number", models.CharField(max_length=1000, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("is_veteran", models.BooleanField(default=False)),
                ("failed_attempts", models.PositiveIntegerField(default=0)),
                ("status", models.CharField(max_length=255)),
                ("status_signal", models.BooleanField(default=False)),
                (
                    "operator",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="operators.operator",
                    ),
                ),
            ],
            options={
                "ordering": ["id"],
            },
        ),
        migrations.CreateModel(
            name="TicketHistory",
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
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("completed", "Обслужен"),
                            ("cancelled", "Не обслужен"),
                        ],
                        max_length=255,
                    ),
                ),
                ("completed_at", models.DateTimeField(auto_now_add=True)),
                (
                    "ticket",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="talon.ticket",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="TicketArchive",
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
                ("number", models.CharField(max_length=1000)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("is_veteran", models.BooleanField(default=False)),
                ("failed_attempts", models.PositiveIntegerField(default=0)),
                ("status", models.CharField(default="Не подошел", max_length=255)),
                ("status_signal", models.BooleanField(default=True)),
                (
                    "operator",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="operators.operator",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="OutherTalon",
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
                ("number", models.CharField(max_length=1000)),
                ("start_time", models.DateTimeField(blank=True)),
                ("end_time", models.DateTimeField(blank=True, null=True)),
                ("is_completed", models.BooleanField(default=False)),
                (
                    "operator",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="operators.operator",
                    ),
                ),
            ],
        ),
    ]
