from django.contrib import admin
from .models import Email

@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ('subject', 'sender', 'recipient', 'received_date', 'is_read')

