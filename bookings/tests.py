from django.test import TestCase, Client
from .models import Activity, Booking
from django.urls import reverse
from users.models import CustomUser, Review
from payments.models import Payment
from promotions.models import Promotion
from decimal import Decimal
import datetime
import json

class ActivityModelTest(TestCase):

    def test_activity_creation(self):
        activity = Activity.objects.create(
            name='Tennis',
            description='A fun sport',
            price=10.00,
        )
        self.assertEqual(activity.name, 'Tennis')
        self.assertEqual(activity.description, 'A fun sport')
        self.assertEqual(activity.price, 10.00)
        self.assertTrue(activity.availability_status)  # Default value is True

    def test_activity_fields_blank_null(self):
        activity = Activity.objects.create(name='Swimming')
        self.assertEqual(activity.name, 'Swimming')
        self.assertIsNone(activity.description)
        self.assertFalse(activity.image)

    def test_activity_price_default(self):
        activity = Activity.objects.create(name='Basketball')
        self.assertEqual(activity.price, 0.00)  # Default value is 0.00

    def test_activity_availability_status_default(self):
        activity = Activity.objects.create(name='Football')
        self.assertTrue(activity.availability_status)  # Default value is True

    def test_activity_str_method(self):
        activity = Activity.objects.create(name='Volleyball')
        self.assertEqual(str(activity), 'Volleyball')

    def test_activity_name_unique(self):
        Activity.objects.create(name='Yoga')
        with self.assertRaises(Exception):
            Activity.objects.create(name='Yoga')


class ActivityViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.admin_user = CustomUser.objects.create_superuser(username='adminuser', password='adminpassword')
        self.regular_user = CustomUser.objects.create_user(username='regularuser', password='regularpassword')
        self.activity = Activity.objects.create(name='Tennis', description='A fun sport', price=10.00)

    def test_activity_list_access_admin(self):
        self.client.login(username='adminuser', password='adminpassword')
        response = self.client.get(reverse('activity_list'))
        self.assertEqual(response.status_code, 200)  # Admin should have access

    

    def test_add_activity_access_admin(self):
        self.client.login(username='adminuser', password='adminpassword')
        response = self.client.get(reverse('add_activity'))
        self.assertEqual(response.status_code, 200)  # Admin should have access

   

    def test_edit_activity_access_admin(self):
        self.client.login(username='adminuser', password='adminpassword')
        response = self.client.get(reverse('edit_activity', args=[self.activity.id]))
        self.assertEqual(response.status_code, 200)  # Admin should have access

    

    def test_delete_activity_access_admin(self):
        self.client.login(username='adminuser', password='adminpassword')
        response = self.client.get(reverse('delete_activity', args=[self.activity.id]))
        self.assertEqual(response.status_code, 200)  # Admin should have access

    

    def test_activity_list_displays_activities(self):
        self.client.login(username='adminuser', password='adminpassword')
        response = self.client.get(reverse('activity_list'))
        self.assertContains(response, 'Tennis')
        self.assertContains(response, 'A fun sport')
        self.assertContains(response, '10.00')


class BookingModelTest(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testuser', password='testpassword')
        self.activity = Activity.objects.create(name='Tennis', price=10.00)

    def test_booking_creation(self):
        booking = Booking.objects.create(
            user=self.user,
            activity=self.activity,
            date='2024-01-01',
            time='10:00',
            duration=60,
        )
        self.assertEqual(booking.user, self.user)
        self.assertEqual(booking.activity, self.activity)
        self.assertEqual(booking.date, '2024-01-01')
        self.assertEqual(booking.time, '10:00')
        self.assertEqual(booking.duration, 60)
        self.assertEqual(booking.status, 'pending')  # Default value is 'pending'

    def test_booking_fields_default(self):
        booking = Booking.objects.create(
            user=self.user,
            activity=self.activity,
            date='2024-01-01',
            time='10:00',
        )
        self.assertEqual(booking.duration, 60)  # Default value is 60
        self.assertEqual(booking.status, 'pending')  # Default value is 'pending'

    def test_booking_str_method(self):
        booking = Booking.objects.create(
            user=self.user,
            activity=self.activity,
            date='2024-01-01',
            time='10:00',
        )
        expected_str = f"Booking by {self.user.username} for {self.activity.name} on 2024-01-01 at 10:00"
        self.assertEqual(str(booking), expected_str)

    
class BookingViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.admin_user = CustomUser.objects.create_superuser(username='adminuser', password='adminpassword')
        self.regular_user = CustomUser.objects.create_user(username='regularuser', password='regularpassword')
        self.activity = Activity.objects.create(name='Tennis', price=10.00)
        self.booking = Booking.objects.create(
            user=self.regular_user,
            activity=self.activity,
            date='2024-01-01',
            time='10:00',
            duration=60,
        )

    def test_booking_list_access_admin(self):
        self.client.login(username='adminuser', password='adminpassword')
        response = self.client.get(reverse('booking_list'))
        self.assertEqual(response.status_code, 200)  # Admin should have access

    
    
    def test_user_booking_create_access_user(self):
        self.client.login(username='regularuser', password='regularpassword')
        response = self.client.get(reverse('user_booking_create'))
        self.assertEqual(response.status_code, 200) # User should have access

    def test_user_booking_create_access_admin(self):
        self.client.login(username='adminuser', password='adminpassword')
        response = self.client.get(reverse('user_booking_create'))
        self.assertEqual(response.status_code, 200) # Admin should have access

    def test_user_dashboard_access_user(self):
        self.client.login(username='regularuser', password='regularpassword')
        response = self.client.get(reverse('user_dashboard'))
        self.assertEqual(response.status_code, 200) # User should have access

    def test_user_dashboard_access_admin(self):
        self.client.login(username='adminuser', password='adminpassword')
        response = self.client.get(reverse('user_dashboard'))
        self.assertEqual(response.status_code, 200) # Admin should have access

    def test_payment_review_access_user(self):
        self.client.login(username='regularuser', password='regularpassword')
        response = self.client.get(reverse('payment_review', args=[self.booking.id]))
        self.assertEqual(response.status_code, 200) # User should have access


class BookingCreationTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.admin_user = CustomUser.objects.create_superuser(username='adminuser', password='adminpassword')
        self.regular_user = CustomUser.objects.create_user(username='regularuser', password='regularpassword')
        self.activity = Activity.objects.create(name='Tennis', price=10.00)

    def test_user_booking_create_user(self):
        self.client.login(username='regularuser', password='regularpassword')
        response = self.client.post(reverse('user_booking_create'), {
            'activity': self.activity.id,
            'date': '2024-01-01',
            'time': '10:00',
            'duration': 60,
        })
        self.assertEqual(response.status_code, 302)  # Should redirect after successful creation
        self.assertEqual(Booking.objects.count(), 1)  # Check if booking was created
        booking = Booking.objects.first()
        self.assertEqual(booking.user, self.regular_user)  # Check if booking was created for the correct user

class BookingDeleteTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.admin_user = CustomUser.objects.create_superuser(username='adminuser', password='adminpassword')
        self.regular_user = CustomUser.objects.create_user(username='regularuser', password='regularpassword')
        self.activity = Activity.objects.create(name='Tennis', price=10.00)
        self.booking = Booking.objects.create(
            user=self.regular_user,
            activity=self.activity,
            date='2024-01-01',
            time='10:00',
            duration=60,
        )


    def test_booking_delete_admin(self):
        self.client.login(username='adminuser', password='adminpassword')
        response = self.client.post(reverse('delete_booking', args=[self.booking.id]))
        self.assertEqual(response.status_code, 302)  # Should redirect after successful deletion
        self.assertEqual(Booking.objects.count(), 0)  # Check if booking was deleted


class UserBookingCreationTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.regular_user = CustomUser.objects.create_user(username='regularuser', password='regularpassword')
        self.activity = Activity.objects.create(name='Tennis', price=10.00)

    def test_user_booking_create(self):
        self.client.login(username='regularuser', password='regularpassword')
        response = self.client.post(reverse('user_booking_create'), {
            'activity': self.activity.id,
            'date': '2024-01-01',
            'time': '10:00',
            'duration': 60,
        })
        self.assertEqual(response.status_code, 302)  # Should redirect after successful creation
        self.assertEqual(Booking.objects.count(), 1)  # Check if booking was created
        booking = Booking.objects.first()
        self.assertEqual(booking.user, self.regular_user)  # Check if booking was created for the correct user


class PaymentProcessingTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.regular_user = CustomUser.objects.create_user(username='regularuser', password='regularpassword')
        self.activity = Activity.objects.create(name='Tennis', price=10.00)
        self.booking = Booking.objects.create(
            user=self.regular_user,
            activity=self.activity,
            date='2024-01-01',
            time='10:00',
            duration=60,
        )
        self.promotion = Promotion.objects.create(
            code='TEST',
            discount_percentage=10,
            is_active=True,
            start_date=datetime.date(2024, 1, 1),
            end_date=datetime.date(2024, 1, 31),  
        )

    def test_payment_review(self):
        self.client.login(username='regularuser', password='regularpassword')
        response = self.client.get(reverse('payment_review', args=[self.booking.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '10.00')  # Check for the total price

    def test_process_payment(self):
        self.client.login(username='regularuser', password='regularpassword')
        session = self.client.session # Get the current session
        session['promotion_id'] = self.promotion.id # Set the promotion id in the session
        session.save() # Save the session
        response = self.client.post(reverse('process_payment', args=[self.booking.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Payment.objects.count(), 1)
        payment = Payment.objects.first()
        self.assertEqual(payment.booking, self.booking)
        self.assertEqual(payment.amount, Decimal('9.00'))
        self.assertEqual(self.booking.status, 'pending')

class CalendarViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.regular_user = CustomUser.objects.create_user(username='regularuser', password='regularpassword')
        self.activity = Activity.objects.create(name='Tennis', price=10.00)
        Booking.objects.create(
            user=self.regular_user,
            activity=self.activity,
            date='2024-01-01',
            time='10:00',
            duration=60,
        )

    def test_calendar_view(self):
        response = self.client.get(reverse('calendar'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tennis')  # Check if activity name is displayed
        self.assertContains(response, '2024-01-01') # Check if date is displayed
        self.assertContains(response, '10:00') # Check if time is displayed

class HomeViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.regular_user = CustomUser.objects.create_user(username='regularuser', password='regularpassword')
        Review.objects.create(
            user=self.regular_user,
            review_text='Great experience!',
        )

    def test_home_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Great experience!')  # Check if review is displayed

    def test_submit_review(self):
        self.client.login(username='regularuser', password='regularpassword')
        response = self.client.post(reverse('home'), {
            'review_text': 'Good activity!',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Review.objects.count(), 2)  # Check if review was created