from django.contrib import admin
from .models import User, OBRecord, AuditLog, QueryLog

# models 
admin.site.register(User)
admin.site.register(OBRecord)
admin.site.register(AuditLog)
admin.site.register(QueryLog)