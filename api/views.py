from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Sum
from datetime import datetime

from expenses.models import Expense, Category
from expenses.serializers import (
    ExpenseSerializer,
    CategorySerializer,
    ExpenseSummarySerializer,
    RegisterSerializer,
    UserProfileSerializer
)
from accounts.models import UserProfile


# ─── Auth ────────────────────────────────────────────────

class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message': 'Account created successfully!',
                'username': user.username
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ─── Profile ─────────────────────────────────────────────

class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile, _ = UserProfile.objects.get_or_create(
            user=request.user
        )
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request):
        profile, _ = UserProfile.objects.get_or_create(
            user=request.user
        )
        serializer = UserProfileSerializer(
            profile,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


# ─── Categories ──────────────────────────────────────────

class CategoryListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CategoryDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)


# ─── Expenses ────────────────────────────────────────────

class ExpenseListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Expense.objects.filter(
            user=self.request.user
        ).order_by('-date')

        # Filter by type
        expense_type = self.request.query_params.get('type')
        if expense_type in ['income', 'expense']:
            queryset = queryset.filter(type=expense_type)

        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__id=category)

        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)

        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(title__icontains=search)

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ExpenseDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user)


# ─── Summary ─────────────────────────────────────────────

class SummaryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = datetime.today()
        month = int(request.query_params.get('month', today.month))
        year = int(request.query_params.get('year', today.year))

        expenses = Expense.objects.filter(
            user=request.user,
            date__month=month,
            date__year=year
        )

        total_income = expenses.filter(
            type='income'
        ).aggregate(total=Sum('amount'))['total'] or 0

        total_expenses = expenses.filter(
            type='expense'
        ).aggregate(total=Sum('amount'))['total'] or 0

        balance = total_income - total_expenses

        # Category breakdown
        category_breakdown = expenses.filter(
            type='expense'
        ).values(
            'category__name',
            'category__icon'
        ).annotate(total=Sum('amount')).order_by('-total')

        return Response({
            'month': month,
            'year': year,
            'total_income': total_income,
            'total_expenses': total_expenses,
            'balance': balance,
            'category_breakdown': list(category_breakdown)
        })