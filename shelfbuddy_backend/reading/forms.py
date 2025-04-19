from django import forms
from .models import ReadingPlan, ReadingProgress

class ReadingPlanForm(forms.ModelForm):
    class Meta:
        model = ReadingPlan
        fields = ['book', 'start_date', 'target_end_date', 'daily_target_pages']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'target_end_date': forms.DateInput(attrs={'type': 'date'}),
        }

class ReadingProgressForm(forms.ModelForm):
    class Meta:
        model = ReadingProgress
        fields = ['pages_read']