# Generated by Django 3.2.9 on 2021-11-15 22:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todo', '0006_auto_20211115_2146'),
    ]

    operations = [
        migrations.AlterField(
            model_name='note',
            name='state',
            field=models.CharField(choices=[('TD', 'To do'), ('IP', 'In progress'), ('DN', 'Done')], default='TD', max_length=2),
        ),
    ]
