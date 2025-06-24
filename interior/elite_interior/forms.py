from django import forms
from .models import BudgetItem

class BudgetCalculationForm(forms.Form):
    item = forms.ModelChoiceField(
        queryset=BudgetItem.objects.all(),
        empty_label="Select a budget item",
        widget=forms.Select(attrs={
        'class': 'form-select shadow-sm w-100',  # ✅ full width
        'aria-label': 'Select Budget Item',
        'style': 'max-width: 100%; min-width: 100%;'  # ✅ enforce full responsiveness
    })
    )
    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control shadow-sm',
            'placeholder': 'e.g. 10'
        })
    )
