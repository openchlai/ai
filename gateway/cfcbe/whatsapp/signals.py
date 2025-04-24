from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from .models import WhatsAppMessage
from .utils import forward_whatsapp_message_to_main_system

@receiver(post_save, sender=WhatsAppMessage)
def forward_whatsapp_message(sender, instance, created, **kwargs):
    if created:
        print(f"New WhatsApp Message saved: {instance.sender}")

        # Defer the forwarding logic until the transaction is committed
        transaction.on_commit(lambda: forward_whatsapp_message_to_main_system(instance))
