# Generated by Django 5.0 on 2023-12-14 07:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Country",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("region", models.CharField(max_length=200)),
                ("name", models.CharField(max_length=200, unique=True)),
                ("code", models.CharField(max_length=2)),
                ("flag", models.CharField(max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name="Game",
            fields=[
                ("info_timestamp", models.DateTimeField()),
                ("info_modified_timestamp", models.DateTimeField()),
                ("id", models.IntegerField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=200)),
                ("image", models.CharField(blank=True, max_length=200, null=True)),
                ("description", models.TextField(blank=True, null=True)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Genre",
            fields=[
                ("id", models.IntegerField(primary_key=True, serialize=False)),
                ("genre", models.CharField(max_length=200, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name="LastScrape",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("datetime", models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name="Platform",
            fields=[
                ("id", models.IntegerField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=200, unique=True)),
                ("imported", models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name="GamePlatform",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("game", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="games.game")),
                ("platform", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="games.platform")),
            ],
        ),
        migrations.CreateModel(
            name="GamePlatformCountry",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("country", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="games.country")),
                (
                    "game_platform",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="games.gameplatform"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="GameGenre",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("game", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="games.game")),
                ("genre", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="games.genre")),
            ],
        ),
    ]