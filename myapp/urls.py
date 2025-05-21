# from django.urls import path
# from .import views as v

# urlpatterns=[
#     path('',v.home,name='home'),
#     path('register/',v.register,name='register'),
#     path('login/',v.loginn,name='loginn'),
# ]


from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views
from django.urls import reverse_lazy
from django.contrib.auth.views import LogoutView



urlpatterns = [

    
    path('',views.index,name='index'),
    path('about/', views.about, name='about'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page=reverse_lazy('index')), name='logout'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),  # simple placeholder
    path('book/<int:package_id>/', views.book_package, name='book_package'),
    path('vendor/register/', views.vendor_register, name='vendor_register'),
    path('vendor/dashboard/', views.vendor_dashboard, name='vendor_dashboard'),
    path('vendor/login/', views.vendor_login, name='vendor_login'),
    path('package/<int:pk>/',views.package_detail,name='package_detail'),
    path("payment/success/", views.payment_success, name="payment_success"),
    path('vendor/bookings/', views.vendor_bookings, name='vendor_bookings'),
    path('vendor/logout/', LogoutView.as_view(next_page=reverse_lazy('vendor_login')), name='vendor_logout'),
    path('contact/', views.contact_view, name='contact'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('package/<int:pk>/', views.package_detail, name='package_detail'),
    path('package/<int:package_id>/review/', views.submit_review, name='submit_review'),
    path('custom-redirect/', views.custom_redirect, name='custom_redirect'),
     path('user/logout/', auth_views.LogoutView.as_view(), name='user_logout'),
    path('vendor/logout/', views.vendor_logout, name='vendor_logout'),
    path('test-auth/', views.test_auth, name='test_auth'),

]


