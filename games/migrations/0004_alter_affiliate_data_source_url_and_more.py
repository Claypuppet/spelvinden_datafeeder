# Generated by Django 4.2.16 on 2024-11-06 12:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0003_remove_game_stock'),
    ]

    operations = [
        migrations.AlterField(
            model_name='affiliate',
            name='data_source_url',
            field=models.URLField(max_length=1000),
        ),
        migrations.AlterField(
            model_name='affiliategame',
            name='image',
            field=models.URLField(blank=True, default='', max_length=800),
        ),
        migrations.AlterField(
            model_name='affiliategame',
            name='link',
            field=models.URLField(blank=True, default='', max_length=800),
        ),
    ]
