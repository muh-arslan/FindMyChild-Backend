# Generated by Django 4.1.7 on 2023-04-02 14:08

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("lostchildren", "0005_foundchild"),
    ]

    operations = [
        migrations.AlterField(
            model_name="foundchild",
            name="province",
            field=models.CharField(
                choices=[
                    ("AJK", "Azad Jammu and Kashmir"),
                    ("Bal", "Balochistan"),
                    ("GB", "Gilgit Baltistan"),
                    ("KP", "Khyber Pakhtunkhwa"),
                    ("Pun", "Punjab"),
                    ("Snd", "Sindh"),
                ],
                max_length=18,
                null=True,
            ),
        ),
    ]