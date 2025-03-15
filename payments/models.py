from django.db import models
from bookings.models import Booking
from promotions.models import Promotion 

class Payment(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments', null=True, default=None)
    date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    promotion = models.ForeignKey(Promotion, on_delete=models.SET_NULL, null=True, blank=True)  # Add this line

    def __str__(self):
        return f"Payment for {self.booking} on {self.date}"