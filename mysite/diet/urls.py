from django.urls import path, include
from . import views
from .views import HomeView, MealList, MealsListByDay, AddMealView, UpdateMealView, DeleteMealView

app_name= 'diet'

urlpatterns = [
    path('', HomeView.as_view(), name= 'home'),
    path('diet/', include([
        path('<int:year>/<str:month>/', HomeView.as_view(), name= 'home'),
        path('<int:year>/<str:month>/<int:day>/', MealsListByDay.as_view(), name='meals-by-day'),
        path('<int:year>/<str:month>/<int:day>/update_meal/<int:pk>', UpdateMealView.as_view(), name='update-meal'),
        path('<int:year>/<str:month>/<int:day>/add_meal/', AddMealView.as_view(), name='add-meal'),
        path('<int:year>/<str:month>/<int:day>/delete_meal/<int:pk>', DeleteMealView.as_view(), name='delete-meal'),
        path('meal_list', MealList.as_view(), name='meal-list'),]
    ))
] 