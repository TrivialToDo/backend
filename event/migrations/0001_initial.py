# Generated by Django 4.2.6 on 2023-11-17 13:59

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('hash', models.CharField(max_length=32, primary_key=True, serialize=False)),
                ('title', models.CharField(default='Untitled', max_length=100)),
                ('description', models.TextField(default='')),
                ('repeat', models.CharField(choices=[('never', 'Never'), ('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')], default='never', max_length=10)),
                ('timeStart', models.TimeField()),
                ('timeEnd', models.TimeField(null=True)),
                ('dateStart', models.DateField()),
                ('dateEnd', models.DateField(default=datetime.date(9999, 12, 31))),
                ('dayOfWeek', models.IntegerField(null=True)),
                ('dayOfMonth', models.IntegerField(null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.user')),
            ],
        ),
    ]
