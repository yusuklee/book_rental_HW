from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="카테고리명")

    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=200, verbose_name="제목")
    author = models.CharField(max_length=200, verbose_name="저자")
    description = models.TextField(blank=True)
    categories = models.ManyToManyField(Category, blank=True, related_name="books")

    def __str__(self):
        return f"{self.title} (저자: {self.author})"

    @property
    def total_copies(self):
        return self.copies.count()

    @property
    def available_copies(self):
        from loans.models import Loan
        on_loan = Loan.objects.filter(book_copy__book=self, return_date__isnull=True).count()
        return self.total_copies - on_loan

class BookCopy(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="copies")
    copy_number = models.PositiveIntegerField()

    class Meta:
        unique_together = [("book", "copy_number")]

    def __str__(self):
        return f"{self.book.title} #{self.copy_number}"

    @property
    def is_available(self):
        from loans.models import Loan
        return not Loan.objects.filter(book_copy=self, return_date__isnull=True).exists()

class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="reviews")
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("user", "book")]

    def __str__(self):
        return f"{self.user.username} - {self.book.title} ({self.rating}점)"
