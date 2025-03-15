from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import BaseUserManager
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, password, **extra_fields)


class CustomUser(AbstractUser):
    USER_ROLES = (
        ('customer', 'Customer'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=USER_ROLES, default='customer')
    is_admin = models.BooleanField(default=False)  # Use this for admin status

    objects = CustomUserManager()

    def is_admin(self):
        return self.role == 'admin'


class Membership(models.Model):
    TIER_CHOICES = [
        ("Basic", "Basic"),
        ("Premium", "Premium"),
        ("Vip", "VIP"),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="membership")
    membership_type = models.CharField(max_length=20, choices=TIER_CHOICES, default="Basic")
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    start_date = models.DateField(auto_now_add=True)
    expiration_date = models.DateField(null=True, blank=True)
    auto_renew = models.BooleanField(default=False)

    STATUS_CHOICES = [
        ("Active", "Active"),
        ("Expired", "Expired"),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active")

    def save(self, *args, **kwargs):
        today = timezone.now().date()

        # Set the price based on membership type if it's not already set
        if not self.price:
            if self.membership_type == "Basic":
                self.price = 10.00  # Example price for Basic
            elif self.membership_type == "Premium":
                self.price = 25.00  # Example price for Premium
            elif self.membership_type == "Vip":
                self.price = 50.00  # Example price for VIP

        # Set expiration date if not already set
        if not self.expiration_date:
            self.expiration_date = self.calculate_expiration_date()

        # Check if expired
        if self.expiration_date < today:
            if self.auto_renew:
                self.start_date = today
                self.expiration_date = self.calculate_expiration_date()
                self.status = "Active"
            else:
                self.status = "Expired"

        super().save(*args, **kwargs)

    def calculate_expiration_date(self):
        """Set expiration date based on membership type"""
        duration = {
            "Basic": 30,
            "Premium": 90,
            "Vip": 180
        }.get(self.membership_type, 30)
        return timezone.now().date() + timezone.timedelta(days=duration)

    def __str__(self):
        return f"{self.user.username} - {self.membership_type} ({self.status})"
