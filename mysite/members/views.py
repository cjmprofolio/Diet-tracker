from django.shortcuts import render, redirect,resolve_url
from django.contrib.auth import login, authenticate
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.views.generic.edit import CreateView
from django.contrib.auth.views import LoginView, LogoutView 
from .forms import RegisterForm


class LoginUserView(LoginView):
    template_name= 'registration/login.html'

# class LogoutUserView(LogoutView):
#     next_page= reverse_lazy('members:login_user')
#     redirect_field_name = None

class Useregister(CreateView):
    template_name= 'registration/register.html'
    form_class= RegisterForm
    success_url= reverse_lazy('diet:home')

    def form_valid(self, form):
        response= super().form_valid(form)

        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)
        login(self.request, user)

        return response
    

# def login_user(request):
#     if request.method == 'POST':
#         username= request.POST.get('username')
#         password= request.POST.get('password')
#         user= authenticate(request, username= username, password= password)
#         if user:
#             login(request, user)
#             return redirect('home')
#         else:
#             messages.debug(request, 'There is an error logging in, Try again...')
#             return redirect('login_user')
#     else: 
#         return render(request, 'registration/login.html', {})

# def logout_user(request):
#     logout(request)
#     messages.success(request, 'You have alreadly logout successfully.')
#     return redirect('login_user')

# def login_user(request):
#     if request.method == 'POST':
#         form= AuthenticationForm(request, data= request.POST)
#         if form.is_valid():
#             user= form.get_user()
#             login(request, user)
#         else:
#             messages.warning(request, 'There is wrong with your username or password!!!')
#             redirect('registration/login')
#     else:
#         form= AuthenticationForm(request)
#     return render(request, 'registration/login.html', {'form':form, 'user':user})

# def logout_user(request):
#     logout(request)
#     messages.success(request, 'You have alreadly logout successfully.')
#     return redirect('diet/meal_list')
