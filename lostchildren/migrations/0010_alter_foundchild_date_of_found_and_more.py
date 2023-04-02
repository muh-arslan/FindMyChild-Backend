# Generated by Django 4.1.7 on 2023-04-02 14:49

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("lostchildren", "0009_alter_foundchild_date_of_found_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="foundchild",
            name="date_of_found",
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name="lostchild",
            name="date_of_lost",
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]