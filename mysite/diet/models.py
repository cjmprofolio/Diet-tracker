from django.db import models
from django.forms import ModelForm
from django import forms
from datetime import datetime
from django.utils.safestring import mark_safe

MEAL_CHOICES=[
    ('Breakfast', 'Breakfast'),
    ('Brunch', 'Brunch'),
    ('Lunch', 'Lunch'),
    ('Dinner', 'Dinner'),
    ('Dessert', 'Dessert'),
    ('Midnight Snack', 'Midnight Snack')
]
class Meal(models.Model):
    name= models.CharField(default= None,  max_length=20)
    date= models.DateField(default=datetime.today().date())
    meal= models.CharField(max_length=20, choices=MEAL_CHOICES, default='Breakfast')
    food_name= models.CharField(max_length=60)
    calorie= models.IntegerField(help_text='The unit is kcal')
    location= models.CharField(max_length=50, help_text='Enter the place you buy the food.')

    def __str__(self):
        return f'{self.date} {self.meal}'

class CalorieChart(models.Model):
    food_name= models.CharField(max_length=60)
    calorie= models.IntegerField()

    def __str__(self):
        return f'{self.food_name} {self.calorie}'