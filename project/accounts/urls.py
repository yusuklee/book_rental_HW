from django.urls import path
from accounts import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.login_view, name='login'),
    path("logout/", views.logout_view, name='logout'),
    path("register/", views.register_view, name='register'),
    path("members/", views.member_list, name='member_list'),
]
