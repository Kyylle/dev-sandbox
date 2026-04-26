from django.urls import path
from . import views

urlpatterns = [
    path('teachers/',   views.coming_soon, {'module': 'Teachers'},   name='teachers'),
    path('subjects/',   views.coming_soon, {'module': 'Subjects'},   name='subjects'),
    path('enrollment/', views.coming_soon, {'module': 'Enrollment'}, name='enrollment'),
    path('attendance/', views.coming_soon, {'module': 'Attendance'}, name='attendance'),
    path('grades/',     views.coming_soon, {'module': 'Grades'},     name='grades'),
]       