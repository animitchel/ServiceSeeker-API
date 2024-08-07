# Generated by Django 4.2.14 on 2024-08-01 21:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_providerprofile_bio_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='date_joined',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='servicetype',
            name='availability',
            field=models.CharField(blank=True, choices=[('mon_fri_9_6', 'Monday to Friday: 9 AM - 6 PM'), ('mon_fri_8_5', 'Monday to Friday: 8 AM - 5 PM'), ('mon_fri_10_7', 'Monday to Friday: 10 AM - 7 PM'), ('sat_sun_9_5', 'Saturday and Sunday: 9 AM - 5 PM'), ('sat_sun_10_6', 'Saturday and Sunday: 10 AM - 6 PM'), ('mon_sun_9_6', 'Monday to Sunday: 9 AM - 6 PM'), ('mon_sun_8_8', 'Monday to Sunday: 8 AM - 8 PM'), ('mon_sat_9_6', 'Monday to Saturday: 9 AM - 6 PM'), ('mon_sat_8_8', 'Monday to Saturday: 8 AM - 8 PM'), ('available_24_7', 'Available 24/7'), ('mon_wed_fri_9_5', 'Monday, Wednesday, Friday: 9 AM - 5 PM'), ('tue_thu_10_4', 'Tuesday, Thursday: 10 AM - 4 PM'), ('mon_fri_7_12', 'Monday to Friday: 7 AM - 12 PM'), ('mon_fri_1_6', 'Monday to Friday: 1 PM - 6 PM')], max_length=255, null=True),
        ),
    ]
