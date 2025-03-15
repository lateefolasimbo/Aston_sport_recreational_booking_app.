from django.contrib import admin
from .models import Promotion

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
  list_display = ('code', 'discount_percentage', 'start_date', 'end_date', 'is_active') #Fields in the promotions model
  search_fields = ('code', 'description')
  list_filter = ('is_active', 'start_date', 'end_date')
