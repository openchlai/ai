from django.db import models

class Email(models.Model):
    sender = models.CharField(max_length=255)
    recipient = models.CharField(max_length=255)
    subject = models.TextField()
    body = models.TextField()
    received_date = models.DateTimeField()
    is_read = models.BooleanField(default=False)
    raw_message = models.BinaryField(default=None)  # Store raw email message


    def __str__(self):
        return f"Email from {self.sender} to {self.recipient}: {self.subject}"
