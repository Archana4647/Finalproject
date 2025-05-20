

from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import login,authenticate,logout
from django.contrib.auth.views import LoginView
from .forms import UserRegisterForm , VendorRegisterForm ,TourPackageForm
from django.contrib.auth.decorators import login_required
from .models import TourPackage, Booking ,VendorProfile,PackageReview,UserProfile
from django.http import HttpResponseForbidden
from django.contrib import messages
from datetime import date
from .utils import expire_old_packages
from .decorators import role_required
from django.http import HttpResponseForbidden
from .models import VendorProfile  # make sure this is imported
from django.contrib.auth.models import User
from django.forms import modelformset_factory
from .forms import  PackageImageFormSet
from .models import  PackageImage
from datetime import date
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, get_object_or_404
from django.shortcuts import render, get_object_or_404
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import PackageBooking
from .models import Booking, PackageBooking
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.core.mail import send_mail
from .forms import ContactForm
from django.shortcuts import redirect, get_object_or_404
from .models import  PackageReview
from django.contrib.auth.views import LogoutView



def index(request):
    return render(request,'index.html')

def about(request):
    return render(request, 'about.html')


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # auto login after registration
            return redirect('login')  # or any user home page
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})





@login_required
@role_required('user')
def user_dashboard(request):
    try:
        user_profile = request.user.userprofile
        if user_profile.role != 'user':
            messages.error(request, "You must register as a user to access the dashboard.")
            return redirect('register') 
    except UserProfile.DoesNotExist:
        messages.error(request, "You must register as a user to access the dashboard.")
        return redirect('register')

    #  existing user dashboard logic here...
    packages = TourPackage.objects.filter(is_approved=True, is_expired=False)
    destination = request.GET.get('destination')

    if destination:
        packages = packages.filter(destinations__icontains=destination)

    sort_by = request.GET.get('sort')
    if sort_by == 'cost_asc':
        packages = packages.order_by('cost')
    elif sort_by == 'cost_desc':
        packages = packages.order_by('-cost')
    elif sort_by == 'duration':
        packages = packages.order_by('duration')

    return render(request, 'dashboard.html', {'packages': packages})

    

@login_required
def book_package(request, package_id):
    package = get_object_or_404(TourPackage, id=package_id, is_approved=True)
    if package.vendor == request.user:
        messages.error(request,"you cannot book your own package.")
        return redirect('dashboard')
    Booking.objects.create(user=request.user, package=package)
    messages.success(request, "Booking successfull!")
    return redirect('dashboard')

#vender registration


def vendor_register(request):
    if request.method == 'POST':
        form = VendorRegisterForm(request.POST)
        if form.is_valid():
            # Check if user/email already exists as normal user
            email = form.cleaned_data.get('email')
            if UserProfile.objects.filter(user__email=email, role='user').exists():
                form.add_error(None, "You already have a user account. Cannot register as vendor.")
            else:
                user = form.save()
                VendorProfile.objects.get_or_create(user=user)
                messages.success(request, "Registration successful. Please log in.")
                return redirect('vendor_login')
    else:
        form = VendorRegisterForm()
    return render(request, 'vendor_register.html', {'form': form})




@login_required(login_url='vendor_login')
@role_required('vendor')
def vendor_dashboard(request):
    expire_old_packages()

    try:
        vendor_profile = VendorProfile.objects.get(user=request.user)
    except VendorProfile.DoesNotExist:
        messages.error(request, "You must register as a vendor to access the dashboard.")
        return redirect('vendor_register')

    # Mark expired
    TourPackage.objects.filter(booking_end_date__lt=date.today()).update(is_expired=True)
    packages = TourPackage.objects.filter(vendor=request.user)

    #  Move counts up here (always available)
    total_count = packages.count()
    approved_count = packages.filter(is_approved=True).count()
    pending_count = packages.filter(is_approved=False).count()

    if request.method == 'POST':
        form = TourPackageForm(request.POST, request.FILES)
        formset = PackageImageFormSet(request.POST, request.FILES, queryset=PackageImage.objects.none())

        if form.is_valid() and formset.is_valid():
            package = form.save(commit=False)
            package.vendor = request.user
            package.save()

            for image_form in formset:
                if image_form.cleaned_data:
                    image = image_form.save(commit=False)
                    image.package = package
                    image.save()

            messages.success(request, "Tour package and images added successfully (pending admin approval).")
            return redirect('vendor_dashboard')
    else:
        form = TourPackageForm()
        formset = PackageImageFormSet(queryset=PackageImage.objects.none())

    return render(request, 'vendor_dashboard.html', {
        'form': form,
        'formset': formset,
        'packages': packages,
        'total_packages': total_count,
        'approved_packages': approved_count,
        'pending_packages': pending_count,
        'today': date.today(),
    })




def vendor_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if VendorProfile.objects.filter(user=user).exists():
                login(request, user)
                return redirect('vendor_dashboard')  # Make sure this URL name is correct
            else:
                messages.error(request, 'You are not registered as a vendor.')
                return redirect('vendor_register')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()

    return render(request, 'vendor_login.html', {'form': form})



def package_detail(request, pk):
    # Fetching the approved tour package
    package = get_object_or_404(TourPackage, pk=pk, is_approved=True)

    # Razorpay setup
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    # Convert Decimal to int (in paise)
    amount = int(float(package.cost) * 100)  # Package cost in paise

    # Create Razorpay order
    razorpay_order = client.order.create({
        "amount": amount,
        "currency": "INR",
        "payment_capture": "1"
    })

    context = {
        "package": package,
        "razorpay_order_id": razorpay_order["id"],
        "razorpay_merchant_key": settings.RAZORPAY_KEY_ID,
        "amount": amount,
        "currency": "INR"
    }
    
    return render(request, "package_detail.html", context)



@csrf_exempt  # Required if Razorpay posts directly
@login_required
def payment_success(request):
    if request.method == "POST":
        razorpay_payment_id = request.POST.get("razorpay_payment_id")
        package_id = request.POST.get("package_id")  # You must pass this

        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")


        try:
            package = TourPackage.objects.get(id=package_id)
        except TourPackage.DoesNotExist:
            return render(request, "error.html", {"message": "Package not found."})

        # Create the booking
        PackageBooking.objects.create(
            user=request.user,
            package=package,
            paid=True,
            razorpay_payment_id=razorpay_payment_id,
            amount_paid=package.cost,

            full_name=full_name,
            email=email,
            phone=phone
        )

        return render(request, "payment_success.html", {"package": package})
    else:
        return render(request, "error.html", {"message": "Invalid request method."})



#  booked users

@login_required
def vendor_bookings(request):
    try:
        vendor_profile = VendorProfile.objects.get(user=request.user)
    except VendorProfile.DoesNotExist:
        return HttpResponseForbidden("You are not registered as a vendor.")

    # Bookings via direct/manual method
    manual_bookings = Booking.objects.filter(package__vendor=request.user).select_related('user', 'package')

    # Bookings via Razorpay (paid bookings)
    paid_bookings = PackageBooking.objects.filter(package__vendor=request.user, paid=True).select_related('user', 'package')

    return render(request, 'vendor_bookings.html', {
        'manual_bookings': manual_bookings,
        'paid_bookings': paid_bookings,
    })



class VendorLogoutView(LogoutView):
    def get_next_page(self):
        return '/vendor/login/'  # or use reverse('vendor_login') if it's named
    


def contact_page(request):
    if request.method == "POST":
        name = request.POST['name']
        email = request.POST['email']
        message = request.POST['message']

        send_mail(
            subject=f"Contact from {name}",
            message=message,
            from_email=email,
            recipient_list=[settings.DEFAULT_FROM_EMAIL],
        )
        return render(request, 'contact.html', {'success': True})
    return render(request, 'contact.html')



@login_required
def submit_review(request, package_id):
    if request.method == 'POST':
        package = get_object_or_404(TourPackage, id=package_id)
        rating = int(request.POST.get('rating'))
        comment = request.POST.get('comment')

        PackageReview.objects.create(
            user=request.user,
            package=package,
            rating=rating,
            comment=comment
        )
        return redirect('package_detail', pk=package.id)
    else:
        return redirect('package_detail',pk=package_id)
    


@login_required
def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            # Send email to admin/support
            send_mail(
                subject=f"Contact Form: {cd['subject']}",
                message=f"Message from {cd['name']} ({cd['email']}, {cd['phone']}):\n\n{cd['message']}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.CONTACT_EMAIL],  # Define this in your settings
                fail_silently=False,
            )
            return render(request, 'contact_success.html', {'name': cd['name']})
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})




@login_required
def custom_redirect(request):
    user = request.user
    if hasattr(user, 'vendorprofile'):
        return redirect('vendor_dashboard')
    elif hasattr(user, 'userprofile') and user.userprofile.role == 'user':
        return redirect('user_dashboard')
    else:
        return redirect('index')


#user logout view
def user_logout(request):
    logout(request)
    return redirect('user_logout.html') 


# Vendor logout view
def vendor_logout(request):
    logout(request)
    return redirect('vendor_logout.html') 