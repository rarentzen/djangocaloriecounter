# Generated by Django 3.1.7 on 2021-05-07 13:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_auto_20210322_2138'),
    ]

    operations = [
        migrations.AlterField(
            model_name='consumedfood',
            name='date_time',
            field=models.DateField(auto_now_add=True),
        ),
    ]
