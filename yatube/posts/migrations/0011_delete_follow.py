# Generated by Django 2.2.16 on 2022-11-22 20:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0010_follow'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Follow',
        ),
    ]
