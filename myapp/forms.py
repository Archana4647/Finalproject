


from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import VendorProfile , TourPackage ,PackageImage
from django.forms import modelformset_factory


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']





class VendorRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    company_name = forms.CharField(max_length=100)
    contact_number = forms.CharField(max_length=20)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            VendorProfile.objects.create(
                user=user,
                company_name=self.cleaned_data['company_name'],
                contact_number=self.cleaned_data['contact_number']
            )
        return user
    


#to add packages


class TourPackageForm(forms.ModelForm):
    class Meta:
        model = TourPackage
        # fields = ['title', 'description', 'price', 'duration']  # Add other fields as needed
        exclude = ['vendor','is_approved']


class PackageImageForm(forms.ModelForm):
    class Meta:
        model = PackageImage
        fields = ['image']

PackageImageFormSet = modelformset_factory(PackageImage, form=PackageImageForm, extra=5)




class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, label="Full Name")
    email = forms.EmailField(label="Email Address")
    phone = forms.CharField(max_length=20, required=False, label="Phone Number (optional)")
    subject = forms.CharField(max_length=200)
    message = forms.CharField(widget=forms.Textarea, label="Your Message")
