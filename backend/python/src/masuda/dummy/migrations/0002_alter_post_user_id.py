# Generated by Django 3.2.9 on 2022-09-29 09:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dummy', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='user_id',
            field=models.CharField(max_length=200),
        ),
    ]