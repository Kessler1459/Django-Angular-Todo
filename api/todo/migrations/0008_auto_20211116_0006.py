# Generated by Django 3.2.9 on 2021-11-16 00:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('todo', '0007_alter_note_state'),
    ]

    operations = [
        migrations.AddField(
            model_name='board',
            name='guests',
            field=models.ManyToManyField(null=True, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='note',
            name='creator',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]