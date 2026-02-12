from django.contrib import admin

from books.models import Category, Book, BookCopy, Review


@admin.register(Category)
class BookAdmin(admin.ModelAdmin):
    list_display = ("id","name")

class BookCopyInline(admin.TabularInline):
    model = BookCopy
    extra = 1

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("id","title","author")
    filter_horizontal = ("categories",)
    inlines = [BookCopyInline]

@admin.register(BookCopy)
class BookCopyAdmin(admin.ModelAdmin):
    list_display = ("id","book","copy_number")

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id","user","book","rating","created_at")
