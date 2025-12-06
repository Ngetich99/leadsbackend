from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import Reminder, Lead
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def send_reminder_email(self, reminder_id):
    """Send reminder email for a specific reminder"""
    try:
        reminder = Reminder.objects.get(id=reminder_id, is_completed=False)
        
        # Check if reminder is still relevant (not too old)
        if reminder.due_date < timezone.now() - timedelta(hours=24):
            reminder.is_completed = True
            reminder.save()
            return f"Reminder {reminder_id} is too old, marked as completed"
        
        subject = f"Reminder: {reminder.title}"
        message = f"""
        Hello {reminder.created_by.get_full_name() or reminder.created_by.email},
        
        You have a reminder for lead: {reminder.lead.full_name}
        
        Title: {reminder.title}
        Description: {reminder.description}
        Priority: {reminder.get_priority_display()}
        Due: {reminder.due_date.strftime('%Y-%m-%d %H:%M')}
        
        Please take appropriate action.
        
        Best regards,
        CRM System
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[reminder.created_by.email],
            fail_silently=False,
        )
        
        logger.info(f"Reminder email sent for {reminder.title}")
        return f"Reminder email sent for {reminder.title}"
    
    except Reminder.DoesNotExist:
        logger.warning(f"Reminder {reminder_id} not found or already completed")
        return f"Reminder {reminder_id} not found or already completed"
    
    except Exception as e:
        logger.error(f"Failed to send reminder email: {e}")
        # Retry the task
        raise self.retry(exc=e, countdown=60)

@shared_task
def send_daily_reminders():
    """Send reminders for today"""
    today = timezone.now().date()
    tomorrow = today + timedelta(days=1)
    
    reminders = Reminder.objects.filter(
        due_date__date__range=[today, tomorrow],
        is_completed=False
    )
    
    sent_count = 0
    for reminder in reminders:
        try:
            send_reminder_email.delay(str(reminder.id))
            sent_count += 1
        except Exception as e:
            logger.error(f"Failed to schedule reminder {reminder.id}: {e}")
    
    return f"Scheduled {sent_count} daily reminders"

@shared_task
def send_hourly_reminders():
    """Send reminders for the next hour