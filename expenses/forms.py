from django import forms
from .models import Expense, Category


class ExpenseForm(forms.ModelForm):

    class Meta:
        model = Expense
        fields = ['title', 'amount', 'type', 'category', 'date', 'note']
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'e.g. Lunch at restaurant',
                'class': 'form-control'
            }),
            'amount': forms.NumberInput(attrs={
                'placeholder': '0.00',
                'class': 'form-control'
            }),
            'type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'note': forms.Textarea(attrs={
                'placeholder': 'Add a note (optional)',
                'class': 'form-control',
                'rows': 3
            }),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(user=user)
        self.fields['category'].empty_label = "Select category"