# Generated by Django 4.1.7 on 2023-06-07 12:17

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("notification_app", "0003_feedbackreview"),
    ]

    operations = [
        migrations.AlterField(
            model_name="feedbackreview",
            name="feedback",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="feedbackreview",
            name="rating",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
