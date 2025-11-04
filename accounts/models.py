from django.db import models
from django.contrib.auth.models import AbstractUser

#본교 
class University(models.Model):
    univ_name = models.CharField(max_length=120, unique=True)

    def __str__(self):
        return self.univ_name

#파견국 옵션 
class CountryOption(models.TextChoices):
        USA = "USA", "미국"
        JAPAN = "JAPAN", "일본"
        GERMANY = "GERMANY", "독일"
        FRANCE = "FRANCE", "프랑스"
        CHINA = "CHINA", "중국"
        TAIWAN = "TAIWAN", "대만"
        CANADA = "CANADA", "캐나다"
        ITALY = "ITALY", "이탈리아"
        NETHERLANDS = "NETHERLANDS", "네덜란드"
        UK = "UK", "영국"

#파견교 
class ExchangeUniversity(models.Model):    
    univ_name = models.CharField(max_length=120, unique=True)
    country = models.CharField(max_length=20, choices=CountryOption.choices);
    city = models.CharField(max_length=20)

    def __str__(self):
        return self.univ_name


#국가별 평균 예산안(DB용)
class AverageFee(models.Model):
    country = models.CharField(max_length=20, choices=CountryOption.choices);
    #KRW 기준으로 입력
    flight = models.IntegerField(default=0)
    insurance = models.IntegerField(default=0)
    visa = models.IntegerField(default=0)
    tuition = models.IntegerField(default=0)
    transport =  models.IntegerField(default=0) #평균 교통비
    food =  models.IntegerField(default=0) #평균 식비


#사용자 
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
    exchange_country = models.CharField(max_length=50, null=True, blank=True)
    exchange_type = models.CharField(max_length=20, choices=ExchangeType.choices, null=True, blank=True)
    exchange_semester = models.CharField(max_length=40, null=True, blank=True)
    exchange_period = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.exchange_univ.univ_name if self.exchange_univ else 'No Exchange University'}"