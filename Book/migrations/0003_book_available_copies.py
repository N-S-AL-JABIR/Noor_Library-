# Generated by Django 5.1.3 on 2025-06-24 13:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Book', '0002_alter_book_cover_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='available_copies',
            field=models.PositiveIntegerField(blank=True, default=0, null=True),
        ),
    ]
