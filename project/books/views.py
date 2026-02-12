from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.shortcuts import render, get_object_or_404, redirect

from books.models import Book, BookCopy, Category, Review
from books.forms import BookForm, CategoryForm, ReviewForm


def home(request):
    recent_books = Book.objects.all().order_by("-id")[:5]
    return render(request, "books/home.html", {"recent_books": recent_books})


def book_list(request):
    books = Book.objects.all()

    query = request.GET.get("q", "")
    search_type = request.GET.get("search_type", "title")
    sort_by = request.GET.get('sort', "title")
    category_id = request.GET.get("category", "")

    if query:
        if search_type == 'title':
            books = books.filter(title__icontains=query)
        elif search_type == "author":
            books = books.filter(author__icontains=query)
        elif search_type == "category":
            books = books.filter(categories__name__icontains=query)

    if category_id:
        books = books.filter(categories__id=category_id)

    books = books.distinct()

    if sort_by == "title":
        books = books.order_by("title")
    elif sort_by == "author":
        books = books.order_by("author")
    elif sort_by == "id_desc":
        books = books.order_by("-id")

    categories = Category.objects.all()
    return render(request, "books/book_list.html", {
        "books": books,
        "categories": categories,
        "query": query,
        "search_type": search_type,
        "sort_by": sort_by,
        "selected_category": category_id,
    })


def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    copies = book.copies.all()
    reviews = book.reviews.all().order_by("-created_at")
    avg_rating = reviews.aggregate(avg=Avg("rating"))["avg"]

    can_review = False
    if request.user.is_authenticated:
        from loans.models import Loan
        has_returned = Loan.objects.filter(
            user=request.user,
            book_copy__book=book,
            return_date__isnull=False,
        ).exists()
        already_reviewed = Review.objects.filter(user=request.user, book=book).exists()
        can_review = has_returned and not already_reviewed

    return render(request, "books/book_detail.html", {
        "book": book,
        "copies": copies,
        "reviews": reviews,
        "avg_rating": avg_rating,
        "can_review": can_review,
    })


@login_required
def book_add(request):
    if not request.user.is_admin:
        messages.error(request, "관리자만 접근 가능합니다.")
        return redirect("books:book_list")
    if request.method == "POST":
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save()
            num_copies = form.cleaned_data['num_copies']
            for i in range(1, num_copies + 1):
                BookCopy.objects.create(book=book, copy_number=i)
            messages.success(request, f"{book.title}이 {num_copies}권으로 등록되었습니다.")
            return redirect("books:book_list")
    else:
        form = BookForm()
    return render(request, "books/book_form.html", {"form": form, "title": "도서 추가"})


@login_required
def book_edit(request, pk):
    if not request.user.is_admin:
        messages.error(request, "관리자만 접근 가능합니다.")
        return redirect("books:book_list")
    book = get_object_or_404(Book, pk=pk)
    if request.method == "POST":
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            book = form.save()
            num_copies = form.cleaned_data["num_copies"]
            current_count = book.copies.count()
            if num_copies > current_count:
                for i in range(current_count + 1, num_copies + 1):
                    BookCopy.objects.create(book=book, copy_number=i)
            messages.success(request, f"{book.title}이 수정되었습니다.")
            return redirect("books:book_detail", pk=book.pk)
    else:
        form = BookForm(instance=book, initial={'num_copies': book.copies.count()})
    return render(request, "books/book_form.html", {"form": form, "title": "도서 수정"})


@login_required
def book_delete(request, pk):
    if not request.user.is_admin:
        messages.error(request, "관리자만 접근가능")
        return redirect("books:book_list")
    book = get_object_or_404(Book, pk=pk)
    if request.method == "POST":
        title = book.title
        book.delete()
        messages.success(request, f"{title}이 삭제 되었습니다.")
        return redirect("books:book_list")
    return render(request, "books/book_confirm_delete.html", {"book": book})


@login_required
def category_list(request):
    if not request.user.is_admin:
        messages.error(request, "관리자만 접근가능")
        return redirect("home")
    categories = Category.objects.all().order_by("name")
    return render(request, "books/category_list.html", {"categories": categories})


@login_required
def category_add(request):
    if not request.user.is_admin:
        messages.error(request, "관리자만 접근 가능")
        return redirect("home")
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "카테고리가 추가되었습니다.")
            return redirect("books:category_list")
    else:
        form = CategoryForm()
    return render(request, "books/category_form.html", {"form": form})


@login_required
def category_delete(request, pk):
    if not request.user.is_admin:
        messages.error(request, "관리자만 접근 가능")
        return redirect("home")
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, "카테고리가 삭제 되었습니다.")
        return redirect("books:category_list")
    return render(request, "books/category_confirm_delete.html", {"category": category})


@login_required
def review_add(request, pk):
    book = get_object_or_404(Book, pk=pk)
    from loans.models import Loan
    has_returned = Loan.objects.filter(
        user=request.user,
        book_copy__book=book,
        return_date__isnull=False,
    ).exists()
    if not has_returned:
        messages.error(request, "반납 완료한 도서만 리뷰작성이 가능합니다.")
        return redirect("books:book_detail", pk=pk)
    if Review.objects.filter(user=request.user, book=book).exists():
        messages.error(request, "이미 리뷰를 작성한 도서입니다.")
        return redirect("books:book_detail", pk=pk)
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.book = book
            review.save()
            messages.success(request, "리뷰가 등록되었습니다.")
            return redirect("books:book_detail", pk=pk)
    else:
        form = ReviewForm()
    return render(request, "books/review_form.html", {"form": form, "book": book})
