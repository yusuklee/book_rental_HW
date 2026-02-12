from django.contrib import admin

from loans.models import Loan


# Register your models here.

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ("id","user","book_copy","loan_date","return_date")
    list_filter = ("return_date",)
