# Generated by Django 5.1.6 on 2025-03-09 04:21

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_remove_customuser_is_admin_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='membership',
            name='membership_type',
            field=models.CharField(choices=[('Basic', 'Basic'), ('Premium', 'Premium'), ('Vip', 'VIP')], default='Basic', max_length=20),
        ),
        migrations.AlterField(
            model_name='membership',
            name='status',
            field=models.CharField(choices=[('Active', 'Active'), ('Expired', 'Expired')], default='active', max_length=10),
        ),
        migrations.AlterField(
            model_name='membership',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='memberships', to=settings.AUTH_USER_MODEL),
        ),
    ]
