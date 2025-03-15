from django.contrib import admin
from .models import Booking, Activity

# Register your models here.

#Activity Model Register (w/Admin)
@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

#Booking Model Register (w/Admin)
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
  list_display = ('user', 'activity', 'date', 'time', 'status') #Fields displayed in the Booking Model
  search_fields = ('user_username', 'activity', 'status') #Search Functionality
  list_filter = ('date', 'activity', 'status')