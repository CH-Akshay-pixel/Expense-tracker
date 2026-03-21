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
    path('ai/categorize/', views.ai_categorize_view, name='ai_categorize'),
    path('ai/insights/', views.ai_insights_view, name='ai_insights'),
    path('ai/budget/', views.ai_budget_view, name='ai_budget'),
    path('ai/chat/', views.ai_chat_view, name='ai_chat'),
    path('ai/', views.ai_assistant_view, name='ai_assistant'),
]