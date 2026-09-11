from django import forms
from .models import WasteRequest

class WasteRequestForm(forms.ModelForm):
    class Meta:
        model = WasteRequest
        fields = ['request_type', 'scrap_category', 'quantity', 'scrap_image', 'scheduled_date']
        widgets = {
            'scheduled_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'request_type': forms.Select(attrs={'class': 'form-control'}),
            'scrap_category': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantity in kg'}),
            'scrap_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }