from django import forms
from .models import ReadingPlan, ReadingProgress, ReadingGoal

class ReadingPlanForm(forms.ModelForm):
    class Meta:
        model = ReadingPlan
        fields = ['book', 'start_date', 'target_end_date', 'daily_target_pages']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'target_end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['book'].queryset = user.book_set.all()

class ReadingProgressForm(forms.ModelForm):
    class Meta:
        model = ReadingProgress
        fields = ['pages_read']

class ReadingGoalForm(forms.ModelForm):
    class Meta:
        model = ReadingGoal
        fields = ['name', 'goal_type', 'target_amount', 'time_period', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }