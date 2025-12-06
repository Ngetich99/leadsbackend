from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from auditlog.registry import auditlog
from auditlog.models import AuditlogHistoryField
import uuid

class Lead(models.Model):
    class Status(models.TextChoices):
        NEW = 'new', _('New')
        CONTACTED = 'contacted', _('Contacted')
        QUALIFIED = 'qualified', _('Qualified')
        PROPOSAL = 'proposal', _('Proposal')
        NEGOTIATION = 'negotiation', _('Negotiation')
        CLOSED_WON = 'closed_won', _('Closed Won')
        CLOSED_LOST = 'closed_lost', _('Closed Lost')
    
    class Priority(models.TextChoices):
        LOW = 'low', _('Low')
        MEDIUM = 'medium', _('Medium')
        HIGH = 'high', _('High')
        CRITICAL = 'critical', _('Critical')
    
    class Source(models.TextChoices):
        WEBSITE = 'website', _('Website')
        REFERRAL = 'referral', _('Referral')
        SOCIAL_MEDIA = 'social_media', _('Social Media')
        EMAIL = 'email', _('Email')
        PHONE = 'phone', _('Phone')
        EVENT = 'event', _('Event')
        OTHER = 'other', _('Other')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(_('first name'), max_length=100)
    last_name = models.CharField(_('last name'), max_length=100)
    company = models.CharField(_('company'), max_length=200, blank=True)
    job_title = models.CharField(_('job title'), max_length=200, blank=True)
    email = models.EmailField(_('email'))
    phone = models.CharField(_('phone'), max_length=20, blank=True)
    
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=Status.choices,
        default=Status.NEW
    )
    priority = models.CharField(
        _('priority'),
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM
    )
    source = models.CharField(
        _('source'),
        max_length=20,
        choices=Source.choices,
        default=Source.OTHER
    )
    
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_leads',
        verbose_name=_('assigned to')
    )
    
    value = models.DecimalField(
        _('value'),
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    
    address = models.TextField(_('address'), blank=True)
    city = models.CharField(_('city'), max_length=100, blank=True)
    state = models.CharField(_('state'), max_length=100, blank=True)
    country = models.CharField(_('country'), max_length=100, blank=True)
    postal_code = models.CharField(_('postal code'), max_length=20, blank=True)
    
    description = models.TextField(_('description'), blank=True)
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_leads',
        verbose_name=_('created by')
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    last_contacted = models.DateTimeField(_('last contacted'), null=True, blank=True)
    
    history = AuditlogHistoryField()
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Lead')
        verbose_name_plural = _('Leads')
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['assigned_to']),
            models.Index(fields=['created_at']),
            models.Index(fields=['last_contacted']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.company})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class Contact(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(_('first name'), max_length=100)
    last_name = models.CharField(_('last name'), max_length=100)
    email = models.EmailField(_('email'))
    phone = models.CharField(_('phone'), max_length=20, blank=True)
    
    company = models.CharField(_('company'), max_length=200, blank=True)
    job_title = models.CharField(_('job title'), max_length=200, blank=True)
    
    leads = models.ManyToManyField(
        Lead,
        related_name='contacts',
        blank=True,
        verbose_name=_('leads')
    )
    
    address = models.TextField(_('address'), blank=True)
    city = models.CharField(_('city'), max_length=100, blank=True)
    state = models.CharField(_('state'), max_length=100, blank=True)
    country = models.CharField(_('country'), max_length=100, blank=True)
    
    notes = models.TextField(_('notes'), blank=True)
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_contacts',
        verbose_name=_('created by')
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    history = AuditlogHistoryField()
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Contact')
        verbose_name_plural = _('Contacts')
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['company']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class Note(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lead = models.ForeignKey(
        Lead,
        on_delete=models.CASCADE,
        related_name='notes',
        verbose_name=_('lead')
    )
    content = models.TextField(_('content'))
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='notes',
        verbose_name=_('created by')
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Note')
        verbose_name_plural = _('Notes')
    
    def __str__(self):
        return f"Note for {self.lead}"

class Correspondence(models.Model):
    class Type(models.TextChoices):
        EMAIL = 'email', _('Email')
        PHONE = 'phone', _('Phone Call')
        MEETING = 'meeting', _('Meeting')
        MESSAGE = 'message', _('Message')
        OTHER = 'other', _('Other')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contact = models.ForeignKey(
        Contact,
        on_delete=models.CASCADE,
        related_name='correspondence',
        verbose_name=_('contact')
    )
    lead = models.ForeignKey(
        Lead,
        on_delete=models.CASCADE,
        related_name='correspondence',
        null=True,
        blank=True,
        verbose_name=_('lead')
    )
    
    type = models.CharField(
        _('type'),
        max_length=20,
        choices=Type.choices,
        default=Type.EMAIL
    )
    subject = models.CharField(_('subject'), max_length=200, blank=True)
    content = models.TextField(_('content'))
    date = models.DateTimeField(_('date'), auto_now_add=True)
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='correspondence',
        verbose_name=_('created by')
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        ordering = ['-date']
        verbose_name = _('Correspondence')
        verbose_name_plural = _('Correspondence')
        indexes = [
            models.Index(fields=['type']),
            models.Index(fields=['date']),
        ]
    
    def __str__(self):
        return f"{self.get_type_display()} with {self.contact}"

class Reminder(models.Model):
    class Priority(models.TextChoices):
        LOW = 'low', _('Low')
        MEDIUM = 'medium', _('Medium')
        HIGH = 'high', _('High')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lead = models.ForeignKey(
        Lead,
        on_delete=models.CASCADE,
        related_name='reminders',
        verbose_name=_('lead')
    )
    title = models.CharField(_('title'), max_length=200)
    description = models.TextField(_('description'), blank=True)
    due_date = models.DateTimeField(_('due date'))
    priority = models.CharField(
        _('priority'),
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM
    )
    is_completed = models.BooleanField(_('is completed'), default=False)
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reminders',
        verbose_name=_('created by')
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        ordering = ['due_date']
        verbose_name = _('Reminder')
        verbose_name_plural = _('Reminders')
        indexes = [
            models.Index(fields=['due_date']),
            models.Index(fields=['is_completed']),
            models.Index(fields=['priority']),
        ]
    
    def __str__(self):
        return f"Reminder: {self.title}"

# Register models with auditlog
auditlog.register(Lead, exclude_fields=['created_at', 'updated_at'])
auditlog.register(Contact, exclude_fields=['created_at', 'updated_at'])