# Generated by Django 5.0.2 on 2024-03-16 07:36

from django.db import migrations
from ..views import hashPassword


def hash_passwords(apps, schema_editor):
    Project = apps.get_model('home', 'Project')
    for project in Project.objects.all():
        project.password = hashPassword(project.password) if project.password is not None else None
        project.save()

class Migration(migrations.Migration):

    dependencies = [
        ('home', '0027_passwordresettoken'),
    ]

    operations = [
        migrations.RunPython(hash_passwords),
    ]
