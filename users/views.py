from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from .forms import CustomUserCreationForm

# Create your views here.
def signup_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            login(request, form.save())
            return redirect("stalls:stall_list")
    else:    
        form = CustomUserCreationForm()
    return render(request, 'users/signup.html', { "form": form })

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect("users:gateway")
    else:    
        form = AuthenticationForm()
    return render(request, 'users/login.html', { "form": form })

def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("users:login")

def gateway(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(name="Food Stall Owners").exists():
            return redirect('stalls:select_stall')
        return redirect('stalls:stall_list')
    else:
        return redirect('users:login')