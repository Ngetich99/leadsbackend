from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import Reminder
from datetime import timedelta

@shared_task
def send_reminder_email(reminder_id):
    try:
        reminder = Reminder.objects.get(id=reminder_id, is_completed=False)
        
        subject = f"Reminder: {reminder.title}"
        message = f"""
        You have a reminder for lead: {reminder.lead}
        
        Title: {reminder.title}
        Description: {reminder.description}
        Priority: {reminder.priority}
        Due: {reminder.due_date}
        
        Please take appropriate action.
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[reminder.created_by.email],
            fail_silently=False,
        )
        
        return f"Reminder email sent for {reminder.title}"
    except Reminder.DoesNotExist:
        return f"Reminder {reminder_id} not found or already completed"

@shared_task
def send_daily_reminders():
    tomorrow = timezone.now() + timedelta(days=1)
    reminders = Reminder.objects.filter(
        due_date__date=tomorrow.date(),
        is_completed=False
    )
    
    for reminder in reminders:
        send_reminder_email.delay(str(reminder.id))
    
    return f"Sent {len(reminders)} daily reminders"
