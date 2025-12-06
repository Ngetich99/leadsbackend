from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Lead, Contact, Note, Correspondence, Reminder
from .serializers import (
    LeadSerializer, ContactSerializer, NoteSerializer,
    CorrespondenceSerializer, ReminderSerializer
)
from .permissions import IsManagerOrReadOnly, IsOwnerOrManager
from django.utils import timezone

class LeadViewSet(viewsets.ModelViewSet):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    permission_classes = [IsAuthenticated, IsManagerOrReadOnly, IsOwnerOrManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['first_name', 'last_name', 'email', 'company', 'phone']
    ordering_fields = ['created_at', 'updated_at', 'last_contacted']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_manager:
            return Lead.objects.all()
        return Lead.objects.filter(
            Q(assigned_to=user) | Q(created_by=user)
        )
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_note(self, request, pk=None):
        lead = self.get_object()
        serializer = NoteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(lead=lead, created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def add_reminder(self, request, pk=None):
        lead = self.get_object()
        serializer = ReminderSerializer(data=request.data)
        if serializer.is_valid():
            reminder = serializer.save(lead=lead, created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated, IsManagerOrReadOnly, IsOwnerOrManager]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['first_name', 'last_name', 'email', 'company', 'phone']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_manager:
            return Contact.objects.all()
        return Contact.objects.filter(created_by=user)
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_correspondence(self, request, pk=None):
        contact = self.get_object()
        serializer = CorrespondenceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(contact=contact, created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrManager]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_manager:
            return Note.objects.all()
        return Note.objects.filter(created_by=user)

class CorrespondenceViewSet(viewsets.ModelViewSet):
    queryset = Correspondence.objects.all()
    serializer_class = CorrespondenceSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrManager]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['date']
    ordering = ['-date']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_manager:
            return Correspondence.objects.all()
        return Correspondence.objects.filter(created_by=user)

class ReminderViewSet(viewsets.ModelViewSet):
    queryset = Reminder.objects.all()
    serializer_class = ReminderSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrManager]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['due_date']
    ordering = ['due_date']
    
    def get_queryset(self):
        user = self.request.user
        queryset = Reminder.objects.all()
        if not user.is_manager:
            queryset = queryset.filter(created_by=user)
        
        is_completed = self.request.query_params.get('is_completed', None)
        if is_completed is not None:
            queryset = queryset.filter(is_completed=is_completed.lower() == 'true')
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def mark_completed(self, request, pk=None):
        reminder = self.get_object()
        reminder.is_completed = True
        reminder.save()
        return Response({'status': 'reminder completed'})
