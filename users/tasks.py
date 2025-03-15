from celery import shared_task
from django.utils import timezone
from .models import Membership

@shared_task
def check_and_renew_memberships():
    today = timezone.now().date()
    expired_memberships = Membership.objects.filter(status="expired", auto_renew=True)

    for membership in expired_memberships:
        if membership.auto_renew:
            if membership.membership_type == "basic":
                membership.expiration_date = today + timezone.timedelta(days=30)
            elif membership.membership_type == "premium":
                membership.expiration_date = today + timezone.timedelta(days=90)
            elif membership.membership_type == "vip":
                membership.expiration_date = today + timezone.timedelta(days=180)
            
            membership.status = "active"
            membership.save()
