# Generated by Django 4.1.4 on 2022-12-16 12:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_profileinfo_facebook_url_profileinfo_linkedin_url_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profileinfo',
            old_name='thumbnail',
            new_name='dp',
        ),
    ]
