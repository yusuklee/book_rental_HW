from datetime import timedelta

from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from books.models import Book
from loans.models import Loan


@login_required
def borrow_book(request, book_id):
    book = get_object_or_404(Book, pk=book_id)

    overdue_cutoff = timezone.now() - timedelta(days=7)
    has_overdue = Loan.objects.filter(
        user=request.user,
        return_date__isnull=True,
        loan_date__lt=overdue_cutoff,
    ).exists()
    if has_overdue:
        messages.error(request, "연체된 도서가 있어 대출이 불가합니다. 먼저 반납하세요")
        return redirect("books:book_detail", pk=book_id)

    active_loans = Loan.objects.filter(user=request.user, return_date__isnull=True).count()
    if active_loans >= 3:
        messages.error(request, "최대 3권까지만 대여가능합니다")
        return redirect("books:book_detail", pk=book_id)

    already_borrowed = Loan.objects.filter(
        user=request.user,
        book_copy__book=book,
        return_date__isnull=True,
    ).exists()

    if already_borrowed:
        messages.error(request, "이미 같은 도서를 대여중입니다.")
        return redirect("books:book_detail", pk=book_id)

    available_copy = None
    for copy in book.copies.all():
        if copy.is_available:
            available_copy = copy
            break

    if not available_copy:
        messages.error(request, "현재 대출 가능한 복사본이 없습니다.")
        return redirect("books:book_detail", pk=book_id)

    if request.method == "POST":
        Loan.objects.create(user=request.user, book_copy=available_copy)
        messages.success(request, f"{book.title} #{available_copy.copy_number}를 대출함")
        return redirect("loans:history")
    return render(request, "loans/borrow_confirm.html", {
        "book": book,
        "copy": available_copy,
    })


@login_required
def return_book(request, loan_id):
    loan = get_object_or_404(Loan, pk=loan_id, user=request.user)
    if loan.return_date:
        messages.error(request, "이미 반납된 도서입니다.")
        return redirect("loans:history")
    if request.method == "POST":
        loan.return_date = timezone.now()
        loan.save()
        messages.success(request, f"{loan.book_copy.book.title} #{loan.book_copy.copy_number}를 반납했습니다.")
        return redirect("loans:history")
    return render(request, "loans/return_confirm.html", {"loan": loan})


@login_required
def loan_history(request):
    loans = Loan.objects.filter(user=request.user).order_by("-loan_date")
    now = timezone.now()
    overdue_cutoff = now - timedelta(days=7)

    loan_list = []
    for loan in loans:
        is_overdue = loan.return_date is None and loan.loan_date < overdue_cutoff
        loan_list.append({
            "loan": loan,
            "is_overdue": is_overdue,
        })
    return render(request, "loans/history.html", {"loan_list": loan_list})
