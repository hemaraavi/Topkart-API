# Generated by Django 4.0.4 on 2023-05-22 15:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lightning_deals', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='phone_number',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='username',
            field=models.CharField(max_length=120, unique=True),
        ),
    ]
