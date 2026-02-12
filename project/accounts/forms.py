from django import forms
from django.contrib.auth.forms import AuthenticationForm
from accounts.models import User

ADMIN_NUM = "2023082524"

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="아이디",
        widget=forms.TextInput(attrs={'placeholder': "아이디를 입력하세요"}),
    )
    password = forms.CharField(
        label="비밀번호",
        widget=forms.PasswordInput(attrs={"placeholder": "비밀번호를 입력하세요"})
    )

class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(
        label="비밀번호",
        widget=forms.PasswordInput(attrs={"placeholder": "비밀번호"})
    )
    password2 = forms.CharField(
        label="비밀번호 확인",
        widget=forms.PasswordInput(attrs={'placeholder': '비밀번호 확인'}),
    )

    register_as_admin = forms.BooleanField(
        label="관리자로 가입 하시겠습니까?",
        required=False,
    )
    admin_num = forms.CharField(
        label="관리자 코드",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "관리자 가입시 10자리 코드 입력"}),
    )

    class Meta:
        model = User
        fields = ("username", "email")
        labels = {
            "username": "아이디",
            "email": "이메일",
        }
        widgets = {
            "username": forms.TextInput(attrs={"placeholder": "아이디"}),
            "email": forms.EmailInput(attrs={"placeholder": "이메일"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        pw1 = cleaned_data.get("password1")
        pw2 = cleaned_data.get("password2")
        if pw1 and pw2 and pw1 != pw2:
            raise forms.ValidationError("비밀번호가 일치 하지않습니다.")
        if cleaned_data.get("register_as_admin"):
            code = cleaned_data.get("admin_num", "")
            if len(code) != 10 or not code.isdigit():
                raise forms.ValidationError("관리자 인증번호는 10자리 숫자여야 합니다.")
            if code != ADMIN_NUM:
                raise forms.ValidationError("관리자 인증코드가 올바르지 않습니다.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if self.cleaned_data.get("register_as_admin"):
            user.is_admin = True
        if commit:
            user.save()
        return user
