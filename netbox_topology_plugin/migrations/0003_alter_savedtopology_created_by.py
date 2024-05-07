# Generated by Django 4.2.4 on 2024-05-07 15:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('netbox_topology_plugin', '0002_alter_savedtopology_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='savedtopology',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]