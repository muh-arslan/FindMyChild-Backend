# Generated by Django 4.1.7 on 2023-05-10 06:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("lostchildren", "0003_rename_recievedchild_matchingchild_recieved_child"),
    ]

    operations = [
        migrations.RenameField(
            model_name="matchingreports",
            old_name="Reports",
            new_name="reports",
        ),
    ]
