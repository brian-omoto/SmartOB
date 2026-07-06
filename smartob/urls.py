from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    # Custom URLs FIRST (so they take priority)
    path('', include('ob_records.urls')),
    # Django admin LAST
    path('admin/', admin.site.urls),
]