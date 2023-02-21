# Generated by Django 4.1.5 on 2023-02-12 17:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stations', '0016_rename_stop_id_lift_stop_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Route',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('line', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='stations.line')),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='RouteStation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField(default=1)),
                ('route', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stations.route')),
                ('station', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stations.stop')),
            ],
            options={
                'ordering': ('route', 'order'),
            },
        ),
    ]