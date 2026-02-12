from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class User(AbstractUser):
    is_admin = models.BooleanField(default=False, verbose_name="관리자 여부")

    class Meta:
        verbose_name = "사용자"      #관리자 페이지 이름
        verbose_name_plural = "사용자 목록"

    def __str__(self):
        return self.username
