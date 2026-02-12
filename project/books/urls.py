from django.urls import path
from books import views


app_name = "books"
urlpatterns = [
    path("", views.book_list, name="book_list"),
    path("<int:pk>/", views.book_detail, name="book_detail"),
    path("add/", views.book_add, name="book_add"),
    path("<int:pk>/edit/", views.book_edit, name="book_edit"),
    path("<int:pk>/delete/", views.book_delete, name="book_delete"),
    path("categories/", views.category_list, name="category_list"),
    path("categories/add/", views.category_add, name="category_add"),
    path("categories/<int:pk>/delete/", views.category_delete, name="category_delete"),
    path("<int:pk>/review/", views.review_add, name="review_add"),
]
