# Generated by Django 3.1.3 on 2022-07-06 04:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('friendships', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='friendship',
            options={'ordering': ('-created_at',)},
        ),
    ]