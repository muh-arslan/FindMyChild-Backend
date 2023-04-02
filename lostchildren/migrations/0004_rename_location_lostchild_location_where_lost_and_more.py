# Generated by Django 4.1.7 on 2023-04-02 11:32

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("lostchildren", "0003_delete_foundchild"),
    ]

    operations = [
        migrations.RenameField(
            model_name="lostchild",
            old_name="location",
            new_name="location_where_lost",
        ),
        migrations.AddField(
            model_name="lostchild",
            name="city",
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name="lostchild",
            name="gender",
            field=models.CharField(
                choices=[("M", "Male"), ("F", "Female"), ("O", "Other")],
                max_length=1,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="lostchild",
            name="home_address",
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="lostchild",
            name="phone_number",
            field=models.CharField(max_length=11, null=True),
        ),
        migrations.AddField(
            model_name="lostchild",
            name="province",
            field=models.CharField(max_length=50, null=True),
        ),
    ]