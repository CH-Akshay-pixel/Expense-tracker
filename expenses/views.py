from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from datetime import datetime
from .models import Expense, Category
from .forms import ExpenseForm


@login_required
def dashboard_view(request):
    today = datetime.today()
    month = today.month
    year = today.year

    expenses = Expense.objects.filter(user=request.user)

    monthly_expenses = expenses.filter(
        type='expense',
        date__month=month,
        date__year=year
    ).aggregate(total=Sum('amount'))['total'] or 0

    monthly_income = expenses.filter(
        type='income',
        date__month=month,
        date__year=year
    ).aggregate(total=Sum('amount'))['total'] or 0

    balance = monthly_income - monthly_expenses

    recent_transactions = expenses.order_by('-date')[:5]

    try:
        budget = request.user.userprofile.monthly_budget
        currency = request.user.userprofile.currency
    except:
        budget = 0
        currency = 'USD'

    budget_percentage = 0
    if budget > 0:
        budget_percentage = min(int((monthly_expenses / budget) * 100), 100)

    context = {
        'monthly_expenses': monthly_expenses,
        'monthly_income': monthly_income,
        'balance': balance,
        'recent_transactions': recent_transactions,
        'budget': budget,
        'budget_percentage': budget_percentage,
        'currency': currency,
        'month_name': today.strftime('%B %Y'),
    }

    return render(request, 'expenses/dashboard.html', context)


@login_required
def add_expense_view(request):
    if request.method == 'POST':
        form = ExpenseForm(request.user, request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            messages.success(request, 'Transaction added successfully!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = ExpenseForm(request.user)

    try:
        currency = request.user.userprofile.currency
    except:
        currency = 'USD'

    return render(request, 'expenses/add_expense.html', {
        'form': form,
        'currency': currency
    })


@login_required
def expense_list_view(request):
    expenses = Expense.objects.filter(
        user=request.user
    ).order_by('-date')

    try:
        currency = request.user.userprofile.currency
    except:
        currency = 'USD'

    # Totals
    total_expenses = expenses.filter(
        type='expense'
    ).aggregate(total=Sum('amount'))['total'] or 0

    total_income = expenses.filter(
        type='income'
    ).aggregate(total=Sum('amount'))['total'] or 0

    context = {
        'expenses': expenses,
        'currency': currency,
        'total_expenses': total_expenses,
        'total_income': total_income,
    }
    return render(request, 'expenses/expense_list.html', context)

@login_required
def edit_expense_view(request, pk):
    expense = get_object_or_404(Expense, id=pk, user=request.user)

    if request.method == 'POST':
        form = ExpenseForm(request.user, request.POST, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, 'Transaction updated successfully!')
            return redirect('expense_list')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = ExpenseForm(request.user, instance=expense)

    try:
        currency = request.user.userprofile.currency
    except:
        currency = 'USD'

    return render(request, 'expenses/edit_expense.html', {
        'form': form,
        'expense': expense,
        'currency': currency
    })


@login_required
def delete_expense_view(request, pk):
    expense = get_object_or_404(Expense, id=pk, user=request.user)

    if request.method == 'POST':
        expense.delete()
        messages.success(request, 'Transaction deleted successfully!')
        return redirect('expense_list')

    return render(request, 'expenses/delete_expense.html', {
        'expense': expense
    })