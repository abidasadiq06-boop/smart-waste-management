from django import forms
from .models import WasteRequest,ScrapCategory
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class WasteRequestForm(forms.ModelForm):
    class Meta:
        model = WasteRequest
        fields = ['request_type','scrap_category','quantity','scrap_image','scheduled_date','normal_waste_items']
        widgets = {
            'scheduled_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'scrap_category': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Estimated Kg'}),
            'scrap_image': forms.FileInput(attrs={'class': 'form-control'}),
        }
        from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

# forms.py
from django import forms
from django.contrib.auth.models import User

class CitizenRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
        required=True
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}),
        required=True
    )
    phone_number = forms.CharField(
        max_length=15, 
        required=True, 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    ward_number = forms.IntegerField(
        required=True, 
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=True
    )

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")

        # Check if passwords match
        if p1 and p2 and p1 != p2:
            self.add_error('password2', "Passwords do not match.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user



class ScrapCategoryForm(forms.ModelForm):
    class Meta:
        model = ScrapCategory
        fields = ['name', 'rate_per_kg']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'rate_per_kg': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        