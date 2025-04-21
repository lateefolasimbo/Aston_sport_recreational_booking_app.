from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from .forms import CustomUserCreationForm, CustomAuthenticationForm,UserEditForm, AddUserForm, MembershipForm, UserProfileEditForm, UserMembershipForm
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages
from django.db.models import Sum
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from users.models import CustomUser,Membership, Review
from bookings.models import Booking, Activity
from payments.models import Payment
from promotions.models import Promotion
import csv
import xlwt
from django.utils import timezone
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from datetime import date, timedelta
from .models import ChatbotMessage
from django.http import JsonResponse
import json





# User Register View
def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_admin = form.cleaned_data['is_admin'] #setting is_admin from forms.py
            user.save()
            login(request, user)
            messages.success(request, "Registration Successful!")  

            if user.is_admin:
                return redirect('admin_dashboard') # Redirect to the admin dashboard
            else:
                return redirect('home')  # Redirect to the home page for regular customers
        else:
            # If the form is invalid error messages are displayed 
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error in {field}: {error}")
            return render(request, 'users/register.html', {'form': form})
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})


# User Login View
def user_login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Login Successful!")
            if user.is_superuser or user.is_staff:
                return redirect('admin_dashboard')
            else:
                return redirect('home')  # Redirect to the home page
        messages.error(request, "Invalid username or password.")
    else:
        form = CustomAuthenticationForm()
    return render(request, 'users/login.html', {'form': form})


# User Logout
def user_logout(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')  # Redirect to login page

def admin_required(user):
    return user.is_authenticated and user.is_admin # Only admins can access

# Admin Dashboard
@login_required
@user_passes_test(admin_required)
def admin_dashboard(request):
    # Fields that admin can manage on the admin dashboard
    total_users = CustomUser.objects.count()
    total_bookings = Booking.objects.count()

 # Calculate total payments from bookings
    activity_payments = Payment.objects.aggregate(total=Sum('amount'))['total'] or 0

    # Calculate payments from memberships
    membership_payments = Membership.objects.aggregate(total=Sum('price'))['total'] or 0

    # Calculate total payments
    total_payments = activity_payments + membership_payments

    active_promotions = Promotion.objects.filter(is_active=True).count()

    # Displaying at least 5 latest records from the database
    latest_bookings = Booking.objects.order_by('-date', '-time')[:5]
    print("Admin Dashboard Latest Bookings:", latest_bookings)  # Debugging line
    latest_payments = Payment.objects.order_by('-date')[:5]
    active_promo_list = Promotion.objects.filter(is_active=True).order_by('-start_date')[:5]

    # Displaying recent activity (recent users, bookings...etc)
    recent_users = CustomUser.objects.order_by('-date_joined')[:5]
    recent_bookings = Booking.objects.order_by('-date')[:5]
    recent_payments = Payment.objects.prefetch_related('booking__user', 'booking__activity').order_by('-date')[:5]

    print("Total Bookings:", total_bookings)

    # Implementing search queries
    query = request.GET.get('q', '')
    search_results = {
        'users': CustomUser.objects.filter(username__icontains=query) if query else [],
        'bookings': Booking.objects.filter(user__username__icontains=query) if query else [],
        'promotions': Promotion.objects.filter(code__icontains=query) if query else [],
    }

    context = {
        'total_users': total_users,
        'total_bookings': total_bookings,
        'total_payments': total_payments,
        'active_promotions': active_promotions,
        'latest_bookings': latest_bookings,
        'latest_payments': latest_payments,
        'active_promo_list': active_promo_list,
        'recent_users': recent_users,
        'recent_bookings': recent_bookings,
        'recent_payments': recent_payments,
        'search_results': search_results,
        'query': query,
    }
    return render(request, 'users/admin_dashboard.html', context)  # Passing the data from the database onto the admin dashboard

# Implementing the export data as CSV feature
def export_users_csv(request):
    response = HttpResponse(content_type= 'text/csv')
    response['Content-Disposition'] = 'attachment; filename="users.csv"'

    writer = csv.writer(response)
    writer.writerow(['Username', 'Email', 'Date Joined', 'Is Active', 'Is Admin'])

    users = CustomUser.objects.all()
    for user in users:
        writer.writerow([user.username, user.email, user.date_joined, user.is_active, user.is_staff])

    return response

def export_bookings_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="bookings.csv"'

    writer = csv.writer(response)
    writer.writerow(['User', 'Date', 'Time', 'Activity'])

    bookings = Booking.objects.all()
    for booking in bookings:
        writer.writerow([booking.user.username, booking.date, booking.time, booking.activity,])

    return response

def export_payments_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="payments.csv"'

    writer = csv.writer(response)
    writer.writerow(['User', 'Amount', 'Date'])

    payments = Payment.objects.all()
    for payment in payments:
        writer.writerow([payment.user.username, payment.amount, payment.date])

    return response

#Exporting Users as Excel
def export_users_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="users.xls"'

    wb = xlwt.Workbook()
    ws = wb.add_sheet('Users')

    columns = ['Username', 'Email', 'Date Joined', 'Is Active', 'Is Admin']
    for col_num, column_title in enumerate(columns):
        ws.write(0, col_num, column_title)

    users = CustomUser.objects.all()
    for row_num, user in enumerate(users, start=1):
        ws.write(row_num, 0, user.username)
        ws.write(row_num, 1, user.email)
        ws.write(row_num, 2, str(user.date_joined))
        ws.write(row_num, 3, user.is_active)
        ws.write(row_num, 4, user.is_staff)

    wb.save(response)
    return response

#User List View (Admin)
def user_list(request):
    query = request.GET.get("q", "")  # Get search query from request
    role_filter = request.GET.get("role", "")  # Get selected role filter

    users = CustomUser.objects.all()

    # Filter by search query (username or email)
    if query:
        users = users.filter(username__icontains=query) | users.filter(email__icontains=query)

    # Filter by role
    if role_filter == "admin":
        users = users.filter(is_superuser=True)

    elif role_filter == "user":
        users = users.filter(is_staff=False, is_superuser=False)

    return render(request, "users/user_list.html", {"users": users, "query": query, "role_filter": role_filter})

#Edit user view (Admin)
@login_required
def edit_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    old_role = user.role
    
    if request.method == "POST":
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            new_role = form.cleaned_data["role"]

            #if role is being changed, confirmation is required
            if old_role != new_role:
                messages.warning(request, f"You are changing {user.username}'s role from {old_role} to {new_role}. Confirm before proceeding.")

            form.save()
            messages.success(request, "User profile updated successfully")
            return redirect("user_list")  # Redirect back to user list after editing
    else:
        form = UserEditForm(instance=user)

    return render(request, "users/edit_user.html", {"form": form, "user": user})


# Add User View(Admin)
def add_user(request):
    if request.method == "POST":
        form = AddUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # Hash password
            user.save()
            messages.success(request, "User added successfully!")
            return redirect('user_list')  # Redirect back to user list
    else:
        form = AddUserForm()  # Initialize empty form only on GET requests

    return render(request, 'users/add_user.html', {'form': form}) 

# View User View(Admin)
@login_required
def view_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    try:
        membership = Membership.objects.get(user=user)
    except Membership.DoesNotExist:
        membership = None
    context = {'user': user, 'membership': membership}
    return render(request, 'users/view_user.html', context)

#Delete User View
@login_required
def delete_user(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)
    if request.method == 'POST':
        user.delete()
        messages.success(request, "User deleted successfully.")
        return redirect('user_list')
    context = {'user': user,
               'first_name': user.first_name,
               'last_name': user.last_name,
               'email': user.email,
               'username': user.username,
               
               
                }
    return render(request, 'users/delete_user.html', context)

# List all memberships
class MembershipListView(ListView):
    model = Membership
    template_name = "memberships/membership_list.html"
    context_object_name = "memberships"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = CustomUser.objects.all()  # Retrieve all users
        context['form'] = MembershipForm()
        return context


# Create a new membership
class MembershipCreateView(CreateView):
    model = Membership
    form_class = MembershipForm
    template_name = "memberships/membership_form.html"
    success_url = reverse_lazy("membership_list")

    def form_valid(self, form):
        membership = form.save(commit=False)
        membership.save()  # Save the object first to set start_date
        membership.expiration_date = membership.calculate_expiration_date()  # Calculate expiration_date after saving
        membership.save()  # Save again to update expiration_date
        return super().form_valid(form)


# Edit a membership
class MembershipUpdateView(UpdateView):
    model = Membership
    form_class = MembershipForm
    template_name = "memberships/membership_form.html"
    success_url = reverse_lazy("membership_list")

    def get_initial(self):
        # Set the initial user value from the URL parameter
        initial = super().get_initial()
        initial['user'] = self.object.user.pk  # Get user from existing Membership
        return initial


    def form_valid(self, form):
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('membership_list')


# Delete a membership
class MembershipDeleteView(DeleteView):
    model = Membership
    template_name = "memberships/membership_confirm_delete.html"
    success_url = reverse_lazy("membership_list")


def membership_list(request):
    active_memberships = Membership.objects.filter(status="Active")
    expired_memberships = Membership.objects.filter(status="Expired")

    return render(
        request,
        "memberships/membership_list.html",
        {"active_memberships": active_memberships, "expired_memberships": expired_memberships},
    )

@login_required
def user_profile_edit(request):
    user = request.user
    if request.method == "POST":
        form = UserProfileEditForm(request.POST, instance=user)  # Use the new form
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated!")
            return redirect('user_dashboard')  # Or wherever you want to redirect
    else:
        form = UserProfileEditForm(instance=user)  # Use the new form
    return render(request, "users/user_profile_edit.html", {"form": form})


#For the users
def membership_plans(request):
    """View to display membership plans to users."""
    membership_tiers = Membership.TIER_CHOICES
    membership_details = {}

    sample_user = CustomUser.objects.first()
    
    if not sample_user:
        return render(request, "memberships/membership_plans.html", {
            "membership_tiers": membership_tiers,
            "membership_details": {},
            "error_message": "No users found. Please create a user first.",
        })

    today = date.today()

    for tier, _ in membership_tiers:
        sample_membership = Membership(membership_type=tier, user=sample_user)
        sample_membership.price = {
            "Basic": 10.00,
            "Premium": 25.00,
            "Vip": 50.00
        }.get(tier, 10.00)

        sample_membership.start_date = today  # Set start_date to today

        membership_details[tier] = {
            'price': sample_membership.price,
            'duration': sample_membership.calculate_expiration_date() - sample_membership.start_date
        }

    return render(request, "memberships/membership_plans.html", {
        "membership_tiers": membership_tiers,
        "membership_details": membership_details,
        "today": today,
    })

@login_required
def user_membership_signup(request, tier):
    if request.method == 'POST':
        form = UserMembershipForm(request.POST)
        if form.is_valid():
            membership = form.save(commit=False)
            membership.user = request.user
            membership.save()  # Save the object first to set start_date
            membership.expiration_date = membership.calculate_expiration_date()  # Calculate expiration date after saving
            membership.save()  # Save again to update expiration_date
            return redirect('user_dashboard')
    else:
        form = UserMembershipForm(initial={'membership_type': tier})
    return render(request, 'users/user_membership_signup.html', {'form': form, 'tier': tier})

def promotions(request):
    today = timezone.now().date()
    active_promotions = Promotion.objects.filter(is_active=True, end_date__gte=today)
    return render(request, 'users/promotions.html', {
        'active_promotions': active_promotions,
    })

def admin_required(user):
    return user.is_authenticated and user.is_admin

@login_required
@user_passes_test(admin_required)
def admin_reviews(request):
    reviews = Review.objects.all().order_by('-created_at')
    return render(request, 'users/admin_reviews.html', {'reviews': reviews})


@csrf_exempt
@login_required
def save_chatbot_message(request):
    if request.method == "POST":
        data = json.loads(request.body)
        message = data.get("message")
        if message:
            ChatbotMessage.objects.create(user=request.user, message=message)
            return JsonResponse({"status": "success"})
        else:
            return JsonResponse({"status": "error", "message": "Message is required"})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"})
    

@login_required
@user_passes_test(admin_required) 
def chatbot_messages(request):
    messages = ChatbotMessage.objects.all().order_by('-timestamp')
    return render(request, 'bookings/chatbot_messages.html', {'messages': messages})