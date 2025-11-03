from django.db import models
from django.contrib.auth.models import AbstractUser


class University(models.Model):
    univ_name = models.CharField(max_length=120, unique=True)

    def __str__(self):
        return self.univ_name


class ExchangeUniversity(models.Model):
    univ_name = models.CharField(max_length=120, unique=True)
    country = models.CharField(max_length=50)

    def __str__(self):
        return self.univ_name


class User(AbstractUser):
    class Gender(models.TextChoices):
        MALE = "M", "남"
        FEMALE = "F", "여"
        OTHER = "O", "기타"
    
    nickname = models.CharField(max_length=50, unique=True)
    gender = models.CharField(max_length=20, choices=Gender.choices)
    univ = models.ForeignKey(University, on_delete=models.SET_NULL, null=True, blank=True, related_name="students")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username


class ExchangeProfile(models.Model):
    class ExchangeType(models.TextChoices):
        EXCHANGE = "EX", "교환학생"
        VISITING = "VS", "방문학생"
        OTHER = "OT", "기타"
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="exchange_profile")
    exchange_univ = models.ForeignKey(ExchangeUniversity, on_delete=models.SET_NULL, null=True, blank=True, related_name="exchange_students")
    exchange_country = models.ForeignKey(ExchangeUniversity, on_delete=models.SET_NULL, null=True, blank=True, related_name="exchange_country_students")
    exchange_type = models.CharField(max_length=20, choices=ExchangeType.choices, null=True, blank=True)
    exchange_semester = models.CharField(max_length=40, null=True, blank=True)
    exchange_period = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.exchange_univ.univ_name if self.exchange_univ else 'No Exchange University'}"