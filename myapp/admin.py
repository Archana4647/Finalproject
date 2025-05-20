
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import UserProfile, TourPackage, Booking

# ============================
# 1. USER PROFILE ADMIN
# ============================
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'phone_number']
    list_filter = ['role']  # Filter by user/vendor
    search_fields = ['user__username', 'phone_number']


# ============================
# 2. INLINE USER PROFILE IN USER ADMIN
# ============================
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

# Unregister default User admin and register custom one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


# ============================
# 3. TOUR PACKAGE ADMIN
# ============================
@admin.register(TourPackage)
class TourPackageAdmin(admin.ModelAdmin):
    list_display = ['place', 'vendor', 'cost', 'is_approved', 'phonenumber']
    list_editable = ['is_approved']
    list_filter = ['is_approved', 'vendor']
    search_fields = ['place', 'vendor__username']


# ============================
# 4. BOOKING ADMIN
# ============================
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['user', 'package', 'status', 'booking_date']
    list_filter = ['status', 'booking_date']
    search_fields = ['user__username', 'package__place']
