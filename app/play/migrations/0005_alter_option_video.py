# Generated by Django 3.2.7 on 2021-09-09 02:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('play', '0004_alter_option_video'),
    ]

    operations = [
        migrations.AlterField(
            model_name='option',
            name='video',
            field=models.FileField(blank=True, upload_to='C:/data/videos'),
        ),
    ]