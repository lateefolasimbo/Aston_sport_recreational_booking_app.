from django.test import TestCase, Client
from .models import CustomUser, Membership, Review, ChatbotMessage
from promotions.models import Promotion
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse
import json

class CustomUserModelTest(TestCase):
    def test_create_user(self):
        # Test for creating a regular user
        user = CustomUser.objects.create_user(username='testuser', password='testpassword')
        self.assertEqual(user.username, 'testuser')
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        # Test for creating an admin/superuser
        superuser = CustomUser.objects.create_superuser(username='testadmin', password='adminpassword')
        self.assertEqual(superuser.username, 'testadmin')
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)

    def test_is_admin(self):
        # Test for the is_admin property
        customer = CustomUser.objects.create_user(username='customer', password='password')
        admin = CustomUser.objects.create_user(username='admin', password='password', role='admin')

        self.assertFalse(customer.is_admin())
        self.assertTrue(admin.is_admin())


class MembershipModelTest(TestCase):
    def setUp(self):
        # Creating a test user for our memberships
        self.user = CustomUser.objects.create_user(username='testuser', password='testpassword')

    def test_create_membership(self):
        # Test for creating a membership
        membership = Membership.objects.create(user=self.user, membership_type='Premium')
        self.assertEqual(membership.user, self.user)
        self.assertEqual(membership.membership_type, 'Premium')
        self.assertEqual(membership.price, 25.00)  # Check the price

    def test_calculate_expiration_date(self):
        # Test for the calculate_expiration_date method
        membership = Membership.objects.create(user=self.user, membership_type='Basic')
        expected_expiration = membership.start_date + timedelta(days=30)
        self.assertEqual(membership.calculate_expiration_date(), expected_expiration)

    def test_membership_expiration(self):
        # Testing the membership expiration feature
        membership = Membership.objects.create(user=self.user, membership_type='Basic', expiration_date=timezone.now().date() - timedelta(days=1))
        membership.save()  # Trigger the save method
        self.assertEqual(membership.status, 'Expired')

    def test_membership_auto_renewal(self):
        # Testing the membership auto-renewal feature
        membership = Membership.objects.create(user=self.user, membership_type='Basic', expiration_date=timezone.now().date() - timedelta(days=1), auto_renew=True)
        membership.save()  # Trigger save method
        self.assertEqual(membership.status, 'Active')
        self.assertEqual(membership.start_date, timezone.now().date())


class ReviewModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testuser', password='testpassword')

    def test_create_review(self):
        review = Review.objects.create(user=self.user, review_text='This is a test review.')
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.review_text, 'This is a test review.')

    def test_review_str(self):
        review = Review.objects.create(user=self.user, review_text='This is a test review.')
        self.assertEqual(str(review), f'Review by testuser on {review.created_at}')

class ChatbotMessageModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testuser', password='testpassword')

    def test_create_chatbot_message(self):
        message = ChatbotMessage.objects.create(user=self.user, message='Hello, world!')
        self.assertEqual(message.user, self.user)
        self.assertEqual(message.message, 'Hello, world!')

    def test_chatbot_message_str(self):
        message = ChatbotMessage.objects.create(user=self.user, message='Hello, world!')
        self.assertEqual(str(message), f'testuser: Hello, world! ({message.timestamp})')

    def test_chatbot_message_anonymous(self):
        message = ChatbotMessage.objects.create(user=None, message='Anonymous message')
        self.assertEqual(str(message), f'Anonymous: Anonymous message ({message.timestamp})')



class UserViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(username='testuser', password='testpassword')

    def test_user_login_valid(self):
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'testpassword'})
        self.assertEqual(response.status_code, 302)  # Check for redirect
        self.assertEqual(response.url, reverse('home'))  # Check redirect URL
        self.assertTrue(self.client.session['_auth_user_id'])  # Check if user is logged in

    def test_user_login_invalid_password(self):
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'wrongpassword'})
        self.assertContains(response, "Invalid username or password.")
        self.assertFalse(self.client.session.get('_auth_user_id'))  # Check if user is not logged in

    def test_user_login_invalid_username(self):
        response = self.client.post(reverse('login'), {'username': 'wronguser', 'password': 'testpassword'})
        self.assertContains(response, "Invalid username or password.")
        self.assertFalse(self.client.session.get('_auth_user_id'))

    def test_user_logout(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('login'))
        self.assertFalse(self.client.session.get('_auth_user_id'))

# Admin tests

    def test_admin_dashboard_access_admin(self):
        admin_user = CustomUser.objects.create_superuser(username='adminuser', password='adminpassword')
        self.client.login(username='adminuser', password='adminpassword')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)  # Admin should have access

    def test_user_list_access_admin(self):
        admin_user = CustomUser.objects.create_superuser(username='adminuser', password='adminpassword')
        self.client.login(username='adminuser', password='adminpassword')
        response = self.client.get(reverse('user_list'))
        self.assertEqual(response.status_code, 200)  # Admin should have access


    def test_user_list_displays_users(self):
        admin_user = CustomUser.objects.create_superuser(username='adminuser', password='adminpassword')
        self.client.login(username='adminuser', password='adminpassword')
        user1 = CustomUser.objects.create_user(username='user1', password='password1')
        user2 = CustomUser.objects.create_user(username='user2', password='password2')
        response = self.client.get(reverse('user_list'))
        self.assertContains(response, 'user1')
        self.assertContains(response, 'user2')

    def test_user_list_search(self):
        admin_user = CustomUser.objects.create_superuser(username='adminuser', password='adminpassword')
        self.client.login(username='adminuser', password='adminpassword')
        user1 = CustomUser.objects.create_user(username='searchuser', password='password1')
        user2 = CustomUser.objects.create_user(username='user2', password='password2')
        response = self.client.get(reverse('user_list') + '?q=searchuser')
        self.assertContains(response, 'searchuser')
        self.assertNotContains(response, 'user2')

    def test_user_list_role_filter(self):
        admin_user = CustomUser.objects.create_superuser(username='adminuser', password='adminpassword')
        self.client.login(username='adminuser', password='adminpassword')
        regular_user = CustomUser.objects.create_user(username='regularuser', password='password1')
        response = self.client.get(reverse('user_list') + '?role=user')
        self.assertContains(response, 'regularuser')
        self.assertNotContains(response, 'adminuser')
    
    def test_edit_user_access_admin(self):
        admin_user = CustomUser.objects.create_superuser(username='adminuser', password='adminpassword')
        self.client.login(username='adminuser', password='adminpassword')
        user_to_edit = CustomUser.objects.create_user(username='edituser', password='editpassword')
        response = self.client.get(reverse('edit_user', args=[user_to_edit.id]))
        self.assertEqual(response.status_code, 200)  # Admin should have access


    def test_add_user_access_admin(self):
        admin_user = CustomUser.objects.create_superuser(username='adminuser', password='adminpassword')
        self.client.login(username='adminuser', password='adminpassword')
        response = self.client.get(reverse('add_user'))
        self.assertEqual(response.status_code, 200)  # Admin should have access


    def test_delete_user_access_admin(self):
        admin_user = CustomUser.objects.create_superuser(username='adminuser', password='adminpassword')
        self.client.login(username='adminuser', password='adminpassword')
        user_to_delete = CustomUser.objects.create_user(username='deleteuser', password='deletepassword')
        response = self.client.get(reverse('delete_user', args=[user_to_delete.id]))
        self.assertEqual(response.status_code, 200)  # Admin should have access


    def test_membership_list_access_admin(self):
        admin_user = CustomUser.objects.create_superuser(username='adminuser', password='adminpassword')
        self.client.login(username='adminuser', password='adminpassword')
        response = self.client.get(reverse('membership_list'))
        self.assertEqual(response.status_code, 200)  # Admin should have access

    def test_membership_list_displays_memberships(self):
        admin_user = CustomUser.objects.create_superuser(username='adminuser', password='adminpassword')
        self.client.login(username='adminuser', password='adminpassword')
        user1 = CustomUser.objects.create_user(username='user1', password='password1')
        membership1 = Membership.objects.create(user=user1, membership_type='Basic')
        response = self.client.get(reverse('membership_list'))
        self.assertContains(response, 'user1')
        self.assertContains(response, 'Basic')

    def test_membership_delete_access_admin(self):
        admin_user = CustomUser.objects.create_superuser(username='adminuser', password='adminpassword')
        self.client.login(username='adminuser', password='adminpassword')
        user1 = CustomUser.objects.create_user(username='user1', password='password1')
        membership1 = Membership.objects.create(user=user1, membership_type='Basic')
        response = self.client.get(reverse('membership_delete', args=[membership1.id]))
        self.assertEqual(response.status_code, 200)  # Admin should have access

    def test_chatbot_messages_access_admin(self):
        admin_user = CustomUser.objects.create_superuser(username='adminuser', password='adminpassword')
        self.client.login(username='adminuser', password='adminpassword')
        response = self.client.get(reverse('chatbot_messages'))
        self.assertEqual(response.status_code, 200)  # Admin should have access

    def test_chatbot_messages_displays_messages(self):
        admin_user = CustomUser.objects.create_superuser(username='adminuser', password='adminpassword')
        self.client.login(username='adminuser', password='adminpassword')
        user1 = CustomUser.objects.create_user(username='user1', password='password1')
        ChatbotMessage.objects.create(user=user1, message='Hello, world!')
        response = self.client.get(reverse('chatbot_messages'))
        self.assertContains(response, 'Hello, world!')
        self.assertContains(response, 'user1')

    
    def test_promotions_access_admin(self):
        admin_user = CustomUser.objects.create_superuser(username='adminuser', password='adminpassword')
        self.client.login(username='adminuser', password='adminpassword')
        response = self.client.get(reverse('promotions'))
        self.assertEqual(response.status_code, 200)  # Admin should have access


    def test_admin_reviews_access_admin(self):
        admin_user = CustomUser.objects.create_superuser(username='adminuser', password='adminpassword')
        self.client.login(username='adminuser', password='adminpassword')
        response = self.client.get(reverse('admin_reviews'))
        self.assertEqual(response.status_code, 200)  # Admin should have access

    def test_admin_reviews_displays_reviews(self):
        admin_user = CustomUser.objects.create_superuser(username='adminuser', password='adminpassword')
        self.client.login(username='adminuser', password='adminpassword')
        user1 = CustomUser.objects.create_user(username='user1', password='password1')
        Review.objects.create(user=user1, review_text='Great service!')
        response = self.client.get(reverse('admin_reviews'))
        self.assertContains(response, 'Great service!')
        self.assertContains(response, 'user1')

    def test_membership_plans_access(self):
        regular_user = CustomUser.objects.create_user(username='regularuser', password='regularpassword')
        self.client.login(username='regularuser', password='regularpassword')
        response = self.client.get(reverse('membership_plans'))
        self.assertEqual(response.status_code, 200)  # User should have access

    def test_user_membership_signup_access(self):
        regular_user = CustomUser.objects.create_user(username='regularuser', password='regularpassword')
        self.client.login(username='regularuser', password='regularpassword')
        response = self.client.get(reverse('user_membership_signup', args=['Basic']))
        self.assertEqual(response.status_code, 200)  # User should have access

   

    


   


    
   