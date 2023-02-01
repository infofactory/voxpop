# Generated by Django 4.1.5 on 2023-02-01 10:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stations', '0005_alter_stop_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stair',
            name='stairlift_ptr',
        ),
        migrations.RemoveField(
            model_name='stairlift',
            name='from_areas',
        ),
        migrations.RemoveField(
            model_name='stairlift',
            name='stop_id',
        ),
        migrations.RemoveField(
            model_name='stairlift',
            name='to_areas',
        ),
        migrations.AddField(
            model_name='lift',
            name='assistance_requested',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='lift',
            name='handrail',
            field=models.IntegerField(choices=[(0, 'no'), (1, 'right'), (2, 'left'), (3, 'both')], default=0),
        ),
        migrations.AddField(
            model_name='lift',
            name='handrail_height',
            field=models.FloatField(default=False),
        ),
        migrations.AddField(
            model_name='lift',
            name='lift_type',
            field=models.IntegerField(choices=[(0, 'Lift'), (1, 'Stairlift'), (0, 'Stair'), (0, 'Escalator')], default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='lift',
            name='number_of_steps',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='lift',
            name='steps',
            field=models.IntegerField(choices=[(0, 'No'), (1, 'tapis roulant')], default=0),
        ),
        migrations.AddField(
            model_name='lift',
            name='steps_height',
            field=models.FloatField(default=False),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='stop',
            name='desc',
            field=models.TextField(blank=True, null=True, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='stop',
            name='lat',
            field=models.FloatField(blank=True, null=True, verbose_name='Latitude'),
        ),
        migrations.AlterField(
            model_name='stop',
            name='visually_impaired_path',
            field=models.IntegerField(choices=[(0, 'No info for the stop'), (1, 'Yes'), (2, 'No'), (3, 'Only in some areas')], default=0),
        ),
        migrations.AlterField(
            model_name='stop',
            name='wheelchair_boarding',
            field=models.IntegerField(choices=[(0, 'No info'), (1, 'Yes, there is'), (2, 'No')], default=0),
        ),
        migrations.AlterField(
            model_name='stop',
            name='wifi',
            field=models.BooleanField(default=False),
        ),
        migrations.DeleteModel(
            name='Escalator',
        ),
        migrations.DeleteModel(
            name='Stair',
        ),
        migrations.DeleteModel(
            name='Stairlift',
        ),
    ]