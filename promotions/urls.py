from django.urls import path
from .views import promotion_list, add_promotion, edit_promotion, delete_promotion

urlpatterns = [
    path('', promotion_list, name='promotion_list'),
    path('add/', add_promotion, name='add_promotion'),
    path('<int:promo_id>/edit/', edit_promotion, name='edit_promotion'),
    path('<int:promo_id>/delete/', delete_promotion, name='delete_promotion'),
]
