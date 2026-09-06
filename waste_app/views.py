from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return HttpResponse("<h1>Smart Waste Management System</h1><p>Home Page Working Successfully!</p>")