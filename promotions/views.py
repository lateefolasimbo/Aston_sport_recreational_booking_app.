from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Promotion
from .forms import PromotionForm

# Helper function to restrict access to admins only
def admin_required(user):
    return user.is_authenticated and user.is_admin

# List all promotions (Admin Only)
@login_required
@user_passes_test(admin_required)
def promotion_list(request):
    promotions = Promotion.objects.all()
    return render(request, 'promotions/promotion_list.html', {'promotions': promotions})

# Create a new promotion
@login_required
@user_passes_test(admin_required)
def add_promotion(request):
    if request.method == "POST":
        form = PromotionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Promotion added successfully!")
            return redirect('promotion_list')
    else:
        form = PromotionForm()
    return render(request, 'promotions/add_promotion.html', {'form': form})

# Edit an existing promotion
@login_required
@user_passes_test(admin_required)
def edit_promotion(request, promo_id):
    promotion = get_object_or_404(Promotion, id=promo_id)
    if request.method == "POST":
        form = PromotionForm(request.POST, instance=promotion)
        if form.is_valid():
            form.save()
            messages.success(request, "Promotion updated successfully!")
            return redirect('promotion_list')
    else:
        form = PromotionForm(instance=promotion)
    return render(request, 'promotions/add_promotion.html', {'form': form, 'promotion': promotion})

# Delete a promotion
@login_required
@user_passes_test(admin_required)
def delete_promotion(request, promo_id):
    promotion = get_object_or_404(Promotion, id=promo_id)
    if request.method == "POST":
        promotion.delete()
        messages.success(request, "Promotion deleted successfully!")
        return redirect('promotion_list')
    return render(request, 'promotions/delete_promotion.html', {'promotion': promotion})
