# Generated by Django 5.1.5 on 2025-02-06 12:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rooms", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="room",
            name="tags",
            field=models.ManyToManyField(blank=True, null=True, to="rooms.tag"),
        ),
    ]
