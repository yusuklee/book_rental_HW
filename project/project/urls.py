from django.contrib import admin
from django.urls import path, include
from books import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("accounts/", include("accounts.urls")),
    path("books/", include("books.urls")),
    path("loans/", include("loans.urls")),
    path("stats/", include("stats.urls")),
]
