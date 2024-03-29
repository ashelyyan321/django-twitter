# Generated by Django 3.1.3 on 2022-07-26 05:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('friendships', '0003_auto_20220726_0553'),
    ]

    operations = [
        migrations.AlterField(
            model_name='friendship',
            name='from_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='following_friendship_set', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='friendship',
            name='to_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='follower_friendship_set', to=settings.AUTH_USER_MODEL),
        ),
    ]
