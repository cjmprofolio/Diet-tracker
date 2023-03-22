from django import forms
from django.forms import ModelForm
from .models import Meal
from datetime import datetime

# Create MealForm
class MealModelForm(ModelForm):
    
    class Meta:
        model= Meal
        fields= ['date', 'meal', 'food_name', 'calorie', 'location']

        widgets={
            'date':forms.SelectDateWidget(attrs={'class':'form-control'}),
            'meal':forms.Select(attrs={'class':'form-control'}),
            'food_name':forms.TextInput(attrs={'class':'form-control'}),
            'location':forms.TextInput(attrs={'class':'form-control'})
        }
    
    def __init__(self,  *args, **kwargs):
        self.year= kwargs.pop('year')
        self.month= kwargs.pop('month')
        self.day= kwargs.pop('day')
        super(MealModelForm, self).__init__(*args, **kwargs)
        self.fields['date'].initial= datetime.strptime(f'{self.year}-{self.month}-{self.day}', "%Y-%B-%d")
