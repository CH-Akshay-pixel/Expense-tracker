from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from datetime import datetime
from .models import Expense, Category
from .forms import ExpenseForm
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json


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

    # --- Search ---
    search = request.GET.get('search', '')
    if search:
        expenses = expenses.filter(title__icontains=search)

    # --- Filter by Type ---
    filter_type = request.GET.get('type', '')
    if filter_type in ['income', 'expense']:
        expenses = expenses.filter(type=filter_type)

    # --- Filter by Category ---
    filter_category = request.GET.get('category', '')
    if filter_category:
        expenses = expenses.filter(category__id=filter_category)

    # --- Filter by Date Range ---
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    if date_from:
        expenses = expenses.filter(date__gte=date_from)
    if date_to:
        expenses = expenses.filter(date__lte=date_to)

    # --- Totals (after filtering) ---
    total_expenses = expenses.filter(
        type='expense'
    ).aggregate(total=Sum('amount'))['total'] or 0

    total_income = expenses.filter(
        type='income'
    ).aggregate(total=Sum('amount'))['total'] or 0

    # --- Pagination ---
    from django.core.paginator import Paginator
    paginator = Paginator(expenses, 10)  # 10 per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # --- User Categories for filter dropdown ---
    categories = Category.objects.filter(user=request.user)

    try:
        currency = request.user.userprofile.currency
    except:
        currency = 'USD'

    context = {
        'page_obj': page_obj,
        'expenses': page_obj,
        'currency': currency,
        'total_expenses': total_expenses,
        'total_income': total_income,
        'categories': categories,
        'search': search,
        'filter_type': filter_type,
        'filter_category': filter_category,
        'date_from': date_from,
        'date_to': date_to,
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

@login_required
def summary_view(request):
    from django.db.models import Sum, Count
    from datetime import datetime
    import json

    today = datetime.today()
    month = today.month
    year = today.year

    # Get selected month/year from URL params
    selected_month = int(request.GET.get('month', month))
    selected_year = int(request.GET.get('year', year))

    # All expenses for selected month
    monthly_data = Expense.objects.filter(
        user=request.user,
        date__month=selected_month,
        date__year=selected_year
    )

    # Total income & expenses
    total_income = monthly_data.filter(
        type='income'
    ).aggregate(total=Sum('amount'))['total'] or 0

    total_expenses = monthly_data.filter(
        type='expense'
    ).aggregate(total=Sum('amount'))['total'] or 0

    balance = total_income - total_expenses

    # Expenses by category
    category_data = monthly_data.filter(
        type='expense'
    ).values(
        'category__name',
        'category__icon'
    ).annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')

    # Last 6 months data for trend
    months_data = []
    for i in range(5, -1, -1):
        from datetime import date
        from dateutil.relativedelta import relativedelta
        d = date.today() - relativedelta(months=i)
        m_expenses = Expense.objects.filter(
            user=request.user,
            type='expense',
            date__month=d.month,
            date__year=d.year
        ).aggregate(total=Sum('amount'))['total'] or 0

        m_income = Expense.objects.filter(
            user=request.user,
            type='income',
            date__month=d.month,
            date__year=d.year
        ).aggregate(total=Sum('amount'))['total'] or 0

        months_data.append({
            'month': d.strftime('%b'),
            'expenses': float(m_expenses),
            'income': float(m_income),
        })

    try:
        currency = request.user.userprofile.currency
    except:
        currency = 'USD'

    # Month choices for dropdown
    month_names = [
        'January', 'February', 'March', 'April',
        'May', 'June', 'July', 'August',
        'September', 'October', 'November', 'December'
    ]

    context = {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'balance': balance,
        'category_data': category_data,
        'currency': currency,
        'months_data': json.dumps(months_data),
        'selected_month': selected_month,
        'selected_year': selected_year,
        'month_names': enumerate(month_names, 1),
        'current_year': year,
    }

    return render(request, 'expenses/summary.html', context)

@login_required
def analytics_view(request):
    from django.db.models import Sum, Count
    from datetime import datetime, date
    from dateutil.relativedelta import relativedelta
    import json

    today = date.today()

    # --- Pie Chart Data (expenses by category) ---
    category_expenses = Expense.objects.filter(
        user=request.user,
        type='expense',
        date__month=today.month,
        date__year=today.year
    ).values(
        'category__name',
        'category__icon'
    ).annotate(
        total=Sum('amount')
    ).order_by('-total')

    pie_labels = []
    pie_data = []
    pie_colors = [
        '#4f46e5', '#7c3aed', '#db2777',
        '#dc2626', '#d97706', '#16a34a',
        '#0891b2', '#6366f1', '#ec4899'
    ]

    for cat in category_expenses:
        pie_labels.append(
            cat['category__name'] or 'Uncategorized'
        )
        pie_data.append(float(cat['total']))

    # --- Line Chart Data (daily spending this month) ---
    import calendar
    days_in_month = calendar.monthrange(
        today.year, today.month
    )[1]

    daily_labels = []
    daily_expenses = []
    daily_income = []

    for day in range(1, days_in_month + 1):
        daily_labels.append(str(day))

        day_expense = Expense.objects.filter(
            user=request.user,
            type='expense',
            date__year=today.year,
            date__month=today.month,
            date__day=day
        ).aggregate(total=Sum('amount'))['total'] or 0

        day_income = Expense.objects.filter(
            user=request.user,
            type='income',
            date__year=today.year,
            date__month=today.month,
            date__day=day
        ).aggregate(total=Sum('amount'))['total'] or 0

        daily_expenses.append(float(day_expense))
        daily_income.append(float(day_income))

    # --- Top 5 Spending Categories (all time) ---
    top_categories = Expense.objects.filter(
        user=request.user,
        type='expense'
    ).values(
        'category__name',
        'category__icon'
    ).annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')[:5]

    # --- Monthly Comparison (last 6 months) ---
    monthly_labels = []
    monthly_expenses_data = []
    monthly_income_data = []

    for i in range(5, -1, -1):
        d = today - relativedelta(months=i)
        monthly_labels.append(d.strftime('%b %Y'))

        m_exp = Expense.objects.filter(
            user=request.user,
            type='expense',
            date__month=d.month,
            date__year=d.year
        ).aggregate(total=Sum('amount'))['total'] or 0

        m_inc = Expense.objects.filter(
            user=request.user,
            type='income',
            date__month=d.month,
            date__year=d.year
        ).aggregate(total=Sum('amount'))['total'] or 0

        monthly_expenses_data.append(float(m_exp))
        monthly_income_data.append(float(m_inc))

    # --- Overall Stats ---
    total_transactions = Expense.objects.filter(
        user=request.user
    ).count()

    total_spent_ever = Expense.objects.filter(
        user=request.user,
        type='expense'
    ).aggregate(total=Sum('amount'))['total'] or 0

    total_earned_ever = Expense.objects.filter(
        user=request.user,
        type='income'
    ).aggregate(total=Sum('amount'))['total'] or 0

    try:
        currency = request.user.userprofile.currency
    except:
        currency = 'USD'

    context = {
        'currency': currency,
        'pie_labels': json.dumps(pie_labels),
        'pie_data': json.dumps(pie_data),
        'pie_colors': json.dumps(pie_colors[:len(pie_data)]),
        'daily_labels': json.dumps(daily_labels),
        'daily_expenses': json.dumps(daily_expenses),
        'daily_income': json.dumps(daily_income),
        'monthly_labels': json.dumps(monthly_labels),
        'monthly_expenses_data': json.dumps(monthly_expenses_data),
        'monthly_income_data': json.dumps(monthly_income_data),
        'top_categories': top_categories,
        'total_transactions': total_transactions,
        'total_spent_ever': total_spent_ever,
        'total_earned_ever': total_earned_ever,
        'month_name': today.strftime('%B %Y'),
    }

    return render(request, 'expenses/analytics.html', context)


@login_required
@require_http_methods(["POST"])
def ai_categorize_view(request):
    """Auto categorize expense by title"""
    try:
        data = json.loads(request.body)
        title = data.get('title', '')

        if not title:
            return JsonResponse({'error': 'Title is required'}, status=400)

        # Get user categories
        categories = Category.objects.filter(user=request.user)
        category_names = [cat.name for cat in categories]

        if not category_names:
            return JsonResponse({'category': 'Other'})

        from .ai_service import categorize_expense
        suggested_category = categorize_expense(title, category_names)

        # Find matching category id
        category_id = None
        for cat in categories:
            if cat.name.lower() == suggested_category.lower():
                category_id = cat.id
                break

        return JsonResponse({
            'category': suggested_category,
            'category_id': category_id
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def ai_insights_view(request):
    """Get AI spending insights"""
    from django.db.models import Sum
    from .ai_service import get_spending_insights

    # Get this month's data
    from datetime import datetime
    today = datetime.today()

    category_data = Expense.objects.filter(
        user=request.user,
        type='expense',
        date__month=today.month,
        date__year=today.year
    ).values('category__name').annotate(
        total=Sum('amount')
    )

    expenses_data = {
        item['category__name'] or 'Uncategorized': float(item['total'])
        for item in category_data
    }

    try:
        budget = request.user.userprofile.monthly_budget
        currency = request.user.userprofile.currency
    except:
        budget = 0
        currency = 'USD'

    if not expenses_data:
        return JsonResponse({
            'insights': 'No expense data found for this month. Start adding expenses to get AI insights!'
        })

    insights = get_spending_insights(expenses_data, currency, budget)
    return JsonResponse({'insights': insights})


@login_required
def ai_budget_view(request):
    """Get AI budget recommendations"""
    from django.db.models import Sum
    from .ai_service import get_budget_recommendation
    from datetime import datetime

    today = datetime.today()

    # Last 3 months average
    category_data = Expense.objects.filter(
        user=request.user,
        type='expense',
    ).values('category__name').annotate(
        total=Sum('amount')
    )

    expenses_data = {
        item['category__name'] or 'Uncategorized': float(item['total'])
        for item in category_data
    }

    # Total income
    total_income = Expense.objects.filter(
        user=request.user,
        type='income',
        date__month=today.month,
        date__year=today.year
    ).aggregate(total=Sum('amount'))['total'] or 0

    try:
        currency = request.user.userprofile.currency
    except:
        currency = 'USD'

    recommendation = get_budget_recommendation(
        expenses_data,
        float(total_income),
        currency
    )

    return JsonResponse({'recommendation': recommendation})


@login_required
@require_http_methods(["POST"])
def ai_chat_view(request):
    """AI chatbot for expense queries"""
    from django.db.models import Sum
    from .ai_service import chat_with_ai

    try:
        data = json.loads(request.body)
        user_message = data.get('message', '')

        if not user_message:
            return JsonResponse({'error': 'Message is required'}, status=400)

        # Build expense context
        from datetime import datetime
        today = datetime.today()

        recent_expenses = Expense.objects.filter(
            user=request.user
        ).order_by('-date')[:10]

        monthly_total = Expense.objects.filter(
            user=request.user,
            type='expense',
            date__month=today.month,
            date__year=today.year
        ).aggregate(total=Sum('amount'))['total'] or 0

        monthly_income = Expense.objects.filter(
            user=request.user,
            type='income',
            date__month=today.month,
            date__year=today.year
        ).aggregate(total=Sum('amount'))['total'] or 0

        try:
            currency = request.user.userprofile.currency
            budget = request.user.userprofile.monthly_budget
        except:
            currency = 'USD'
            budget = 0

        # Build context string
        expenses_context = f"""
Monthly Income: {currency} {monthly_income}
Monthly Expenses: {currency} {monthly_total}
Monthly Budget: {currency} {budget}

Recent transactions:
"""
        for exp in recent_expenses:
            expenses_context += f"- {exp.title}: {currency} {exp.amount} ({exp.type}) on {exp.date}\n"

        response = chat_with_ai(user_message, expenses_context)
        return JsonResponse({'response': response})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@login_required
def ai_assistant_view(request):
    try:
        currency = request.user.userprofile.currency
    except:
        currency = 'USD'
    return render(request, 'expenses/ai_assistant.html', {
        'currency': currency
    })