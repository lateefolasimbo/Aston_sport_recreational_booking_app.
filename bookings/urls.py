from django.urls import path
from .views import BookingListView, BookingCreateView, BookingUpdateView, BookingDeleteView, activity_list, add_activity,edit_activity, delete_activity, booking_events, calendar_view, user_booking_create, check_availability, user_dashboard, payment_review, process_payment #added process_payment

urlpatterns = [
    path('', BookingListView.as_view(), name='booking_list'),
    path('create/', BookingCreateView.as_view(), name='create_booking'),
    path('<int:pk>/edit/', BookingUpdateView.as_view(), name='edit_booking'),
    path('<int:pk>/delete/', BookingDeleteView.as_view(), name='delete_booking'),
    path('activities/', activity_list, name='activity_list'),
    path('activities/add/', add_activity, name='add_activity'),
    path('calendar/', calendar_view, name='calendar'),
    path('user/book/', user_booking_create, name='user_booking_create'),
    path('dashboard/', user_dashboard, name='user_dashboard'),
    path("bookings/check-availability/", check_availability, name="check_availability"),
    path('activities/<int:activity_id>/edit/', edit_activity, name='edit_activity'),
    path('activities/<int:activity_id>/delete/', delete_activity, name='delete_activity'),
    path('payment_review/<int:booking_id>/', payment_review, name='payment_review'),
    path('process_payment/<int:booking_id>/', process_payment, name='process_payment'), #added this line
]