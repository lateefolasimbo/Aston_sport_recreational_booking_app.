from django.conf import settings
from django.db import models
from  decimal import Decimal

#Activity Model
class Activity(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='activity_images/', null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) 
    availability_status = models.BooleanField(default=True, help_text="Check if the activity is available")

    def __str__(self):
        return self.name

#Booking Model
class Booking(models.Model):
    DURATION_CHOICES = (
        (30, '30 minutes'),
        (60, '60 minutes'),
        (90, '90 minutes'),
        (120, '120 minutes'),
        (180, '180 minutes'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name="bookings")
    date = models.DateField()
    time = models.TimeField()
    duration = models.IntegerField(choices=DURATION_CHOICES, default=60, help_text="Duration in minutes") #changed to choices
    status = models.CharField(
        max_length=20,
        choices=[("pending", "Pending"), ("confirmed", "Confirmed"), ("cancelled", "Cancelled")],
        default="pending",
    )

    def __str__(self):
        return f"Booking by {self.user.username} for {self.activity.name} on {self.date} at {self.time}"

    def get_total_price(self):
        activity_price = self.activity.price
        duration_hours = self.duration / 60
        total_price = activity_price * Decimal(str(duration_hours))  # Convert duration_hours to Decimal
        return total_price
    
