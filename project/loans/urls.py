from loans import views
from django.urls import path
app_name = "loans"

urlpatterns = [
    path("borrow/<int:book_id>/", views.borrow_book, name="borrow"),
    path("return/<int:loan_id>/", views.return_book,name="return"),
    path("history/", views.loan_history, name="history"), #url 연결할 함수 url 별칭
    
]
