from django import forms
from .models import WasteRequest
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class WasteRequestForm(forms.ModelForm):
    class Meta:
        model = WasteRequest
        fields = ['request_type', 'scrap_category', 'quantity', 'scrap_image', 'scheduled_date']
        widgets = {
            'scheduled_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'scrap_category': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Estimated Kg'}),
            'scrap_image': forms.FileInput(attrs={'class': 'form-control'}),
        }
        from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class CitizenRegistrationForm(UserCreationForm):
    phone_number = forms.CharField(max_length=15, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}))
    ward_number = forms.IntegerField(required=True, widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ward Number'}))
    address = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Address'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'ward_number', 'address']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }