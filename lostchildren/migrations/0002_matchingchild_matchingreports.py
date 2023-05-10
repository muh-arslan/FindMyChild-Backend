# Generated by Django 4.1.7 on 2023-05-10 06:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("lostchildren", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="MatchingChild",
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
                ("distance", models.FloatField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "recievedChild",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="match",
                        to="lostchildren.foundchild",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="MatchingReports",
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
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "Reports",
                    models.ManyToManyField(
                        related_name="matches", to="lostchildren.matchingchild"
                    ),
                ),
                (
                    "lostChild",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="matchingReports",
                        to="lostchildren.lostchild",
                    ),
                ),
            ],
        ),
    ]
