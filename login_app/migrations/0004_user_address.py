# Generated by Django 4.1.7 on 2023-05-20 11:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("login_app", "0003_alter_orgdetails_city_alter_orgdetails_latitude_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="address",
            field=models.TextField(blank=True, null=True),
        ),
    ]