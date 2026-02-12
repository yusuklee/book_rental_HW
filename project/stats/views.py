import json
from datetime import timedelta

from django.db.models import Count
from django.shortcuts import render
from django.utils import timezone

from books.models import Category
from loans.models import Loan


def popular_books(request):
    three_months_ago = timezone.now() - timedelta(days=90)

    popular = (
        Loan.objects.filter(loan_date__gte=three_months_ago)
        .values("book_copy__book_id", "book_copy__book__title", "book_copy__book__author")
        .annotate(loan_count=Count("id"))
        .order_by("-loan_count")[:10]
    )

    selected_category = request.GET.get("category", "")
    categories = Category.objects.all()
    category_popular = []

    if selected_category:
        category_popular = (
            Loan.objects.filter(
                loan_date__gte=three_months_ago,
                book_copy__book__categories__id=selected_category,
            )
            .values("book_copy__book__id", "book_copy__book__title", "book_copy__book__author")
            .annotate(loan_count=Count("id"))
            .order_by("-loan_count")[:10]
        )

    max_count = popular[0]["loan_count"] if popular else 1

    return render(request, "stats/popular.html", {
        "popular": popular,
        "max_count": max_count,
        "categories": categories,
        "selected_category": selected_category,
        "category_popular": category_popular,
    })


def monthly_trends(request):
    now = timezone.now()
    months = []
    counts = []

    for i in range(11, -1, -1):
        year = now.year
        month = now.month - i
        while month <= 0:
            month += 12
            year -= 1
        next_month = month + 1
        next_year = year
        if next_month > 12:
            next_month = 1
            next_year = year + 1

        start = timezone.datetime(year, month, 1, tzinfo=timezone.get_current_timezone())
        end = timezone.datetime(next_year, next_month, 1, tzinfo=timezone.get_current_timezone())

        cnt = Loan.objects.filter(loan_date__gte=start, loan_date__lt=end).count()
        months.append(f"{year} - {month:02d}")
        counts.append(cnt)

    max_count = max(counts) if counts else 1

    return render(request, "stats/monthly.html", {
        "months": months,
        "counts": counts,
        "chart_data": zip(months, counts),
        "max_count": max_count,
        "months_json": json.dumps(months),
        "counts_json": json.dumps(counts),
    })


def category_ratio(request):
    data = (
        Loan.objects.values("book_copy__book__categories__name")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    labels = []
    values = []
    colors = [
        "#3498db", "#e74c3c", "#2ecc71", "#f39c12", "#9b59b6",
        "#1abc9c", "#e67e22", "#34495e", "#16a085", "#c0392b",
    ]

    total = sum(item["count"] for item in data if item["book_copy__book__categories__name"])
    chart_items = []

    for i, item in enumerate(data):
        name = item["book_copy__book__categories__name"]
        if name:
            labels.append(name)
            values.append(item["count"])
            pct = (item["count"] / total * 100) if total > 0 else 0
            chart_items.append({
                "name": name,
                "count": item["count"],
                "pct": round(pct, 1),
                "color": colors[i % len(colors)],
            })

    return render(request, "stats/category_ratio.html", {
        "chart_items": chart_items,
        "total": total,
        "labels_json": json.dumps(labels),
        "values_json": json.dumps(values),
    })
