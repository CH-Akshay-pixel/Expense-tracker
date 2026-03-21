from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from . import views

urlpatterns = [

    # Auth
    path('auth/register/', views.RegisterAPIView.as_view(), name='api_register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='api_login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='api_refresh'),

    # Profile
    path('profile/', views.ProfileAPIView.as_view(), name='api_profile'),

    # Categories
    path('categories/', views.CategoryListCreateAPIView.as_view(), name='api_categories'),
    path('categories/<int:pk>/', views.CategoryDetailAPIView.as_view(), name='api_category_detail'),

    # Expenses
    path('expenses/', views.ExpenseListCreateAPIView.as_view(), name='api_expenses'),
    path('expenses/<int:pk>/', views.ExpenseDetailAPIView.as_view(), name='api_expense_detail'),

    # Summary
    path('summary/', views.SummaryAPIView.as_view(), name='api_summary'),
]