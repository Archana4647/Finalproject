
from django.db import models
from django.contrib.auth.models import User
import datetime
from datetime import date
from django.db.models.signals import post_save
from django.dispatch import receiver
import django.utils.timezone



class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('vendor', 'Vendor'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    phone_number = models.CharField(max_length=20, blank=True,null=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"



#tourpackage and booking

class TourPackage(models.Model):
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_staff': False})
    place = models.CharField(max_length=100)
    img = models.ImageField(upload_to='gallery/',blank=True,null=True)
    destinations = models.CharField(max_length=100, default='')
    description = models.TextField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.CharField(max_length=50, default='3 days')
    phonenumber = models.BigIntegerField(default=0)
    is_approved = models.BooleanField(default=False)
    package_start_date = models.DateField(default=date.today)
    package_end_date = models.DateField()
    transportation = models.CharField(max_length=100,blank=True)
    accommodation = models.CharField(max_length=100,blank=True)
    meals_included = models.BooleanField(default=False)
    booking_end_date = models.DateField(default=datetime.date.today)
    is_expired = models.BooleanField(default=False)


    def __str__(self):
        return self.place
    

#package image
class PackageImage(models.Model):
    package = models.ForeignKey(TourPackage, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='gallery/')
    uploaded_at = models.DateTimeField(auto_now_add=True)


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    package = models.ForeignKey(TourPackage, on_delete=models.CASCADE)
    booking_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Pending')

    def __str__(self):
        return f"{self.user.username} - {self.package.place}"
    


#vendor profile


class VendorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=100,default="N/A")
    contact_number = models.CharField(max_length=20,default="N/A")
    is_approved = models.BooleanField(default=True)  # Optional approval step

    def __str__(self):
        return self.company_name
    


#razorpay

class PackageBooking(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    package = models.ForeignKey('TourPackage', on_delete=models.CASCADE)
    razorpay_payment_id = models.CharField(max_length=100)
    razorpay_order_id = models.CharField(max_length=100)
    amount_paid = models.IntegerField()
    paid = models.BooleanField(default=False)
    full_name = models.CharField(max_length=100, blank=True,null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True ,null=True)
    booking_date = models.DateTimeField(default=django.utils.timezone.now)


class PackageReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    package = models.ForeignKey(TourPackage, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)




@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created and not hasattr(instance, 'userprofile'):
        UserProfile.objects.create(user=instance, role='user')  # default role
