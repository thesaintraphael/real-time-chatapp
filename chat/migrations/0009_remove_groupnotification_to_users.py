# Generated by Django 3.1.5 on 2021-03-04 07:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0008_groupnotification_to_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='groupnotification',
            name='to_users',
        ),
    ]
