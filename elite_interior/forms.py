from django import forms
from .models import BudgetItem

class BudgetCalculationForm(forms.Form):
    item = forms.ModelChoiceField(
        queryset=BudgetItem.objects.all(),
        empty_label="Select a budget item",
        widget=forms.Select(attrs={
        'class': 'form-select shadow-sm w-100 text-left',  # ✅ full width
        'aria-label': 'Select Budget Item',
        'style': 'max-width: 100%; min-width: 100%; text-align: left;'  # ✅ enforce full responsiveness
    })
    )
    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control shadow-sm',
            'placeholder': 'e.g. 10'
        })
    )





from .models import *

class ClientForm(forms.Form):
    client_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 'id': 'clientName', 'placeholder': 'e.g. John Doe'
    }))
    client_address = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control', 'id': 'clientAddress', 'placeholder': 'e.g. 123 Main St', 'style': 'max-height: 80px; min-height: 50px; max-width: 100%; min-width: 100%;'
    }))
    phone_number = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 'id': 'clientPhone', 'placeholder': 'e.g. +1 234 567 890'
    }))
    email_address = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control', 'id': 'clientEmail', 'placeholder': 'e.g. john@example.com'
    }))
    shop_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 'id': 'shopName', 'placeholder': 'e.g. My Shop'
    }))



class MaterialForm(forms.Form):
    design_place = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control bg-light', 'placeholder': 'e.g. Living Room'}))
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control product-select custom-product-select rounded-12 form-control', 'placeholder': 'e.g. Product playwood'})
    )
    height = forms.DecimalField(widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 200'}))
    width = forms.DecimalField(widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 100'}))
    qty = forms.DecimalField(widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 50'}))
    thickness = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 5mm'}),
    )
    unit = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. mm', 'readonly': True}),
    )

    category = forms.ModelChoiceField(
        queryset=ProductCategory.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control' , 'placeholder': 'e.g. Category wood'})
    )
    brand = forms.ModelChoiceField(
        queryset=Brand.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control' , 'placeholder': 'e.g. Brand A'})
    )
    origin = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. India','readonly': True}),
        required=False
    )
    series_type = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Series A', 'readonly': True}),
    )
    offer = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Offer %'}),
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'e.g. Description of the product'}),
        required=False
    )

