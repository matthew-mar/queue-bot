# Generated by Django 4.0.3 on 2022-03-21 08:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Chats',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chat_vk_id', models.CharField(max_length=20, null=True, unique=True)),
                ('chat_name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Queues',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('member_order', models.IntegerField()),
                ('member_vk_id', models.CharField(max_length=11, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='QueuesChats',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('queue_datetime', models.DateTimeField()),
                ('queue_name', models.CharField(max_length=255, null=True)),
                ('chat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bot.chats')),
                ('queue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bot.queues')),
            ],
        ),
        migrations.CreateModel(
            name='ChatMembers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('member_vk_id', models.CharField(max_length=11, null=True, unique=True)),
                ('chat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bot.chats')),
            ],
        ),
        migrations.CreateModel(
            name='Admins',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('admin_vk_id', models.CharField(max_length=11, null=True, unique=True)),
                ('chat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bot.chats')),
            ],
        ),
    ]