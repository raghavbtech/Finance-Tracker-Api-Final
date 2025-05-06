from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from .models import Transaction
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import requests



FLASK_API_BASE = "https://raghavcseai.pythonanywhere.com/api"

def signup_view(request):
    context = {}
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # Validate form data
        has_error = False
        
        # Save form values to repopulate the form
        context['username'] = username
        context['email'] = email
        
        # Validation checks
        if not username:
            context['username_error'] = 'Username is required'
            has_error = True
        
        if not email:
            context['email_error'] = 'Email is required'
            has_error = True
        
        if not password:
            context['password_error'] = 'Password is required'
            has_error = True
        
        if password != confirm_password:
            context['confirm_password_error'] = 'Passwords do not match'
            has_error = True
        
        if User.objects.filter(username=username).exists():
            context['username_error'] = 'Username already exists'
            has_error = True
            
        if User.objects.filter(email=email).exists():
            context['email_error'] = 'Email already exists'
            has_error = True
        
        # If no errors, create user
        if not has_error:
            try:
                validate_password(password)
                User.objects.create_user(username=username, email=email, password=password)
                messages.success(request, 'Registered successfully. Please login.')
                return redirect('login')
            except ValidationError as e:
                context['password_error'] = list(e.messages)
                has_error = True
    
    return render(request, 'signup.html', context)


def login_view(request):
    context = {}
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Save email to repopulate the form
        context['email'] = email
        
        if not email:
            context['email_error'] = 'Email is required'
        elif not password:
            context['password_error'] = 'Password is required'
        else:
            try:
                user = User.objects.get(email=email)
                user_auth = authenticate(request, username=user.username, password=password)
                if user_auth is not None:
                    auth_login(request, user_auth)
                    return redirect('profile')
                else:
                    context['password_error'] = 'Invalid password'
            except User.DoesNotExist:
                context['email_error'] = 'User with this email does not exist'
    
    return render(request, 'login.html', context)

@login_required
def profile_view(request):
    transactions = Transaction.objects.filter(user=request.user)
    total_amount = sum(transaction.amount for transaction in transactions)
    transaction_count = transactions.count()
    
    context = {
        'user': request.user,
        'total_amount': total_amount,
        'transaction_count': transaction_count,
        'recent_transactions': transactions.order_by('-id')[:5]
    }
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        
        # Simple validation
        if email and email != request.user.email and User.objects.filter(email=email).exists():
            context['email_error'] = 'Email already exists'
            return render(request, 'profile.html', context)
        
        # Update user profile
        request.user.first_name = first_name
        request.user.last_name = last_name
        if email:
            request.user.email = email
        request.user.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    
    return render(request, 'profile.html', context)

@login_required
def transaction_list(request):
    user_id = request.user.id
    try:
        response = requests.get(f"{FLASK_API_BASE}/transactions", params={"user_id": user_id})
        transactions = response.json() if response.status_code == 200 else []
    except Exception as e:
        print(f"Error calling Flask API: {e}")
        transactions = []

    context = {
        'transactions': transactions,
        'total_amount': sum(t['amount'] for t in transactions)
    }
    return render(request, 'transaction_list.html', context)

@login_required
def transaction_create(request):
    context = {'title': 'Create Transaction'}
    
    if request.method == 'POST':
        payload = {
            "category": request.POST.get('category'),
            "amount": request.POST.get('amount'),
            "description": request.POST.get('description'),
            "user_id": request.user.id
        }

        try:
            response = requests.post(f"{FLASK_API_BASE}/transactions", json=payload)
            if response.status_code == 201:
                messages.success(request, 'Transaction created successfully!')
                return redirect('transaction_list')
            else:
                context['api_error'] = "Failed to create transaction."
        except Exception as e:
            context['api_error'] = f"Server error: {e}"

    return render(request, 'transaction_form.html', context)



@login_required
def transaction_update(request, pk):
    context = {
        'title': 'Update Transaction',
        'transaction': {}
    }

    # Fetch existing transaction from Flask
    try:
        response = requests.get(f"{FLASK_API_BASE}/transactions/{pk}", params={"user_id": request.user.id})


        if response.status_code == 200:
            context['transaction'] = response.json()
        else:
            messages.error(request, "Failed to fetch transaction from Flask API.")
            return redirect('transaction_list')
    except Exception as e:
        messages.error(request, f"Error contacting Flask API: {e}")
        return redirect('transaction_list')

    # Handle form submission
    if request.method == 'POST':
        payload = {
            "category": request.POST.get("category"),
            "amount": request.POST.get("amount"),
            "description": request.POST.get("description")
        }

        try:
            response = requests.put(f"{FLASK_API_BASE}/transactions/{pk}", json=payload)
            if response.status_code == 200:
                messages.success(request, "Transaction updated successfully.")
                return redirect('transaction_list')
            else:
                messages.error(request, "Failed to update transaction.")
        except Exception as e:
            messages.error(request, f"Error updating transaction: {e}")

        context['transaction'] = payload  # Keep form data filled on error

    return render(request, 'transaction_form.html', context)

@login_required
def transaction_delete(request, pk):
    if request.method == 'POST':
        try:
            response = requests.get(f"{FLASK_API_BASE}/transactions/{pk}", params={"user_id": request.user.id})

            if response.status_code == 200:
                messages.success(request, "Transaction deleted successfully.")
            else:
                messages.error(request, "Failed to delete transaction.")
        except Exception as e:
            messages.error(request, f"Error contacting Flask API: {e}")
        return redirect('transaction_list')

    # If accessed via GET: Fetch transaction details from Flask
    try:
        response = requests.delete(f"{FLASK_API_BASE}/transactions/{pk}", params={"user_id": request.user.id})

        if response.status_code == 200:
            transaction = response.json()
        else:
            transaction = {'id': pk, 'category': '-', 'amount': '-', 'description': '-'}
            messages.warning(request, "Unable to load full transaction details.")
    except Exception as e:
        transaction = {'id': pk, 'category': '-', 'amount': '-', 'description': '-'}
        messages.warning(request, f"Error loading transaction details: {e}")

    return render(request, 'transaction_confirm_delete.html', {'transaction': transaction})


@login_required
def profile_update_view(request):
    context = {'user': request.user}
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        
        # Simple validation
        has_error = False
        
        if email and email != request.user.email and User.objects.filter(email=email).exists():
            context['email_error'] = 'Email already exists'
            has_error = True
        
        # If no errors, update profile
        if not has_error:
            request.user.first_name = first_name
            request.user.last_name = last_name
            if email:
                request.user.email = email
            request.user.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    
    return render(request, 'profile_update.html', context)


def contact_view(request):
    return render(request, "contactus.html")


def homepage_view(request):
    return render(request, 'homepage.html')


def about_view(request):
    return render(request, "aboutus.html")


def tax_view(request):
    return render(request, "tax.html")