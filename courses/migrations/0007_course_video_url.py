# Generated by Django 5.2.1 on 2025-05-22 08:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0006_remove_question_created_at_alter_question_exam'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='video_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]
