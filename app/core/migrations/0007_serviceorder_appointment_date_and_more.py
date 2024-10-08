# Generated by Django 4.2.15 on 2024-08-14 00:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_alter_providerprofile_options_alter_review_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='serviceorder',
            name='appointment_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='serviceorder',
            name='is_appointment',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='serviceorder',
            name='status',
            field=models.CharField(choices=[('approved', 'Approved'), ('canceled', 'Canceled'), ('completed', 'Completed')], default='pending', max_length=50),
        ),
    ]
