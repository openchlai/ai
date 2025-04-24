from django.db import models
import uuid


# Model for storing information about Victims or Perpetrators
class Person(models.Model):
    name = models.CharField(max_length=255)
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=50, null=True, blank=True)
    additional_info = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

# Enum choices for categorizing complaints
# class ComplaintCategory(models.TextChoices):
#     ABUSE = 'ABUSE', 'Abuse'
#     HARASSMENT = 'HARASSMENT', 'Harassment'
#     FRAUD = 'FRAUD', 'Fraud'
#     NEGLECT = 'NEGLECT', 'Neglect'
#     OTHER = 'OTHER', 'Other'

# Model to represent a Complaint
class Complaint(models.Model):
    complaint_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    session_id = models.UUIDField(default=uuid.uuid4, null=True, blank=True) 
    timestamp = models.DateTimeField(auto_now_add=True)
    reporter_nickname = models.CharField(max_length=100, null=True, blank=True)
    case_category = models.CharField(max_length=255, default="Not Specified", null=True, blank=True)
    complaint_text = models.TextField(blank=True, null=True)
    complaint_image = models.ImageField(upload_to="complaints/images/", blank=True, null=True)
    complaint_audio = models.FileField(upload_to="complaints/audio/", blank=True, null=True)  # Change from BinaryField
    complaint_video = models.FileField(upload_to="complaints/videos/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    message_id_ref = models.CharField(max_length=255, null=True, blank=True)
    
    victim = models.ForeignKey(Person, related_name='victims', on_delete=models.CASCADE, null=True, blank=True)
    perpetrator = models.ForeignKey(Person, related_name='perpetrators', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Complaint {self.complaint_id} by {self.reporter_nickname}"




# Model for Case Notes (to document updates or notes related to the case)
class CaseNote(models.Model):
    complaint = models.ForeignKey(Complaint, related_name='case_notes', on_delete=models.CASCADE)
    note_text = models.TextField()
    note_audio = models.BinaryField(blank=True, null=True)  # Optional audio note
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=255)  # This could be an agent's name or system

    def __str__(self):
        return f"CaseNote for {self.complaint.complaint_id} on {self.created_at}"

# Model for storing the status of a complaint (e.g., Under Investigation, Resolved, etc.)
class ComplaintStatus(models.Model):
    complaint = models.OneToOneField(Complaint, on_delete=models.CASCADE)
    status = models.CharField(max_length=100)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.CharField(max_length=255)  # This could be an agent's name or system

    def __str__(self):
        return f"Status for Complaint {self.complaint.complaint_id}: {self.status}"



class Notification(models.Model):
    notification_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    complaint = models.ForeignKey('Complaint', on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for Complaint {self.complaint.complaint_id}"

class Voicenotes (models.Model):
    # complaint = models.ForeignKey('Complaint', on_delete=models.CASCADE, related_name='voicenotes')
    voicenote = models.BinaryField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Voicenote for Complaint {self.complaint.complaint_id}"
