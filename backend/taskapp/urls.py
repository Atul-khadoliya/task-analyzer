from django.urls import path
from . import views

urlpatterns = [
    path('analyze/', views.analyze_placeholder),
    path('suggest/', views.suggest_placeholder),
]
