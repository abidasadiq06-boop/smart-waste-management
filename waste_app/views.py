from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import WasteRequestForm

def home(request):
    return render(request, 'waste_app/home.html')

@login_required
def create_request(request):
    if request.method == 'POST':
        form = WasteRequestForm(request.POST, request.FILES)
        if form.is_valid():
            waste_req = form.save(commit=False)
            waste_req.citizen = request.user
            waste_req.save()
            return redirect('home')
    else:
        form = WasteRequestForm()
    return render(request, 'waste_app/request_form.html', {'form': form})
    from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import WasteRequestForm
from .models import WasteRequest

def home(request):
    return render(request, 'waste_app/home.html')

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