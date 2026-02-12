from django import forms

from books.models import Book, Category, Review


class BookForm(forms.ModelForm):
    num_copies = forms.IntegerField(
        label="복사본 수량",
        min_value=1,
        initial=1,
        help_text="등록할 물리적 책의 수량",
    )

    class Meta:
        model = Book
        fields = ("title", "author", "description", "categories")
        labels = {
            "title": "제목",
            "author": "저자",
            "description": "설명",
            "categories": "카테고리",
        }
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "도서 제목"}),
            "author": forms.TextInput(attrs={"placeholder": "저자명"}),
            "description": forms.Textarea(attrs={"placeholder": "도서 설명", "rows": 3}),
            "categories": forms.CheckboxSelectMultiple,
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ("name",)
        labels = {"name": "카테고리명"}
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "카테고리명을 입력하세요"}),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ("rating", "content")
        labels = {
            "rating": "평점",
            "content": "리뷰 내용",
        }
        widgets = {
            "rating": forms.Select(choices=[(i, f"{i}점") for i in range(1, 6)]),
            "content": forms.Textarea(attrs={"placeholder": "리뷰를 작성해주세요", "rows": 3}),
        }
