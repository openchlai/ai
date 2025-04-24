from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from .models import Email
from .utils import forward_email_to_main_system

@receiver(post_save, sender=Email)
def forward_email(sender, instance, created, **kwargs):
    if created:
        print(f"New email saved: {instance.subject}")

        # Defer the forwarding logic until the transaction is committed
        transaction.on_commit(lambda: forward_email_to_main_system(instance))
