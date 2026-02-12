from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from accounts.forms import LoginForm, RegisterForm
from accounts.models import User


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, "로그인 되었습니다.")
            return redirect("home")
    else:
        form = LoginForm()
    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    if request.method != "POST":
        return redirect("home")
    logout(request)
    messages.success(request, "로그 아웃 되었습니다.")
    return redirect("home")


def register_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "회원가입이 완료되었습니다.")
            return redirect("home")
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form})


@login_required
def member_list(request):
    if not request.user.is_admin:
        messages.error(request, "관리자만 접근할수 있습니다.")
        return redirect("home")
    members = User.objects.all().order_by("-date_joined")
    return render(request, "accounts/member_list.html", {"members": members})
