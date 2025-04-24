from django.shortcuts import render
from rest_framework import generics
from .models import Email
from .serializers import EmailSerializer

# Create your views here.
class EmailListCreateView(generics.ListCreateAPIView):
    queryset = Email.objects.all()
    serializer_class = EmailSerializer

class EmailDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Email.objects.all()
    serializer_class = EmailSerializer