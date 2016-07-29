# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import opal.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('elcid', '0032_move_models_to_microhaem'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    state_operations = [
        migrations.CreateModel(
            name='EpisodeOfNeutropenia',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(null=True, blank=True)),
                ('updated', models.DateTimeField(null=True, blank=True)),
                ('consistency_token', models.CharField(max_length=8)),
                ('start', models.DateField(null=True, blank=True)),
                ('stop', models.DateField(null=True, blank=True)),
                ('created_by', models.ForeignKey(related_name='created_microhaem_episodeofneutropenia_subrecords', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('patient', models.ForeignKey(to='opal.Patient')),
                ('updated_by', models.ForeignKey(related_name='updated_microhaem_episodeofneutropenia_subrecords', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ['-start'],
            },
            bases=(opal.models.UpdatesFromDictMixin, models.Model),
        ),
        migrations.CreateModel(
            name='HaemChemotherapyType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
            ],
            options={
                'verbose_name': 'Chemotherapy type',
            },
        ),
        migrations.CreateModel(
            name='HaemInformation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(null=True, blank=True)),
                ('updated', models.DateTimeField(null=True, blank=True)),
                ('consistency_token', models.CharField(max_length=8)),
                ('date_of_transplant', models.DateField(null=True, blank=True)),
                ('neutropenia_onset', models.DateField(null=True, blank=True)),
                ('date_of_chemotherapy', models.DateField(null=True, blank=True)),
                ('count_recovery', models.DateField(null=True, blank=True)),
                ('details', models.TextField(null=True, blank=True)),
                ('type_of_transplant_ft', models.CharField(default=b'', max_length=255, null=True, blank=True)),
                ('patient_type_ft', models.CharField(default=b'', max_length=255, null=True, blank=True)),
                ('type_of_chemotherapy_ft', models.CharField(default=b'', max_length=255, null=True, blank=True)),
                ('created_by', models.ForeignKey(related_name='created_microhaem_haeminformation_subrecords', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('patient', models.ForeignKey(to='opal.Patient')),
            ],
            options={
                'abstract': False,
            },
            bases=(opal.models.UpdatesFromDictMixin, models.Model),
        ),
        migrations.CreateModel(
            name='HaemInformationType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
            ],
            options={
                'ordering': ['name'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='HaemTransplantType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
            ],
            options={
                'verbose_name': 'Transplant Type',
            },
        ),
        migrations.AddField(
            model_name='haeminformation',
            name='patient_type_fk',
            field=models.ForeignKey(blank=True, to='microhaem.HaemInformationType', null=True),
        ),
        migrations.AddField(
            model_name='haeminformation',
            name='type_of_chemotherapy_fk',
            field=models.ForeignKey(blank=True, to='microhaem.HaemChemotherapyType', null=True),
        ),
        migrations.AddField(
            model_name='haeminformation',
            name='type_of_transplant_fk',
            field=models.ForeignKey(blank=True, to='microhaem.HaemTransplantType', null=True),
        ),
        migrations.AddField(
            model_name='haeminformation',
            name='updated_by',
            field=models.ForeignKey(related_name='updated_microhaem_haeminformation_subrecords', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]

    operations = [
        # After this state operation, the Django DB state should match the
        # actual database structure.
        migrations.SeparateDatabaseAndState(state_operations=state_operations)
    ]
