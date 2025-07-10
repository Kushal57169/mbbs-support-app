# community/utils.py
from .models import Notification

def send_notification(recipient, sender, type, message):
    Notification.objects.create(
        recipient=recipient,
        sender=sender,
        type=type,
        message=message
    )
