# Generated by Django 4.2.15 on 2024-08-21 11:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0003_review'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='rating',
            field=models.IntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)]),
        ),
    ]
