# Generated by Django 4.1.5 on 2023-02-12 13:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stations', '0010_alter_stop_cardinal_direction_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='lift',
            old_name='assistance_requested',
            new_name='assistance_required',
        ),
    ]
