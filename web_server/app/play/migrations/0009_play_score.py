# Generated by Django 3.2.7 on 2021-09-27 17:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('play', '0008_alter_option_video'),
    ]

    operations = [
        migrations.AddField(
            model_name='play',
            name='score',
            field=models.IntegerField(default=0),
        ),
    ]