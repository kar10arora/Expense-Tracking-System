from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.db import IntegrityError
from django.http import JsonResponse, FileResponse, HttpResponse
from django.db.models import Sum
from django.contrib import messages
from calendar import monthrange
from django.db.models.functions import TruncMonth
from .models import Expense
from django.utils.timezone import now
from calendar import month_name
import datetime
import os
import io
import re
import openpyxl
from openpyxl import Workbook
from reportlab.pdfgen import canvas
from .models import Expense
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import tempfile
import re
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import logging
from transformers import pipeline
import subprocess

User = get_user_model()
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\user\tesseract.exe"

# Set FFmpeg path GLOBALLY at module load time
FFMPEG_PATH = r"C:\Users\user\ffmpeg\ffmpeg\bin"
if FFMPEG_PATH not in os.environ["PATH"]:
    os.environ["PATH"] = FFMPEG_PATH + os.pathsep + os.environ["PATH"]

# ============================================
# OPTIMIZED SPEECH-TO-TEXT (Singleton Pattern)
# ============================================
asr_pipeline = None

def get_asr_pipeline():
    """
    Initialize ASR pipeline once and reuse it.
    Using whisper-tiny.en for faster processing.
    """
    global asr_pipeline
    if asr_pipeline is None:
        print("--- Initializing ASR Pipeline (first time) ---")
        asr_pipeline = pipeline(
            "automatic-speech-recognition",
            model="openai/whisper-tiny.en",
            device=-1,  # CPU
        )
        print("--- ASR Pipeline Ready ---")
    return asr_pipeline


def convert_webm_to_wav(input_path, output_path):
    """
    Convert webm audio to wav format using FFmpeg.
    This is crucial because Whisper works best with WAV files.
    """
    try:
        cmd = [
            "ffmpeg",
            "-y",  # Overwrite output file
            "-i", input_path,
            "-ar", "16000",  # Sample rate 16kHz (optimal for Whisper)
            "-ac", "1",  # Mono channel
            "-c:a", "pcm_s16le",  # 16-bit PCM
            output_path
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode != 0:
            print(f"FFmpeg stderr: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"FFmpeg conversion error: {e}")
        return False


@csrf_exempt
def speech_to_text(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    audio_file = request.FILES.get("audio")
    if not audio_file:
        return JsonResponse({"error": "No audio received"}, status=400)

    temp_webm_path = None
    temp_wav_path = None
    
    try:
        # 1. Save the uploaded webm file
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as temp_webm:
            for chunk in audio_file.chunks():
                temp_webm.write(chunk)
            temp_webm_path = temp_webm.name
        
        print(f"--- Saved webm to: {temp_webm_path} ---")
        print(f"--- File size: {os.path.getsize(temp_webm_path)} bytes ---")
        
        # Check if file is too small (likely empty recording)
        if os.path.getsize(temp_webm_path) < 1000:
            return JsonResponse({
                "text": "",
                "status": "empty",
                "message": "Recording too short or empty"
            })
        
        # 2. Convert webm to wav using FFmpeg
        temp_wav_path = temp_webm_path.replace(".webm", ".wav")
        
        print(f"--- Converting to WAV: {temp_wav_path} ---")
        
        if not convert_webm_to_wav(temp_webm_path, temp_wav_path):
            return JsonResponse({
                "error": "Audio conversion failed",
                "detail": "FFmpeg could not convert the audio file"
            }, status=500)
        
        print(f"--- WAV file size: {os.path.getsize(temp_wav_path)} bytes ---")
        
        # 3. Run ASR inference on the WAV file
        asr = get_asr_pipeline()
        
        print("--- Running ASR inference ---")
        result = asr(temp_wav_path)
        print(f"--- Raw ASR result: {result} ---")
        
        # Extract text from result
        if isinstance(result, dict):
            text = result.get("text", "").strip()
        elif isinstance(result, list) and len(result) > 0:
            text = result[0].get("text", "").strip()
        else:
            text = str(result).strip()
        
        print(f"--- Extracted text: '{text}' ---")

        if not text:
            return JsonResponse({
                "text": "",
                "status": "empty",
                "message": "No speech detected in audio"
            })

        return JsonResponse({
            "text": text,
            "status": "success"
        })

    except Exception as e:
        import traceback
        print(f"--- Speech Error: {str(e)} ---")
        print(traceback.format_exc())
        return JsonResponse({
            "error": "Processing failed", 
            "detail": str(e)
        }, status=500)
    
    finally:
        # 4. Cleanup temporary files
        for path in [temp_webm_path, temp_wav_path]:
            if path and os.path.exists(path):
                try:
                    os.unlink(path)
                    print(f"--- Deleted temp file: {path} ---")
                except Exception as e:
                    print(f"Could not delete temp file {path}: {e}")


# ============================================
# AUTO MAP INVOICE DATA
# ============================================
@csrf_exempt
@login_required
@require_http_methods(["POST"])
def auto_map_invoice_data(request):
    import datetime

    invoice_file = request.FILES.get('invoice')
    if not invoice_file:
        return JsonResponse({'error': 'No invoice file uploaded.'}, status=400)

    # Save file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        for chunk in invoice_file.chunks():
            temp_pdf.write(chunk)
        temp_pdf_path = temp_pdf.name

    # Convert PDF to Image (if PDF), else load Image directly
    if invoice_file.name.endswith('.pdf'):
        images = convert_from_path(temp_pdf_path, dpi=300, poppler_path=r'C:\Users\user\Downloads\Release-24.08.0-0\poppler-24.08.0\Library\bin')
    else:
        images = [Image.open(temp_pdf_path)]

    # Extract text from first page
    extracted_text = pytesseract.image_to_string(images[0])

    print("\n--- OCR Extracted Text ---\n", extracted_text, "\n---------------------------\n")

    # Extract Invoice Date
    date_match = re.search(r'Date Of Issue[:\s]*([\d]{4}-[\d]{2}-[\d]{2})', extracted_text)
    invoice_date = ''
    if date_match:
        invoice_date = date_match.group(1).strip()

    # Extract All Items (Title + Description)
    item_pattern = r'\d+\s+(.*?)\s*-\s*(.*?)(?:\n|$)'
    item_matches = re.findall(item_pattern, extracted_text)

    # Extract All Amounts (Line items, not Total)
    amount_pattern = r'=\s*([\d,]+(?:\.\d{1,2})?)'
    amount_matches = re.findall(amount_pattern, extracted_text)

    # Clean amount values (remove commas)
    amounts_clean = [amt.replace(',', '').strip() for amt in amount_matches]

    print("\n--- Matched Items ---\n", item_matches)
    print("\n--- Matched Amounts ---\n", amounts_clean)

    # Pair items with amounts (assume sequential matching)
    items = []
    for idx, item in enumerate(item_matches):
        title = item[0].strip()
        description = item[1].strip()
        amount = amounts_clean[idx] if idx < len(amounts_clean) else ''

        items.append({
            'title': title,
            'description': description,
            'amount': amount,
            'date': invoice_date
        })

    if not items:
        return JsonResponse({'error': 'No items found in invoice.'}, status=404)

    return JsonResponse({'items': items})


# ============================================
# EXPENSE VIEWS
# ============================================
def submit_expense(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        amount = request.POST.get('amount')
        date = request.POST.get('date')
        category = request.POST.get('category')
        description = request.POST.get('description')

        # Save the expense
        Expense.objects.create(
            user=request.user,
            title=title,
            amount=amount,
            date=date,
            category=category,
            description=description
        )
        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


@login_required
def add_expense_view(request):
    if request.method == 'POST':
        title = request.POST['title']
        amount = request.POST['amount']
        category = request.POST['category']
        description = request.POST.get('description', '')
        date = request.POST.get('date')
        invoice = request.FILES.get('invoice')

        Expense.objects.create(
            user=request.user,
            title=title,
            amount=amount,
            category=category,
            description=description,
            date=date,
            invoice=invoice
        )

        return redirect('/add-expense?submitted=true')

    submitted = request.GET.get('submitted') == 'true'
    return render(request, 'add_expense.html', {'submitted': submitted})


@login_required
def edit_expense(request, id):
    expense = get_object_or_404(Expense, id=id, user=request.user)

    if request.method == 'POST':
        expense.title = request.POST.get('title')
        expense.amount = request.POST.get('amount')
        expense.category = request.POST.get('category')
        expense.date = request.POST.get('date')

        if 'delete_invoice' in request.POST and expense.invoice:
            if os.path.isfile(expense.invoice.path):
                os.remove(expense.invoice.path)
            expense.invoice = None

        if request.FILES.get('invoice'):
            expense.invoice = request.FILES['invoice']

        expense.save()
        messages.success(request, "Expense updated successfully.")
        return redirect('my_submissions')

    return render(request, 'edit_expense.html', {'expense': expense})


@login_required
def delete_expense(request, id):
    expense = get_object_or_404(Expense, id=id, user=request.user)
    if expense.invoice and os.path.isfile(expense.invoice.path):
        os.remove(expense.invoice.path)
    expense.delete()
    messages.success(request, "Expense deleted.")
    return redirect('my_submissions')


@login_required
def my_submissions_view(request):
    user_expenses = Expense.objects.filter(user=request.user).order_by('-date')
    return render(request, 'my_submissions.html', {'expenses': user_expenses})


# ============================================
# AUTHENTICATION
# ============================================
@csrf_protect
def login_register_view(request):
    login_error = False
    register_failed = False
    form_data = {}
    show_register = False
    if request.method == "POST":
        # --- Login Form ---
        if 'email' in request.POST and 'password' in request.POST and 'first_name' not in request.POST:
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(request, email=email, password=password)
            if user:
                login(request, user)
                request.session.set_expiry(1800)
                return redirect('dashboard')
            else:
                login_error = True
                messages.error(request, "Invalid email or password.")

        # --- Registration Form ---
        elif 'first_name' in request.POST:
            show_register = True
            form_data = {
                'first_name': request.POST.get('first_name', ''),
                'last_name': request.POST.get('last_name', ''),
                'email': request.POST.get('email', ''),
                'role': request.POST.get('role', ''),
            }

            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')

            # Password Validation
            if password1 != password2:
                messages.error(request, "Passwords do not match.")
                register_failed = True
            elif len(password1) < 8:
                messages.error(request, "Password must be at least 8 characters long.")
                register_failed = True
            elif not any(char.isdigit() for char in password1):
                messages.error(request, "Password must contain at least one digit.")
                register_failed = True
            elif not any(char.isalpha() for char in password1):
                messages.error(request, "Password must contain at least one letter.")
                register_failed = True
            elif not re.search(r'[!@#$%^&*(),.?":{}|<>]', password1):
                messages.error(request, "Password must contain at least one special character.")
                register_failed = True
            elif User.objects.filter(email=form_data['email']).exists():
                messages.error(request, "Email already exists.")
                register_failed = True
            else:
                try:
                    user = User.objects.create_user(
                        email=form_data['email'],
                        password=password1,
                        first_name=form_data['first_name'],
                        last_name=form_data['last_name'],
                        role=form_data['role']
                    )
                    messages.success(request, "Registration successful! Please log in.")
                    return redirect('login')
                except IntegrityError:
                    messages.error(request, "An error occurred during registration.")
                    register_failed = True
    else:
        if request.path == '/register/':
            show_register = True

    return render(request, "login_register.html", {
        "login_error": login_error,
        "register_failed": register_failed,
        "form_data": form_data,
        "show_register": show_register
    })


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


# ============================================
# DASHBOARD & CHARTS
# ============================================
@login_required
def dashboard_view(request):
    return render(request, 'dashboard.html')


def invoice_generator_view(request):
    return render(request, 'dashboard_invoice.html')


@login_required
@require_http_methods(["GET"])
def chart_data_api(request):
    user   = request.user
    today  = now().date()
    period = request.GET.get("period", "daily").lower()

    if period == "daily":
        days_in_month = monthrange(today.year, today.month)[1]
        daily_totals  = {day: 0 for day in range(1, days_in_month + 1)}

        expenses = (
            Expense.objects
            .filter(user=user, date__year=today.year, date__month=today.month)
        )

        for e in expenses:
            daily_totals[e.date.day] += float(e.amount)

        labels = [str(d) for d in range(1, days_in_month + 1)]
        totals = [daily_totals[d] for d in range(1, days_in_month + 1)]
        title  = f"Daily Expenses — {month_name[today.month]} {today.year}"

    else:  # monthly
        expenses = Expense.objects.filter(user=user, date__year=today.year)

        monthly_totals = (
            expenses
            .annotate(month=TruncMonth("date"))
            .values("month")
            .annotate(total=Sum("amount"))
            .order_by("month")
        )

        labels = [m["month"].strftime("%b") for m in monthly_totals]
        totals = [float(m["total"])          for m in monthly_totals]
        title  = f"Monthly Expenses — {today.year}"

    category_qs = (
        expenses
        .values("category")
        .annotate(total=Sum("amount"))
        .order_by("-total")
    )
    cat_labels  = [c["category"]        for c in category_qs]
    cat_totals  = [float(c["total"])    for c in category_qs]

    return JsonResponse({
        "labels"          : labels,
        "totals"          : totals,
        "title"           : title,
        "category_labels" : cat_labels,
        "category_totals" : cat_totals,
    })


@login_required
@require_http_methods(["GET"])
def reports_chart_data_api(request):
    range_type = request.GET.get('range', 'daily').lower()
    expenses = filter_expenses(request.user, range_type)

    category_data = expenses.values('category').annotate(total=Sum('amount')).order_by('-total')

    return JsonResponse({
        'category_labels': [entry['category'] for entry in category_data],
        'category_totals': [float(entry['total']) for entry in category_data],
        'range_type': range_type
    })


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
    else:
        start_date = today - datetime.timedelta(days=365)

    return Expense.objects.filter(user=user, date__gte=start_date)


# ============================================
# REPORTS
# ============================================
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
@require_http_methods(["GET"])
def test_api(request):
    return JsonResponse({
        'status': 'success',
        'message': 'API is working',
        'user': request.user.email,
        'timestamp': now().isoformat()
    })