from django.db import models

# Create your models here.

from accounts.models import User

class Loan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name="loans")
    book_copy = models.ForeignKey("books.BookCopy", on_delete=models.CASCADE, related_name="loans")
    loan_date = models.DateTimeField(auto_now_add=True)
    return_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        status = "반납 완료" if self.return_date else "대출중"
        return f"{self.user.username} - {self.book_copy} [{status}]"
