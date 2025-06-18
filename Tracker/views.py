from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.db import IntegrityError
from django.http import FileResponse, HttpResponse, JsonResponse
from django.db.models import Sum
from django.utils.timezone import now
from calendar import month_name
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.shortcuts import redirect, get_object_or_404

import io
import datetime
from openpyxl import Workbook
from reportlab.pdfgen import canvas

from .models import Profile, Expense  # Ensure Expense model exists
import io
from django.http import HttpResponse, FileResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from openpyxl import Workbook
from reportlab.pdfgen import canvas
from .models import Expense

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Expense

@login_required
def edit_expense(request, id):
    expense = get_object_or_404(Expense, id=id, user=request.user)
    
    if request.method == 'POST':
        expense.title = request.POST.get('title')
        expense.amount = request.POST.get('amount')
        expense.category = request.POST.get('category')
        expense.date = request.POST.get('date')
        expense.save()
        return redirect('my_submissions')
    
    return render(request, 'edit_expense.html', {'expense': expense})

@login_required
def delete_expense(request, id):
    expense = get_object_or_404(Expense, id=id, user=request.user)
    expense.delete()
    return redirect('my_submissions')

@login_required
def my_submissions_view(request):
    user_expenses = Expense.objects.filter(user=request.user).order_by('-date')
    return render(request, 'my_submissions.html', {'expenses': user_expenses})

# API endpoints for chart data
@login_required
@require_http_methods(["GET"])
def chart_data_api(request):
    """API endpoint to get chart data for the current user"""
    today = now().date()
    
    # Monthly data for current year
    monthly_totals = [0] * 12
    expenses = Expense.objects.filter(user=request.user, date__year=today.year)
    for exp in expenses:
        monthly_totals[exp.date.month - 1] += float(exp.amount)

    month_labels = [month_name[i][:3] for i in range(1, 13)]  # Jan, Feb, ...

    # Category-wise data
    category_data = (
        expenses.values('category')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )
    category_labels = [entry['category'] for entry in category_data]
    category_totals = [float(entry['total']) for entry in category_data]

    # Add some debugging
    print(f"Chart data for user {request.user.username}:")
    print(f"Monthly totals: {monthly_totals}")
    print(f"Category labels: {category_labels}")
    print(f"Category totals: {category_totals}")

    return JsonResponse({
        'month_labels': month_labels,
        'monthly_totals': monthly_totals,
        'category_labels': category_labels,
        'category_totals': category_totals,
    })

@login_required
@require_http_methods(["GET"])
def reports_chart_data_api(request):
    """API endpoint to get chart data for reports page"""
    range_type = request.GET.get('range', 'daily').lower()
    expenses = filter_expenses(request.user, range_type)
    
    category_data = expenses.values('category').annotate(total=Sum('amount')).order_by('-total')
    
    return JsonResponse({
        'category_labels': [entry['category'] for entry in category_data],
        'category_totals': [float(entry['total']) for entry in category_data],
        'range_type': range_type
    })

@csrf_protect
def login_register_view(request):
    login_error = False
    registered = False

    if request.method == "POST":
        # --- Login Form ---
        if 'username' in request.POST and 'password' in request.POST and 'email' not in request.POST:
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                request.session.set_expiry(1800)  # Session expires in 30 minutes
                return redirect('dashboard')
            else:
                login_error = True

        # --- Registration Form ---
        elif 'email' in request.POST:
            username = request.POST['username']
            email = request.POST['email']
            password1 = request.POST['password1']
            password2 = request.POST['password2']
            role = request.POST.get('role')

            if password1 == password2 and not User.objects.filter(username=username).exists():
                try:
                    user = User.objects.create_user(username=username, email=email, password=password1)
                    if not Profile.objects.filter(user=user).exists():
                        Profile.objects.create(user=user, role=role)
                    registered = True
                except IntegrityError:
                    login_error = True

    return render(request, "login_register.html", {
        "login_error": login_error,
        "registered": registered
    })


@login_required
def dashboard_view(request):
    return render(request, 'dashboard.html')


@login_required
def add_expense_view(request):
    if request.method == 'POST':
        title = request.POST['title'] 
        amount = request.POST['amount']
        category = request.POST['category']
        description = request.POST.get('description', '')
        date = request.POST.get('date')

        Expense.objects.create(
            user=request.user,  # ← This is key
             title=request.POST['title'],
            amount=amount,
            category=category,
            description=description,
            date=date
        )
        messages.success(request, 'Expense added successfully.')
        return redirect('dashboard')
    
    return render(request, 'add_expense.html')

def filter_expenses(user, range_type):
    today = now().date()
    if range_type == 'daily':
        start_date = today
    elif range_type == 'weekly':
        start_date = today - datetime.timedelta(days=7)
    elif range_type == 'quarterly':
        start_date = today - datetime.timedelta(days=90)
    elif range_type == 'half_yearly':
        start_date = today - datetime.timedelta(days=180)
    else:  # yearly or default
        start_date = today - datetime.timedelta(days=365)

    return Expense.objects.filter(user=user, date__gte=start_date)


@login_required
def reports_view(request):
    if request.method == 'POST':
        range_type = request.POST.get('range', 'daily').lower()
        format_type = request.POST.get('format', 'html')
        expenses = filter_expenses(request.user, range_type)

        if format_type == 'pdf':
            buffer = io.BytesIO()
            p = canvas.Canvas(buffer)
            p.drawString(100, 800, f"{range_type.capitalize()} Expense Report")
            y = 750
            for expense in expenses:
                p.drawString(100, y, f"{expense.date} - {expense.category} - ₹{expense.amount}")
                y -= 20
            p.showPage()
            p.save()
            buffer.seek(0)
            return FileResponse(buffer, as_attachment=True, filename=f'{range_type}_report.pdf')

        elif format_type == 'excel':
            wb = Workbook()
            ws = wb.active
            ws.append(['Date', 'Category', 'Amount'])
            for expense in expenses:
                ws.append([expense.date.strftime("%Y-%m-%d"), expense.category, expense.amount])
            response = HttpResponse(content_type='application/ms-excel')
            response['Content-Disposition'] = f'attachment; filename="{range_type}_report.xlsx"'
            wb.save(response)
            return response

        # If viewing in browser
        category_data = expenses.values('category').annotate(total=Sum('amount')).order_by('-total')
        return render(request, 'reports.html', {
            'category_data': category_data,
            'range_type': range_type
        })

    return render(request, 'reports.html')


@login_required
def approve_expenses_view(request):
    return render(request, 'approve_expenses.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
@require_http_methods(["GET"])
def test_api(request):
    """Simple test endpoint to verify API functionality"""
    return JsonResponse({
        'status': 'success',
        'message': 'API is working',
        'user': request.user.username,
        'timestamp': now().isoformat()
    })