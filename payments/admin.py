from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    # Display fields derived from the Payment and its related Booking
    list_display = ('get_user', 'get_activity', 'amount', 'date')
    search_fields = ('booking__user__username', 'booking__activity__name')  # Search by user and activity
    list_filter = ('date',)  # Filter payments by date

    def get_user(self, obj):
        return obj.booking.user.username  # Access the user from the related Booking
    get_user.short_description = 'User'  # Column name in the admin panel

    def get_activity(self, obj):
        return obj.booking.activity.name  # Access the activity name from the related Booking
    get_activity.short_description = 'Activity'  # Column name in the admin panel

    def amount(self, obj):
        return obj.amount  # Use the @property method from the Payment model
    amount.short_description = 'Amount'  # Column name in the admin panel
