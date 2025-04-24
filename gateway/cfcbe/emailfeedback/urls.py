from django.urls import path
from .views import EmailListCreateView, EmailDetailView

urlpatterns = [
    path('emails/', EmailListCreateView.as_view(), name='email-list-create'),
    path('emails/<int:pk>/', EmailDetailView.as_view(), name='email-detail'),
]