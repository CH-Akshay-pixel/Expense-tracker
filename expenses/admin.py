from django.contrib import admin
from .models import Category, Expense

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'user', 'created_at']
    search_fields = ['name']
    list_filter= ['user']

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['title', 'amount', 'type', 'category', 'user', 'date']
    list_filter = ['type', 'category', 'date']
    search_fields = ['title', 'note']
    ordering = ['-date']
    date_hierarchy = 'date'
    list_per_page = 20