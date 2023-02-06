from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Field, Submit, Row, Column, HTML


# Create your views here.

def login_user(request):
    if request.user.is_authenticated:
        return redirect(reverse('home'))
    form = AuthenticationForm(data=request.POST or None)
    form.helper = FormHelper()
    form.helper.add_input(Submit('login', 'Login', css_class='login-btn'))

    if request.method == 'POST':
        if form.is_valid():
            login(request, form.get_user())
            return redirect(reverse('home'))
        else:
            messages.error(request, 'Email o password non validi.')
    context = {'form': form}
    return render(request, 'users/login.html', context)

def logout_user(request):
    logout(request)
    return redirect(reverse('login'))