from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from .forms import CitizenRegistrationForm, WasteRequestForm, ScrapCategoryForm
from django.db.models import Sum
from .models import (
    UserProfile,
    WasteRequest,
    CollectionPayment,
    ScrapCategory,
    MonthlyWasteSchedule,
)
import io
from django.http import FileResponse
from django.contrib.auth.decorators import login_required
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from .models import WasteRequest

@login_required
def download_receipt(request, request_id):
    # Retrieve the specific request for the logged-in citizen
    req = WasteRequest.objects.get(id=request_id, citizen=request.user)

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)

    # Header / Title
    p.setFont("Helvetica-Bold", 18)
    p.setFillColor(colors.HexColor("#065f46")) # Emerald Dark
    p.drawString(50, 750, "HARITHA KARMA SENA - PAYMENT RECEIPT")
    
    p.setFont("Helvetica", 10)
    p.setFillColor(colors.gray)
    p.drawString(50, 735, "Clean Environment, Better Tomorrow | Kerala Local Self Government")
    p.line(50, 725, 550, 725)

    # Receipt Information
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, 690, f"Receipt No: HKS-REC-{req.id}")
    p.setFont("Helvetica", 10)
    p.drawString(50, 670, f"Date: {req.preferred_date if hasattr(req, 'preferred_date') and req.preferred_date else 'N/A'}")
    p.drawString(50, 650, f"Citizen Name: {request.user.username}")
    p.drawString(50, 630, f"Status: {req.status}")

    # Details Box
    p.rect(50, 520, 500, 90, stroke=1, fill=0)
    p.setFont("Helvetica-Bold", 11)
    p.drawString(65, 585, "Service / Collection Description")
    p.drawString(450, 585, "Amount")
    p.line(50, 575, 550, 575)

    p.setFont("Helvetica", 10)
    desc = f"{req.request_type.capitalize()} Waste Collection"
    p.drawString(65, 550, desc)
    
    # Amount calculation (Using 'Rs.' instead of '₹' to avoid standard font encoding errors)
    amount = "Rs. 50.00" if req.request_type.lower() == 'normal' else "Payout as per scrap rate"
    p.drawString(430, 550, amount)

    # Footer note
    p.setFont("Helvetica-Oblique", 9)
    p.setFillColor(colors.gray)
    p.drawString(50, 480, "* This is an automated computer-generated receipt for Haritha Karma Sena waste management service.")

    p.showPage()
    p.save()

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f"Receipt_HKS_{req.id}.pdf")




# ==============================
# LOGOUT
# ==============================
def user_logout(request):
    logout(request)
    return redirect('login')


# ==============================
# LOGIN
# ==============================


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

            return redirect('citizen_dashboard')

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

            return redirect('citizen_dashboard')

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


# ==============================
# CITIZEN DASHBOARD
# ==============================

@login_required
def citizen_dashboard(request):
    # Fetch user profile for logged-in user
    profile = UserProfile.objects.filter(user=request.user).first()

    # Fetch user requests using citizen ForeignKey, ordered by latest
    user_requests = WasteRequest.objects.filter(citizen=request.user).order_by('-id')

    # Latest request for tracking status
    latest_request = user_requests.first()

    # Next scheduled request for pickup card
    next_pickup = user_requests.filter(status__in=['Pending', 'pending', 'Scheduled', 'In Progress']).first()

    # Request counts
    total_requests = user_requests.count()
    pending_count = user_requests.filter(status__iexact='pending').count()

    context = {
        'profile': profile,
        'requests': user_requests[:5],        # Recent 5 requests for table
        'latest_request': latest_request,    # Live tracking data
        'next_pickup': next_pickup,          # Next scheduled pickup card
        'total_requests': total_requests,
        'pending_count': pending_count,
    }

    return render(request, 'waste_app/citizen_dashboard.html', context)

    
@login_required
def admin_dashboard(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        # 1. Update Request Status
        if action == 'update_request_status':
            req_id = request.POST.get('request_id')
            new_status = request.POST.get('status')
            waste_req = get_object_or_404(WasteRequest, id=req_id)
            waste_req.status = new_status
            waste_req.save()
            messages.success(request, f'Request #{req_id} status updated to {new_status.title()}!')

        # 2. Add Citizen Directly
        elif action == 'add_citizen':
            username = request.POST.get('username')
            phone = request.POST.get('phone')
            ward_no = request.POST.get('ward_no')
            address = request.POST.get('address')
        # 3. Delete Citizen
        elif action == 'delete_citizen':
            citizen_id = request.POST.get('citizen_id')
            profile = get_object_or_404(UserProfile, id=citizen_id)
            user_obj = profile.user
            profile.delete()
            user_obj.delete()
            messages.success(request, 'Citizen deleted successfully!')

        # 4. Add HKS Member
        elif action == 'add_hks':
            username = request.POST.get('username')
            password = request.POST.get('password') or '1234'
            phone = request.POST.get('phone')
            ward_no = request.POST.get('ward_no')
            if username:
                user, _ = User.objects.get_or_create(username=username)
                user.set_password(password)
                user.save()
                profile, _ = UserProfile.objects.get_or_create(user=user)
                profile.role = 'worker'
                profile.phone = phone
                profile.ward_no = str(ward_no).strip()
                profile.save()
                messages.success(request, f'HKS Member {username} added!')

        # 5. Edit HKS Member
        elif action == 'edit_hks':
            member_id = request.POST.get('member_id')
            phone = request.POST.get('phone')
            ward_no = request.POST.get('ward_no')
            first_name = request.POST.get('first_name')
            new_password = request.POST.get('password')
            
            profile = get_object_or_404(UserProfile, id=member_id)
            profile.phone = phone
            profile.ward_no = str(ward_no).strip()
            profile.save()
            
            if first_name:
                profile.user.first_name = first_name
            if new_password:
                profile.user.set_password(new_password)
            profile.user.save()
            messages.success(request, 'HKS Member updated successfully!')

        # Delete HKS Member
        elif action == 'delete_hks':
            member_id = request.POST.get('member_id')
            profile = get_object_or_404(UserProfile, id=member_id)
            user_obj = profile.user
            profile.delete()
            user_obj.delete()
            messages.success(request, 'HKS Member deleted successfully!')  
            
            
        return redirect('admin_dashboard')

    # Citizens
    citizens = UserProfile.objects.filter(role='citizen')
    total_citizens = citizens.count()

    # HKS Members with Work Status
    hks_profiles = UserProfile.objects.exclude(role='citizen').exclude(user__is_superuser=True)
    total_workers = hks_profiles.count()

    hks_members = []
    for hks in hks_profiles:
        hks_requests = WasteRequest.objects.filter(citizen__userprofile__ward_no=hks.ward_no) if hks.ward_no else WasteRequest.objects.none()
        pending_cnt = hks_requests.filter(status='pending').count()
        completed_cnt = hks_requests.filter(status='completed').count()
        
        hks_members.append({
            'id': hks.id,
            'user': hks.user,
            'phone': hks.phone,
            'ward_no': hks.ward_no,
            'pending_count': pending_cnt,
            'completed_count': completed_cnt,
            'work_status': 'Completed' if (pending_cnt == 0 and completed_cnt > 0) else ('Pending' if pending_cnt > 0 else 'No Tasks')
        })

    # Requests & Stats
    total_requests = WasteRequest.objects.count()
    completed_requests = WasteRequest.objects.filter(status='completed').count()
    all_requests = WasteRequest.objects.all().order_by('-id')[:10]

    # Scrap Items
    scrap_items = ScrapCategory.objects.all()

    # Monthly Schedules
    MONTH_NAMES = {
        1: 'January', 2: 'February', 3: 'March', 4: 'April',
        5: 'May', 6: 'June', 7: 'July', 8: 'August',
        9: 'September', 10: 'October', 11: 'November', 12: 'December'
    }
    DEFAULT_SCHEDULES = {
        1: 'Plastic, Paper', 2: 'Glass, Metal', 3: 'Plastic, Paper',
        4: 'Glass, Metal', 5: 'Plastic, Paper', 6: 'Glass, Metal',
        7: 'Plastic, Paper', 8: 'Glass, Metal', 9: 'Plastic, Paper',
        10: 'Glass, Metal', 11: 'Plastic, Paper', 12: 'Glass, Metal'
    }
    schedules = []
    for month_num, month_name in MONTH_NAMES.items():
        schedule_obj, _ = MonthlyWasteSchedule.objects.get_or_create(
            month=month_num,
            defaults={'waste_items': DEFAULT_SCHEDULES.get(month_num, 'Plastic, Paper')}
        )
        items_list = [item.strip() for item in schedule_obj.waste_items.split(',') if item.strip()]
        schedules.append({
            'month_num': month_num,
            'month_name': month_name,
            'items': items_list
        })

    context = {
        'total_citizens': total_citizens,
        'total_workers': total_workers,
        'total_requests': total_requests,
        'completed_requests': completed_requests,
        'citizens': citizens,
        'hks_members': hks_members,
        'scrap_items': scrap_items,
        'schedules': schedules,
        'all_requests': all_requests,
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