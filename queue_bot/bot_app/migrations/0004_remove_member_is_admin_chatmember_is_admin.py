# Generated by Django 4.0.3 on 2022-03-30 18:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot_app', '0003_member_is_admin_delete_admin'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='member',
            name='is_admin',
        ),
        migrations.AddField(
            model_name='chatmember',
            name='is_admin',
            field=models.BooleanField(default=False),
        ),
    ]
