# Generated by Django 3.2.9 on 2023-06-20 03:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workshop', '0007_auto_20230620_1100'),
    ]

    operations = [
        migrations.AddField(
            model_name='inbox',
            name='WorkshopTitle',
            field=models.CharField(default='', max_length=250, null=True),
        ),
    ]
