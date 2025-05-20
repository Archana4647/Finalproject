from datetime import date
from .models import TourPackage

def expire_old_packages():
    TourPackage.objects.filter(booking_end_date__lt=date.today()).update(is_expired=True)
