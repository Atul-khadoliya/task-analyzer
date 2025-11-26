from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse

def analyze_placeholder(request):
    return JsonResponse({"status": "ok", "message": "analyze endpoint placeholder"})

def suggest_placeholder(request):
    return JsonResponse({"status": "ok", "message": "suggest endpoint placeholder"})
