from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from .models import * 
from .serializers import *
from django.conf import settings
from rest_framework import status

# Create your views here.
"""
    views.py
    ├── BudgetView         → 예산안 CRUD
    ├── BaseBudgetView     → 기본 파견비 조회/등록
    ├── BaseBudgetItemView → 기본 파견비 항목 CRUD
    ├── LivingBudgetView   → 생활비 조회/등록
    └── LivingBudgetItemView → 생활비 항목 CRUD
"""

#예산안 전체 조회 및 등록
class BudgetView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    #조회
    def get(self, request):
        budget = Budget.objects.filter(user=request.user).first()
        serilizer = BudgetSerializer(budget)
        return Response(serilizer.data)
    #등록 
    def post(self, request):
        budget, created = Budget.objects.get_or_create(user=request.user)

        serializer = BudgetSerializer(budget, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK if not created else status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



#기본 파견비 조회 및 등록
class BaseBudgetView(APIView):
    permission_classes = [permissions.AllowAny]

    #조회
    def get(self, request):
        budget = Budget.objects.filter(user=request.user).first()
        base_budget = budget.base_budget
        serializer = BaseBudgetSerializer(base_budget)
        return Response(serializer.data)
    
    #등록
    def post(self, request):
        budget, _ = Budget.objects.get_or_create(user=request.user)
        serializer = BaseBudgetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(budget=budget)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
#생활비 조회 및 등록
class LivingBudgetView(APIView):
    permission_classes = [permissions.AllowAny]

    #조회
    def get(self, request):
        budget = Budget.objects.filter(user=request.user).first()
        living_budget = budget.living_budget
        serializer = LivingBudgetSerializer(living_budget)
        return Response(serializer.data)
    

    #등록
    def post(self, request):
        budget, _ = Budget.objects.get_or_create(user=request.user)
        serializer = LivingBudgetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(budget=budget)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)



    
    


