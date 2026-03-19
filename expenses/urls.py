from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('expense/add/', views.add_expense_view, name='add_expense'),
    path('expenses/', views.expense_list_view, name='expense_list'),
]