from django import forms
from .models import Promotion

class PromotionForm(forms.ModelForm):
    class Meta:
        model = Promotion
        fields = ['code', 'description', 'discount_percentage', 'start_date', 'end_date', 'is_active']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }
