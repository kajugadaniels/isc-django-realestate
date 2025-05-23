import random
from django import forms
from backend.models import *
from django.contrib.auth import authenticate
from dateutil.relativedelta import relativedelta
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import validate_password

class LoginForm(forms.Form):
    ROLE_CHOICES = (
        ('Admin', 'Admin'),
        ('User', 'User'),
        ('House Provider', 'House Provider'),
    )

    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.RadioSelect(attrs={
            'required': 'required',
            'class': 'checkbox1',
            'type': 'radio',
            'id': 'role',
        }),
        label=_('Role'),
        error_messages={
            'required': _('Please select your role.'),
        }
    )

    email = forms.EmailField(
        max_length=255,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email',
            'required': 'required',
            'id': 'emailaddress',
        }),
        label=_('Email Address'),
        error_messages={
            'required': _('Please enter your email address.'),
            'invalid': _('Enter a valid email address.'),
        }
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
            'required': 'required',
            'id': 'password',
        }),
        label=_('Password'),
        error_messages={
            'required': _('Please enter your password.'),
        }
    )

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password and role:
            user = authenticate(email=email, password=password)
            if not user:
                raise forms.ValidationError(_('The email or password you entered is incorrect. Please try again.'))
            if not user.is_active:
                raise forms.ValidationError(_('Your account is currently inactive. Please contact support for assistance.'))
            if user.role != role:
                raise forms.ValidationError(_('The role does not match with the email and password entered.'))
            cleaned_data['user'] = user
        else:
            if not email:
                self.add_error('email', _('Email address is required.'))
            if not password:
                self.add_error('password', _('Password is required.'))
            if not role:
                self.add_error('role', _('Role is required.'))

        return cleaned_data

class RegisterForm(forms.ModelForm):
    """
    Form for registering a new user with role 'User' by default.
    """
    ROLE_CHOICES = (
        ('Admin', 'Admin'),
        ('User', 'User'),
        ('House Provider', 'House Provider'),
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter Password',
            'class': 'form-control',
            'required': 'required',
            'id': 'password',
        }),
        label=_('Password'),
        error_messages={'required': _('Please enter a password.')},
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm Password',
            'required': 'required',
            'class': 'form-control',
            'id': 'confirm_password',
        }),
        label=_('Confirm Password'),
        error_messages={'required': _('Please confirm your password.')},
    )
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.RadioSelect(attrs={
            'required': 'required',
            'id': 'role',
        }),
        label=_('Role'),
        error_messages={'required': _('Please select your role.')},
    )

    class Meta:
        model = User
        fields = ['name', 'email', 'phone_number']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Enter your name',
                'required': 'required',
                'class': 'form-control',
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Enter your email address',
                'required': 'required',
                'class': 'form-control',
            }),
            'phone_number': forms.TextInput(attrs={
                'placeholder': 'Enter your phone number',
                'required': 'required',
                'class': 'form-control',
            }),
        }
        labels = {
            'name': _('Name'),
            'email': _('Email Address'),
            'phone_number': _('Phone Number'),
        }
        error_messages = {
            'name': {'required': _('Please enter your name.')},
            'email': {
                'required': _('Please enter your email address.'),
                'invalid': _('Enter a valid email address.'),
            },
            'phone_number': {'required': _('Please enter your phone number.')},
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password:
            if password != confirm_password:
                self.add_error('confirm_password', _('The passwords do not match.'))
            try:
                validate_password(password)
            except forms.ValidationError as error:
                self.add_error('password', error)
        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_('This email address is already in use.'))
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if User.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError(_('This phone number is already in use.'))
        return phone_number

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.role = self.cleaned_data["role"]  # Set the role selected by the user
        if commit:
            user.save()
        return user

class UserProfileForm(forms.ModelForm):
    """
    Form for updating user profile information.
    """
    class Meta:
        model = User  # Ensure you have imported the User model
        fields = ['name', 'email', 'phone_number', 'image']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your full name',
                'required': 'required',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email address',
                'required': 'required',
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your phone number',
                'required': 'required',
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control',
            }),
        }
        labels = {
            'name': _('Full Name'),
            'email': _('Email Address'),
            'phone_number': _('Phone Number'),
            'image': _('Profile Image'),
        }
        error_messages = {
            'name': {
                'required': _('Please enter your full name.'),
                'max_length': _('Name cannot exceed 255 characters.'),
            },
            'email': {
                'required': _('Please enter your email address.'),
                'invalid': _('Enter a valid email address.'),
                'unique': _('This email address is already in use.'),
            },
            'phone_number': {
                'required': _('Please enter your phone number.'),
                'unique': _('This phone number is already in use.'),
                'max_length': _('Phone number cannot exceed 15 characters.'),
            },
            'image': {
                'invalid': _('Please upload a valid image file.'),
            },
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(_('This email address is already in use. Please use a different one.'))
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if User.objects.filter(phone_number=phone_number).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(_('This phone number is already in use. Please use a different one.'))
        return phone_number

class PasswordChangeForm(forms.Form):
    """
    Form for changing user password.
    """
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your current password',
            'required': 'required',
            'id': 'current_password',
        }),
        label=_('Current Password'),
        error_messages={
            'required': _('Please enter your current password.'),
        }
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your new password',
            'required': 'required',
            'id': 'new_password',
        }),
        label=_('New Password'),
        help_text=_('Your password must contain at least 8 characters, including a mix of letters, numbers, and symbols.'),
        error_messages={
            'required': _('Please enter a new password.'),
        }
    )
    confirm_new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your new password',
            'required': 'required',
            'id': 'confirm_new_password',
        }),
        label=_('Confirm New Password'),
        error_messages={
            'required': _('Please confirm your new password.'),
        }
    )

    def __init__(self, user, *args, **kwargs):
        """
        Initialize the form with the current user.
        """
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if not self.user.check_password(current_password):
            raise forms.ValidationError(_('Your current password was entered incorrectly. Please enter it again.'))
        return current_password

    def clean_new_password(self):
        new_password = self.cleaned_data.get('new_password')
        validate_password(new_password, self.user)
        return new_password

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_new_password = cleaned_data.get('confirm_new_password')

        if new_password and confirm_new_password:
            if new_password != confirm_new_password:
                self.add_error('confirm_new_password', _('The new passwords do not match. Please enter them again.'))

        return cleaned_data

class HouseProviderUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password',
            'required': 'required',
        }),
        label=_("Password"),
        help_text=_("Enter a strong password."),
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password',
            'required': 'required',
        }),
        label=_("Confirm Password"),
        help_text=_("Enter the same password for confirmation."),
    )

    class Meta:
        model = User
        # Exclude the 'role' field; we only create House Provider users.
        fields = ['name', 'email', 'phone_number', 'image']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter full name',
                'required': 'required',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter email address',
                'required': 'required',
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter phone number',
                'required': 'required',
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control',
            }),
        }
        labels = {
            'name': _('Full Name'),
            'email': _('Email Address'),
            'phone_number': _('Phone Number'),
            'image': _('Profile Image'),
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(_("The two password fields didn’t match."))
            validate_password(password1)
        return password2

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_("A user with this email already exists."))
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        # Force the role to "House Provider"
        user.role = "House Provider"
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class AmenityForm(forms.ModelForm):
    """
    Form for creating and updating Amenity instances.
    """
    class Meta:
        model = Amenity
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter amenity name',
                'required': 'required',
            }),
        }
        labels = {
            'name': _('Amenity Name'),
        }
        error_messages = {
            'name': {
                'required': _('Please enter the amenity name.'),
                'max_length': _('Amenity name cannot exceed 255 characters.'),
            },
        }

# forms.py

from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Property, Category, Amenity

class PropertyForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        empty_label=_('Select a Category'),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'required': 'required',
        })
    )

    class Meta:
        model = Property
        fields = [
            'name', 'city', 'type', 'category', 'description',
            'price_usd', 'price_rwf', 'bathroom', 'capacity',
            'address', 'size', 'image', 'amenities',
            'nearby_hospital', 'nearby_school', 'nearby_market',
            'nearby_transport', 'nearby_park', 'nearby_gym',
            # newly added model fields:
            'location', 'map_embed', 'video_url', 'video_thumbnail',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter property name',
                'required': 'required',
            }),
            'city': forms.Select(attrs={
                'class': 'form-control',
                'required': 'required',
            }),
            'type': forms.Select(attrs={
                'class': 'form-control',
                'required': 'required',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter property description',
                'required': 'required',
            }),
            'price_usd': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter price in USD',
            }),
            'price_rwf': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter price in RWF',
            }),
            'bathroom': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter number of bathrooms',
                'required': 'required',
            }),
            'capacity': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter number of rooms',
                'required': 'required',
            }),
            'size': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter property size',
                'required': 'required',
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter property address',
                'required': 'required',
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control',
            }),
            'amenities': forms.SelectMultiple(attrs={
                'class': 'form-control',
                'required': 'required',
            }),
            'nearby_hospital': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter nearby hospital details',
            }),
            'nearby_school': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter nearby school details',
            }),
            'nearby_market': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter nearby market details',
            }),
            'nearby_transport': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter nearby transport details',
            }),
            'nearby_park': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter nearby park details',
            }),
            'nearby_gym': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter nearby gym details',
            }),
            # new field widgets
            'location': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter more precise location or coordinates',
                'rows': 2,
            }),
            'map_embed': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Paste your Google Maps iframe HTML here',
                'rows': 3,
            }),
            'video_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter URL for property video (e.g. YouTube)',
            }),
            'video_thumbnail': forms.ClearableFileInput(attrs={
                'class': 'form-control',
            }),
        }
        labels = {
            'name': _('Property Name'),
            'city': _('Property City'),
            'type': _('Property Type'),
            'category': _('Property Category'),
            'description': _('Description'),
            'price_usd': _('Price (USD)'),
            'price_rwf': _('Price (RWF)'),
            'bathroom': _('Number of Bathrooms'),
            'capacity': _('Number of Rooms'),
            'size': _('Size in sqf'),
            'address': _('Property Address'),
            'image': _('Property Image'),
            'amenities': _('Amenities'),
            'nearby_hospital': _('Nearby Hospital'),
            'nearby_school': _('Nearby School'),
            'nearby_market': _('Nearby Market'),
            'nearby_transport': _('Nearby Transport'),
            'nearby_park': _('Nearby Park'),
            'nearby_gym': _('Nearby Gym'),
            # new labels
            'location': _('Nearby Location'),
            'map_embed': _('Map Embed Code'),
            'video_url': _('Video URL'),
            'video_thumbnail': _('Video Thumbnail'),
        }
        error_messages = {
            'name': {
                'required': _('Please enter the property name.'),
                'max_length': _('Property name cannot exceed 255 characters.'),
            },
            'description': {
                'required': _('Please enter the property description.'),
            },
            'capacity': {
                'required': _('Please enter the capacity.'),
            },
        }

class ContractForm(forms.ModelForm):
    """
    Form for creating a rental contract, with the automatic population of certain fields.
    """
    class Meta:
        model = Contract
        fields = [
            'start_date', 'end_date', 'additional_terms', 'rent_due_date',
            'payment_method', 'rent_amount', 'security_deposit', 'rental_period_months'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'additional_terms': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'rent_due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'payment_method': forms.TextInput(attrs={'class': 'form-control'}),
            'rent_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'security_deposit': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Keep the rental_period_months field hidden (it will be handled by JS)
        self.fields['rental_period_months'].required = False
