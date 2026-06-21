from django.db import models
from django.contrib.auth.models import AbstractUser
from pgvector.django import VectorField


class User(AbstractUser):
    ROLE_CHOICES = [
        ('officer', 'Police Officer'),
        ('admin', 'Administrator'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='officer')
    full_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'users'


class OBRecord(models.Model):
    ob_id = models.AutoField(primary_key=True)
    ob_number = models.CharField(max_length=20, unique=True)
    date_reported = models.DateField()
    case_type = models.CharField(max_length=50)
    location = models.CharField(max_length=100)
    complainant_name = models.CharField(max_length=150, blank=True, null=True)
    suspect_names = models.TextField(blank=True, null=True)
    case_summary = models.TextField()
    investigating_officer = models.CharField(max_length=100, blank=True, null=True)
    embedding = VectorField(dimensions=384, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ob_records'

    def __str__(self):
        return self.ob_number


class AuditLog(models.Model):
    log_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action_type = models.CharField(max_length=50)
    affected_table = models.CharField(max_length=50, blank=True, null=True)
    affected_record_id = models.IntegerField(null=True, blank=True)
    action_details = models.TextField(blank=True, null=True)
    ip_address = models.CharField(max_length=45, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'audit_logs'

    def __str__(self):
        return f"{self.action_type} by {self.user.username if self.user else 'Unknown'}"


class QueryLog(models.Model):
    query_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    query_text = models.TextField()
    query_embedding = VectorField(dimensions=384, null=True, blank=True)
    result_count = models.IntegerField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'query_logs'

    def __str__(self):
        return f"{self.user.username}: {self.query_text[:50]}..."