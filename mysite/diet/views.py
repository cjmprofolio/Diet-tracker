import calendar
from datetime import datetime, timedelta
from django.shortcuts import  redirect
from django.urls import reverse_lazy
from .forms import MealModelForm
from .models import Meal
from django.views.generic import ListView, TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.db import connection
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

@method_decorator(login_required, name='dispatch')
class HomeView(TemplateView):
    template_name= 'diet/home.html'

    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)

        username= self.request.user.get_username()
        year= context.get('year') if context.get('year') else datetime.now().year
        month= context.get('month') if context.get('year') else datetime.now().strftime('%B')

        days_list= []
        tmp= []
        list_months= list(calendar.month_name)
        month_num= list_months.index(month)
        for d in calendar.Calendar(firstweekday=6).itermonthdays(year, month_num):
            if len(tmp) == 7:
                days_list.append(tmp)
                tmp= []
            tmp.append('' if d == 0 else d)
        days_list.append(tmp)

        # Set the value for previous an next button
        pre_mn, pre_yr= (list_months[12], year -1) if month_num -1 < 1 else (list_months[month_num-1], year)
        nxt_mn, nxt_yr= (list_months[1], year +1) if month_num +1 > 12 else (list_months[month_num+1], year)

        context.update({'username': username, 'year': year, 'month': month, 
                        'month_num':month_num,'days_list': days_list,
                        'pre_mn':pre_mn, 'pre_yr':pre_yr,
                        'nxt_mn':nxt_mn, 'nxt_yr':nxt_yr,
                        })
        return context

# Change format of date
def DateTransfer(kwargs):
    year= kwargs['year']
    month= list(calendar.month_name).index(kwargs['month'])
    day= int(kwargs['day'])

    return year, month, day

# Get weekrange from given date
# def WeekRange(date:datetime.date):

#     start_date= (date - timedelta(days= date.weekday())).date()
#     end_date= (start_date + timedelta(days= 6))

#     return start_date, end_date

# Transfer sql date into Queryset-like form
def DictFetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

class MealsListByDay(ListView):
    model= Meal
    template_name= 'diet/meals-by-day.html' 

    def get_queryset(self, *args, **kwargs):
        year, month, day= DateTransfer(self.kwargs)
        date= datetime(year, month, day).date().strftime('%Y-%m-%d')
        queries= {'date': date, 'username': self.request.user.get_username()}
        with connection.cursor() as cursor:
            cursor.execute("With rank_table AS\
                (SELECT *, RANK() OVER (\
                    PARTITION BY date >= date_trunc('week', %(date)s::date), \
                        date < date_trunc('week', %(date)s::date) + INTERVAL '7 days' ORDER BY calorie DESC) as rank FROM diet_meal)\
                    SELECT * FROM rank_table WHERE date= %(date)s and name = %(username)s",
                    params= queries)
            queryset= DictFetchall(cursor)
        return queryset

    def get_context_data(self, **kwargs):
        year, month, day= DateTransfer(self.kwargs)
        context= super().get_context_data(**kwargs)
        context['date']= datetime(year, month, day).strftime("%Y-%B-%d")
        para_dict= {'year': year, 'month': self.kwargs['month'], 'day': day}
        context.update(para_dict)
        return context

class AddMealView(CreateView):
    form_class= MealModelForm
    template_name= 'diet/add-meal.html'
    
    def get(self, request, *args, **kwargs):
        form = self.form_class(**kwargs)
        return self.render_to_response({'form': form})

    def post(self, *args, **kwargs):
        form= self.form_class(self.request.POST, **kwargs)
        if form.is_valid(): 
            form.instance.name = self.request.user.get_username()
            form.save()
            messages.success(self.request, 'Congrats!! You have updated your diet.')
            return redirect(self.get_success_url())
        else:
            messages.error(self.request, 'There is something wrong with your new diet. ...')
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('diet:meals-by-day', kwargs= self.kwargs)

class UpdateMealView(UpdateView):
    form_class= MealModelForm
    template_name= 'diet/update-meal.html'
    queryset= Meal.objects.all()

    def get(self, request, *args, **kwargs):
        pk= kwargs.pop('pk')
        meal= Meal.objects.get(pk= pk)
        form = self.form_class(**kwargs, instance= meal)
        return self.render_to_response({'form': form})
    
    def post(self, request, *args, **kwargs):
        pk= kwargs.pop('pk')
        meal= Meal.objects.get(pk= pk)
        form= self.form_class(request.POST, **kwargs, instance= meal)
        if form.is_valid():
            form.save()
            messages.success(self.request, 'Congrats!! You have updated your diet.')
            return redirect(self.get_success_url())
        else:
            messages.error(request, 'There is an error updating the diet.')
            return self.form_invalid(form)

    def get_success_url(self):
        self.kwargs.pop('pk')
        return reverse_lazy('diet:meals-by-day', kwargs= self.kwargs)

class DeleteMealView(DeleteView):
    model= Meal
    template_name= 'diet/delete-meal.html'

    def get_success_url(self):
        self.kwargs.pop('pk')
        return reverse_lazy('diet:meals-by-day', kwargs= self.kwargs)
    
@method_decorator(login_required, name='dispatch')
class MealList(ListView):
    model= Meal
    template_name= 'diet/meal-list.html'
    paginate_by= 50
    
    
    def get_queryset(self):
        queryset= self.model.objects.filter(name= self.request.user.get_username())
        # queryset= self.model.objects.raw('SELECT * FROM diet_meal WHERE name = %s', [self.request.user.get_username()])
        start_date= self.request.GET.get('start_date')
        end_date= self.request.GET.get('end_date')
        meal= self.request.GET.get('meal')
        food_name= self.request.GET.get('food_name')
        location= self.request.GET.get('location')
        q= Q()
        if start_date:
            q &= Q(date__gte=start_date)
        if end_date:
            q &= Q(date__lte=end_date)
        if meal:
            q &= Q(meal__contains=meal)
        if food_name:
            q &= Q(food_name__contains=food_name)
        if location:
            q &= Q(location__contains= location)
        queryset= queryset.filter(q)
        return queryset

    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        context['object_list']= self.get_queryset()
        return context

# function-based view
# def MealsByDay(request, *args, **kwargs):
#     year, month, day= GenerDate(kwargs)
#     date= datetime(year, month, day).strftime("%Y-%B-%d")
#     meals= Meal.objects.filter(date=datetime(year, month, day).date())
    
#     return render(request, 'diet/meals-by-day.html', 
#                     {'meals': meals,'year': year, 'month': list(calendar.month_name)[month], 'day':day
#                     ,'date': date })

# def AddMeal(request, *args, **kwargs):
#     if request.method == 'POST':
#         form= MealModelForm(request.POST, **kwargs)
#         form.save()
#         messages.success(request, 'Congrats!! You have updated your diet.')
#         return redirect(reverse('diet:meals-by-day', kwargs=kwargs))
#     else:     
#         form= MealModelForm(**kwargs)
#     return render(request, 'diet/add-meal.html', {'form': form})

# def UpdateMeal(request, *args, **kwargs):
#     id_= kwargs.pop('pk')
#     meal= Meal.objects.get(pk= id_)
#     form= MealModelForm(request.POST or None, **kwargs, instance= meal)
#     if form.is_valid():
#         form.save()
#         return redirect(reverse('diet:meals-by-day', kwargs= kwargs))
#     return render(request, 'diet/update-meal.html', {'form': form, 'k':kwargs})

# def DeleteMeal(request, *args, **kwargs):
#     id_= kwargs.pop('pk')
#     meal= Meal.objects.get(pk= id_)
#     messages.warning(request, 'You have deleted an meal record!')
#     meal.delete()
#     return redirect(reverse('diet:meals-by-day', kwargs= kwargs))
