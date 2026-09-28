from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import CitizenRegistrationForm, WasteRequestForm
from .models import UserProfile, WasteRequest

def home(request):
    return render(request, 'waste_app/home.html')

def register_citizen(request):
    if request.method == 'POST':
        form = CitizenRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(
                user=user,
                role='citizen',
                phone=form.cleaned_data.get('phone_number'),
                ward_no=form.cleaned_data.get('ward_number'),
                address=form.cleaned_data.get('address')
            )
            login(request, user)
            return redirect('request_list')
    else:
        form = CitizenRegistrationForm()
    return render(request, 'waste_app/register.html', {'form': form})

@login_required
def create_request(request):
    if request.method == 'POST':
        form = WasteRequestForm(request.POST, request.FILES)
        if form.is_valid():
            waste_req = form.save(commit=False)
            waste_req.citizen = request.user
            waste_req.save()
            return redirect('request_list')
    else:
        form = WasteRequestForm()
    return render(request, 'waste_app/request_form.html', {'form': form})

@login_required
def request_list(request):
    requests = WasteRequest.objects.filter(citizen=request.user).order_by('-created_at')
    return render(request, 'waste_app/request_list.html', {'requests': requests})

@login_required
def worker_dashboard(request):
    all_requests = WasteRequest.objects.all().order_by('-created_at')
    return render(request, 'waste_app/worker_dashboard.html', {'requests': all_requests})

@login_required
def update_status(request, request_id, new_status):
    req = WasteRequest.objects.get(id=request_id)
    req.status = new_status
    req.save()
    return redirect('worker_dashboard')
    
@login_required
def dashboard_redirect(request):
    if request.user.is_superuser:
        return redirect('/admin/')
    
    profile = UserProfile.objects.filter(user=request.user).first()
    if profile and profile.role == 'worker':
        return redirect('worker_dashboard')
    else:
        return redirect('request_list')
from django.shortcuts import render
from .models import WasteRequest 

@login_required
def citizen_dashboard(request):
    user = request.user
    
    # Filter requests by the citizen field matching logged in user
    user_requests = WasteRequest.objects.filter(citizen=user)
    
    # Aggregate statistics for dashboard summary cards
    total_requests = user_requests.count()
    pending_count = user_requests.filter(status='pending').count()
    in_progress_count = user_requests.filter(status__in=['accepted', 'scheduled']).count()
    completed_count = user_requests.filter(status='completed').count()
    
    # Order by latest ID to get recent requests
    recent_requests = user_requests.order_by('-id')[:5]

    context = {
        'total_requests': total_requests,
        'pending_count': pending_count,
        'in_progress_count': in_progress_count,
        'completed_count': completed_count,
        'unread_notifications_count': 0,
        'recent_requests': recent_requests,
    }
    return render(request, 'waste_app/citizen_dashboard.html', context)
def about(request):
        return render(request, 'waste_app/about.html')


def services(request):
        return render(request, 'waste_app/services.html')


def contact(request):
        return render(request, 'waste_app/contact.html')
    
    