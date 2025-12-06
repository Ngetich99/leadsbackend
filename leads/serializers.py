from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Lead, Contact, Note, Correspondence, Reminder

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'role']

class NoteSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    
    class Meta:
        model = Note
        fields = ['id', 'lead', 'content', 'created_by', 'created_at', 'updated_at']
        read_only_fields = ['created_by', 'created_at', 'updated_at']

class CorrespondenceSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    
    class Meta:
        model = Correspondence
        fields = ['id', 'contact', 'lead', 'type', 'subject', 'content', 
                 'date', 'created_by', 'created_at', 'updated_at']
        read_only_fields = ['created_by', 'created_at', 'updated_at']

class ReminderSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    
    class Meta:
        model = Reminder
        fields = ['id', 'lead', 'title', 'description', 'due_date', 
                 'priority', 'is_completed', 'created_by', 'created_at', 'updated_at']
        read_only_fields = ['created_by', 'created_at', 'updated_at']

class ContactSerializer(serializers.ModelSerializer):
    leads = serializers.PrimaryKeyRelatedField(many=True, queryset=Lead.objects.all(), required=False)
    created_by = UserSerializer(read_only=True)
    
    class Meta:
        model = Contact
        fields = ['id', 'first_name', 'last_name', 'email', 'phone', 'company',
                 'job_title', 'leads', 'address', 'city', 'state', 'country',
                 'notes', 'created_by', 'created_at', 'updated_at']
        read_only_fields = ['created_by', 'created_at', 'updated_at']

class LeadSerializer(serializers.ModelSerializer):
    assigned_to = UserSerializer(read_only=True)
    assigned_to_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='agent'),
        source='assigned_to',
        write_only=True,
        required=False,
        allow_null=True
    )
    contacts = ContactSerializer(many=True, read_only=True)
    notes = NoteSerializer(many=True, read_only=True)
    reminders = ReminderSerializer(many=True, read_only=True)
    correspondence = CorrespondenceSerializer(many=True, read_only=True)
    created_by = UserSerializer(read_only=True)
    
    class Meta:
        model = Lead
        fields = ['id', 'first_name', 'last_name', 'company', 'job_title',
                 'email', 'phone', 'status', 'priority', 'source',
                 'assigned_to', 'assigned_to_id', 'value', 'address',
                 'city', 'state', 'country', 'postal_code', 'description',
                 'contacts', 'notes', 'reminders', 'correspondence',
                 'created_by', 'created_at', 'updated_at', 'last_contacted']
        read_only_fields = ['created_by', 'created_at', 'updated_at', 'last_contacted']
