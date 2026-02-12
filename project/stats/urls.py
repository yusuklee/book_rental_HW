from django.urls import path
from stats import views

app_name = "stats"

urlpatterns = [
    path("popular/", views.popular_books, name="popular"),
    path("monthly/", views.monthly_trends, name="monthly"),
    path("category-ratio/", views.category_ratio, name="category_ratio"),
]

