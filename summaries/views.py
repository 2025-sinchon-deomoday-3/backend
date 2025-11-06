# summaries/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import *
from .serializers import *


class DetailProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        detail_profile = self._get_detail_profile_or_none(request.user)
        if not detail_profile:
            return Response(
                {"message": "세부 프로필이 없습니다.", "data": None},
                status=status.HTTP_200_OK,
            )

        serializer = DetailProfileSerializer(detail_profile)
        return Response(
            {"message": "세부 프로필 조회 성공", "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        if self._get_detail_profile_or_none(request.user):
            return Response(
                {"message": "이미 세부 프로필이 존재합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = DetailProfileSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"message": "세부 프로필 생성 실패", "error": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save(user=request.user)
        return Response(
            {"message": "세부 프로필 생성 완료", "data": serializer.data},
            status=status.HTTP_201_CREATED,
        )

    def put(self, request):
        detail_profile = self._get_detail_profile_or_none(request.user)
        if not detail_profile:
            return Response(
                {"message": "수정할 세부 프로필이 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = DetailProfileSerializer(
            detail_profile,
            data=request.data,
            partial=True,
        )

        if not serializer.is_valid():
            return Response(
                {"message": "세부 프로필 수정 실패", "error": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save()
        return Response(
            {"message": "세부 프로필 수정 완료", "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    def _get_detail_profile_or_none(self, user):
        try:
            return user.summary_detail_profile
        except DetailProfile.DoesNotExist:
            return None