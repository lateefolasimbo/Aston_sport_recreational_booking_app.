
# Create your models here.

from django.db import models

class Promotion(models.Model):
    #Fields for promotion items
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)



