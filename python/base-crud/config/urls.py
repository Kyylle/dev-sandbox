from django.contrib import admin
from django.urls import path, include

handler404 = 'core.views.error_404'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),
    path('students/', include('students.urls')),
    path('',            include('core.urls')),
]