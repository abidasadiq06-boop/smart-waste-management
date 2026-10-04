from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import CitizenRegistrationForm, WasteRequestForm
from .models import UserProfile, WasteRequest, CollectionPayment
from django.contrib import messages

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
    if profile and profile.role == 'hks_team':
        return redirect('worker_dashboard')
    else:
    
        return redirect('request_list')


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
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import UserProfile, WasteRequest, CollectionPayment


@login_required
def admin_dashboard(request):

    total_citizens = UserProfile.objects.filter(role='citizen').count()
    total_workers = UserProfile.objects.filter(role='hks_team').count()

    total_requests = WasteRequest.objects.count()
    pending_requests = WasteRequest.objects.filter(status='pending').count()
    completed_requests = WasteRequest.objects.filter(status='completed').count()

    total_payments = CollectionPayment.objects.count()

    context = {
        'total_citizens': total_citizens,
        'total_workers': total_workers,
        'total_requests': total_requests,
        'pending_requests': pending_requests,
        'completed_requests': completed_requests,
        'total_payments': total_payments,
    }

    return render(
        request,
        'waste_app/admin_dashboard.html',
        context
    )    
@login_required
def manage_citizens(request):
    citizens = UserProfile.objects.filter(role='citizen').select_related('user')

    return render(
        request,
        'waste_app/manage_citizens.html',
        {'citizens': citizens}
    )    
def about(request):
        return render(request, 'waste_app/about.html')


def services(request):
        return render(request, 'waste_app/services.html')


def contact(request):
        return render(request, 'waste_app/contact.html')
    
@login_required
def manage_hks_members(request):
    members = UserProfile.objects.filter(role='hks_team').select_related('user')

    return render(
        request,
        'waste_app/manage_hks_members.html',
        {'members': members}
    )
@login_required
def add_hks_member(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')
        phone = request.POST.get('phone')
        ward_no = request.POST.get('ward_no')
        address = request.POST.get('address')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('add_hks_member')

        user = User.objects.create_user(
            username=username,
            password=password
        )

        UserProfile.objects.create(
            user=user,
            role='hks_team',
            phone=phone,
            ward_no=ward_no,
            address=address
        )

        messages.success(
            request,
            'HKS Member added successfully!'
        )

        return redirect('manage_hks_members')

    return render(
        request,
        'waste_app/add_hks_member.html'
    )