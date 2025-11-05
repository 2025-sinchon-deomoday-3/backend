from rest_framework import serializers
from .models import *
from django.db import transaction
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "password", "nickname", "gender"]


class AccountSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=30)
    password = serializers.CharField(write_only=True, max_length=255)
    passwordConfirm = serializers.CharField(write_only=True, max_length=255)
    nickname = serializers.CharField(max_length=50)
    gender = serializers.CharField(max_length=20)
    homeUniversity = serializers.CharField(max_length=120)

    def validate(self, attrs):
        password = attrs["password"]
        password_confirm = attrs["passwordConfirm"]

        if password != password_confirm:
            raise serializers.ValidationError({"passwordConfirm": "비밀번호 확인이 일치하지 않습니다."})

        if len(password) < 8:
            raise serializers.ValidationError({"password": "비밀번호는 8자 이상이어야 합니다."})

        username = attrs["username"].strip()
        nickname = attrs["nickname"].strip()

        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({"username": "이미 사용 중인 아이디입니다."})

        if User.objects.filter(nickname=nickname).exists():
            raise serializers.ValidationError({"nickname": "이미 사용 중인 닉네임입니다."})

        return attrs


class DispatchSerializer(serializers.Serializer):
    country = serializers.CharField(max_length=50)
    hostUniversity = serializers.CharField(max_length=120)
    dispatchType = serializers.CharField(max_length=20)
    term = serializers.CharField(max_length=40)
    duration = serializers.CharField(max_length=40)


class SignUpSerializer(serializers.Serializer):
    account = AccountSerializer()
    dispatch = DispatchSerializer()

    def _normalize_gender(self, raw: str) -> str:
        table = {
            "남성": "M",
            "남": "M",
            "여성": "F",
            "여": "F",
            "기타": "O",
            "other": "O",
        }
        cleaned = raw.strip()
        if cleaned in table:
            return table[cleaned]
        return "O"

    def _normalize_country_code(self, raw: str) -> str:
        cleaned = raw.strip()
        for code, label in CountryOption.choices:
            if cleaned == label:
                return code
            if cleaned.upper() == code:
                return code
        return cleaned.upper()

    def _country_label_from_code(self, code: str) -> str:
        for c, label in CountryOption.choices:
            if c == code:
                return label
        return code

    def _normalize_exchange_type(self, raw: str) -> str:
        cleaned = raw.strip()
        table = {
            "교환학생": "EX",
            "방문학생": "VS",
            "기타": "OT",
            "EX": "EX",
            "VS": "VS",
            "OT": "OT",
        }
        return table.get(cleaned, "OT")

    @transaction.atomic
    def create(self, validated_data):
        account_data = validated_data["account"]
        dispatch_data = validated_data["dispatch"]

        home_university_name = account_data["homeUniversity"].strip()
        home_university, _ = University.objects.get_or_create(
            univ_name=home_university_name
        )

        dispatch_country_code = self._normalize_country_code(dispatch_data["country"])
        dispatch_country_label = self._country_label_from_code(dispatch_country_code)

        host_university_name = dispatch_data["hostUniversity"].strip()
        exchange_university, _ = ExchangeUniversity.objects.get_or_create(
            univ_name=host_university_name,
            defaults={
                "country": dispatch_country_code,
                "city": "",
            },
        )
        if exchange_university.country != dispatch_country_code:
            exchange_university.country = dispatch_country_code
            exchange_university.save()

        user = User.objects.create(
            username=account_data["username"].strip(),
            nickname=account_data["nickname"].strip(),
            gender=self._normalize_gender(account_data["gender"]),
            univ=home_university,
        )
        user.set_password(account_data["password"])
        user.save()

        ExchangeProfile.objects.create(
            user=user,
            exchange_univ=exchange_university,
            exchange_country=dispatch_country_label,
            exchange_type=self._normalize_exchange_type(dispatch_data["dispatchType"]),
            exchange_semester=dispatch_data["term"].strip(),
            exchange_period=dispatch_data["duration"].strip(),
        )

        return user


class ExchangeProfileReadSerializer(serializers.ModelSerializer):
    hostUniversity = serializers.CharField(source="exchange_univ.univ_name", read_only=True)
    country = serializers.CharField(source="exchange_univ.country", read_only=True)

    class Meta:
        model = ExchangeProfile
        fields = [
            "exchange_type",
            "exchange_semester",
            "exchange_period",
            "hostUniversity",
            "country",
        ]


class UserReadSerializer(serializers.ModelSerializer):
    homeUniversity = serializers.CharField(source="univ.univ_name", read_only=True)
    dispatch = ExchangeProfileReadSerializer(source="exchange_profile", read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "nickname", "gender", "homeUniversity", "dispatch"]


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=64)
    password = serializers.CharField(max_length=128, write_only=True)

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            raise serializers.ValidationError("아이디와 비밀번호를 모두 입력해주세요.")

        if not User.objects.filter(username=username).exists():
            raise serializers.ValidationError("가입되지 않은 사용자입니다.")

        user = User.objects.get(username=username)
        if not user.check_password(password):
            raise serializers.ValidationError("잘못된 비밀번호입니다.")

        token = RefreshToken.for_user(user)
        refresh = str(token)
        access = str(token.access_token)

        return {
            "id": user.id,
            "username": user.username,
            "access_token": access,
            "refresh_token": refresh,
        }


class LogoutSerializer(serializers.Serializer):
    def validate(self, attrs):
        user = self.context["request"].user
        for token in OutstandingToken.objects.filter(user=user):
            BlacklistedToken.objects.get_or_create(token=token)
        return {"message": "성공적으로 로그아웃되었습니다."}


class UniversityListSerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = ["id", "univ_name"]


class ExchangeUniversityListSerializer(serializers.ModelSerializer):
    country = serializers.CharField()

    class Meta:
        model = ExchangeUniversity
        fields = ["id", "univ_name", "country"]