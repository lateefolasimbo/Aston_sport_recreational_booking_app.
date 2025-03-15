# Generated by Django 5.1.6 on 2025-03-14 18:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0003_remove_payment_amount_remove_payment_user_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
