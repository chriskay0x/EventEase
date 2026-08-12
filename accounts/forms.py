from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, VendorProfile

class ClientRegistrationForm(UserCreationForm):
    phone = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={
        'placeholder': '+234 800 000 0000',
        'class': 'form-input'
    }))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Roles.CLIENT  # Or your choice field enum
        if commit:
            user.save()
        return user

class VendorRegistrationForm(UserCreationForm):
    phone = forms.CharField(max_length=20, required=True)
    business_name = forms.CharField(max_length=255, required=True)
    category = forms.ChoiceField(choices=[
        ('venue', 'Venue'),
        ('catering', 'Catering'),
        ('dj', 'DJ / Sound'),
    ])

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Roles.VENDOR
        if commit:
            user.save()
            VendorProfile.objects.create(
                user=user,
                business_name=self.cleaned_data['business_name'],
                category=self.cleaned_data['category']
            )
        return user

class CustomLoginForm(AuthenticationForm):
    username = forms.EmailField(label="Email Address")