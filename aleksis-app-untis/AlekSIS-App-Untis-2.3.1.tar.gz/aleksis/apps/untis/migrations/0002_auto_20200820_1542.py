# Generated by Django 3.0.9 on 2020-08-20 13:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('untis', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='globalpermissions',
            options={'managed': False, 'permissions': (('assign_subjects_to_groups', 'Kann Fächer zu Gruppen zuzuordnen'),)},
        ),
    ]
