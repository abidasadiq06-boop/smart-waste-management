from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import MonthlyWasteSchedule
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from .forms import CitizenRegistrationForm, WasteRequestForm, ScrapCategoryForm
from .models import (
    UserProfile,
    WasteRequest,
    CollectionPayment,
    ScrapCategory,
    MonthlyWasteSchedule,
)


# =========================
# LOGIN
# =========================

def user_login(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            if user.is_superuser:
                return redirect('admin_dashboard')

            profile = UserProfile.objects.filter(
                user=user
            ).first()

            if profile and profile.role == 'hks_team':
                return redirect('worker_dashboard')

            elif profile and profile.role == 'citizen':
                return redirect('citizen_dashboard')

        else:
            messages.error(
                request,
                'Invalid username or password'
            )

    return render(
        request,
        'waste_app/login.html'
    )


# =========================
# HOME
# =========================

def home(request):
    return render(
        request,
        'waste_app/home.html'
    )


# =========================
# CITIZEN REGISTRATION
# =========================

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

    return render(
        request,
        'waste_app/register.html',
        {'form': form}
    )


# =========================
# WASTE REQUEST
# =========================

@login_required
def create_request(request):

    if request.method == 'POST':

        form = WasteRequestForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            waste_req = form.save(commit=False)

            waste_req.citizen = request.user

            waste_req.save()

            return redirect('request_list')

    else:

        form = WasteRequestForm()

    return render(
        request,
        'waste_app/request_form.html',
        {'form': form}
    )


@login_required
def request_list(request):

    requests = WasteRequest.objects.filter(
        citizen=request.user
    ).order_by('-created_at')

    return render(
        request,
        'waste_app/request_list.html',
        {'requests': requests}
    )


# =========================
# WORKER DASHBOARD
# =========================

@login_required
def worker_dashboard(request):

    all_requests = WasteRequest.objects.all().order_by(
        '-created_at'
    )

    return render(
        request,
        'waste_app/worker_dashboard.html',
        {'requests': all_requests}
    )


@login_required
def update_status(request, request_id, new_status):

    req = get_object_or_404(
        WasteRequest,
        id=request_id
    )

    req.status = new_status

    req.save()

    return redirect('worker_dashboard')


# =========================
# DASHBOARD REDIRECT
# =========================

@login_required
def dashboard_redirect(request):

    if request.user.is_superuser:
        return redirect('admin_dashboard')

    profile = UserProfile.objects.filter(
        user=request.user
    ).first()

    if profile and profile.role == 'hks_team':
        return redirect('worker_dashboard')

    return redirect('request_list')


# =========================
# CITIZEN DASHBOARD
# =========================

@login_required
def citizen_dashboard(request):

    user = request.user

    user_requests = WasteRequest.objects.filter(
        citizen=user
    )

    total_requests = user_requests.count()

    pending_count = user_requests.filter(
        status='pending'
    ).count()

    in_progress_count = user_requests.filter(
        status__in=['accepted', 'scheduled']
    ).count()

    completed_count = user_requests.filter(
        status='completed'
    ).count()

    recent_requests = user_requests.order_by(
        '-id'
    )[:5]

    context = {
        'total_requests': total_requests,
        'pending_count': pending_count,
        'in_progress_count': in_progress_count,
        'completed_count': completed_count,
        'unread_notifications_count': 0,
        'recent_requests': recent_requests,
    }

    return render(
        request,
        'waste_app/citizen_dashboard.html',
        context
    )


# ==========================================
# ADMIN DASHBOARD
# ==========================================

@login_required
def admin_dashboard(request):
    # Summary statistics for admin overview cards
    total_citizens = UserProfile.objects.filter(role='citizen').count()
    total_workers = UserProfile.objects.filter(role='hks_team').count()
    total_requests = WasteRequest.objects.count()
    pending_requests = WasteRequest.objects.filter(status='pending').count()
    completed_requests = WasteRequest.objects.filter(status='completed').count()
    total_payments = CollectionPayment.objects.count()

    # Fetch scrap requests and all scrap categories
    scrap_requests = WasteRequest.objects.filter(
        request_type='custom'
    ).select_related('citizen', 'scrap_category')

    scrap_items = ScrapCategory.objects.all()

    # Pass all variables to the template context
    context = {
        'total_citizens': total_citizens,
        'total_workers': total_workers,
        'total_requests': total_requests,
        'pending_requests': pending_requests,
        'completed_requests': completed_requests,
        'total_payments': total_payments,
        'scrap_requests': scrap_requests,
        'scrap_items': scrap_items,
    }

    return render(request, 'waste_app/admin_dashboard.html', context)

# =========================
# MANAGE HKS MEMBERS
# =========================

@login_required
def manage_hks_members(request):

    members = UserProfile.objects.filter(
        role='hks_team'
    ).select_related('user')

    return render(
        request,
        'waste_app/manage_hks_members.html',
        {'members': members}
    )


# =========================
# ADD HKS MEMBER
# =========================

@login_required
def add_hks_member(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')
        phone = request.POST.get('phone')
        ward_no = request.POST.get('ward_no')
        address = request.POST.get('address')

        if User.objects.filter(
            username=username
        ).exists():

            messages.error(
                request,
                'Username already exists.'
            )

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

        return redirect(
            'manage_hks_members'
        )

    return render(
        request,
        'waste_app/add_hks_member.html'
    )


# =========================
# DELETE HKS MEMBER
# =========================

@login_required
def delete_hks_member(request, member_id):

    member = get_object_or_404(
        UserProfile,
        id=member_id,
        role='hks_team'
    )

    member.user.delete()

    messages.success(
        request,
        'HKS Member deleted successfully!'
    )

    return redirect(
        'manage_hks_members'
    )


# =========================
# SCRAP MANAGEMENT
# =========================

@login_required
def scrap_management(request):

    scrap_items = ScrapCategory.objects.all()

    schedules = MonthlyWasteSchedule.objects.all().order_by(
        'month'
    )

    context = {
        'scrap_items': scrap_items,
        'schedules': schedules,
    }

    return render(
        request,
        'waste_app/scrap_management.html',
        context
    )


# =========================
# ADD SCRAP ITEM
# =========================

@login_required
def add_scrap_item(request):

    if request.method == 'POST':

        name = request.POST.get('name')
        rate = request.POST.get('rate_per_kg')

        if name and rate:

            ScrapCategory.objects.create(
                name=item.name,
                rate_per_kg=rate
            )

            messages.success(
                request,
                'Scrap item added successfully!'
            )

        return redirect(
            'admin_dashboard'
        )

    return redirect(
        'admin_dashboard'
    )


# =========================
# EDIT SCRAP ITEM
# =========================

@login_required
def edit_scrap_item(request, item_id):

    item = get_object_or_404(
        ScrapCategory,
        id=item_id
    )

    if request.method == 'POST':

        item.name = request.POST.get(
            'name'
        )

        item.rate_per_kg = request.POST.get(
            'rate_per_kg'
        )

        item.save()

        messages.success(
            request,
            'Scrap item updated successfully!'
        )

        return redirect(
            'admin_dashboard'
        )

    return render(
        request,
        'waste_app/add_scrap_item.html',
        {'item': item}
    )
@login_required
def delete_scrap_item(request, item_id):
    item = get_object_or_404(ScrapCategory, id=item_id)
    item.delete()
    messages.success(request, 'Scrap item deleted successfully!')
    return redirect('admin_dashboard')

# =========================
# DELETE SCRAP ITEM
# =========================

@login_required
def delete_scrap_item(request, item_id):

    item = get_object_or_404(
        ScrapCategory,
        id=item_id
    )

    item.delete()

    messages.success(
        request,
        'Scrap item deleted successfully!'
    )

    return redirect(
        'scrap_management'
    )


# =========================
# ADD / EDIT MONTHLY SCHEDULE
# =========================

MONTH_NAMES = {
    1: 'January', 2: 'February', 3: 'March', 4: 'April',
    5: 'May', 6: 'June', 7: 'July', 8: 'August',
    9: 'September', 10: 'October', 11: 'November', 12: 'December'
}

@login_required
def edit_schedule(request, month):
    month_name = MONTH_NAMES.get(month, f"Month {month}")
    schedule, created = MonthlyWasteSchedule.objects.get_or_create(month=month)
    if request.method == 'POST':
        waste_items = request.POST.get('waste_items', '')
        schedule.waste_items = waste_items
        schedule.save()
        messages.success(request, f'Schedule for {month_name} updated successfully!')
        return redirect('admin_dashboard')
        
    return render(request, 'waste_app/edit_schedule.html', {
        'schedule': schedule,
        'month': month,
        'month_name': month_name
    })

# =========================
# ABOUT
# =========================

def about(request):

    return render(
        request,
        'waste_app/about.html'
    )


# =========================
# SERVICES
# =========================

def services(request):

    return render(
        request,
        'waste_app/services.html'
    )


# =========================
# CONTACT
# =========================

def contact(request):

    return render(
        request,
        'waste_app/contact.html'
    )
    # ==============================
# SCRAP MANAGEMENT
# ==============================

@login_required
def add_scrap_item(request):

    if request.method == 'POST':

        name = request.POST.get('name')
        rate = request.POST.get('rate')

        if name and rate:
            ScrapCategory.objects.create(
                name=name,
                rate_per_kg=rate
            )

            messages.success(
                request,
                'Scrap item added successfully!'
            )

        return redirect('admin_dashboard')

    return render(
        request,
        'waste_app/add_scrap_items.html'
    )


@login_required
def edit_scrap_item(request, item_id):

    item = get_object_or_404(
        ScrapCategory,
        id=item_id
    )

    if request.method == 'POST':

        item.name = request.POST.get('name')
        item.rate_per_kg = request.POST.get('rate')

        item.save()

        messages.success(
            request,
            'Scrap item updated successfully!'
        )

        return redirect('admin_dashboard')

    return render(
        request,
        'waste_app/edit_scrap_item.html',
        {'item': item}
    )


@login_required
def delete_scrap_item(request, item_id):

    item = get_object_or_404(
        ScrapCategory,
        id=item_id
    )

    item.delete()

    messages.success(
        request,
        'Scrap item deleted successfully!'
    )

    return redirect('admin_dashboard')


# ==============================
# MONTHLY WASTE SCHEDULE
# ==============================

@login_required
def edit_schedule(request, month):

    schedule = get_object_or_404(
        MonthlyWasteSchedule,
        month=month
    )

    if request.method == 'POST':

        schedule.waste_items = request.POST.get(
            'waste_items'
        )

        schedule.save()

        messages.success(
            request,
            'Monthly schedule updated successfully!'
        )

        return redirect('admin_dashboard')

    return render(
        request,
        'waste_app/edit_schedule.html',
        {
            'schedule': schedule
        }
    )
@login_required
def add_scrap_item(request):

    if request.method == 'POST':
        form = ScrapCategoryForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Scrap item added successfully!')
            return redirect('admin_dashboard')

    else:
        form = ScrapCategoryForm()

    return render(
        request,
        'waste_app/add_scrap_items.html',
        {'form': form}
    )    