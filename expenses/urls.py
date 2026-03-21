from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('expense/add/', views.add_expense_view, name='add_expense'),
    path('expenses/', views.expense_list_view, name='expense_list'),
    path('expense/edit/<int:pk>/', views.edit_expense_view, name='edit_expense'),
    path('expense/delete/<int:pk>/', views.delete_expense_view, name='delete_expense'),
    path('summary/', views.summary_view, name='summary'),
    path('analytics/', views.analytics_view, name='analytics'),
]