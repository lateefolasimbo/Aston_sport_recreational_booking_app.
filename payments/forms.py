from django import forms
from .models import Payment
from bookings.models import Booking

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['booking']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['booking'].queryset = Booking.objects.all()
