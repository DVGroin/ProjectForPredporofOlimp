from django.urls import path
from .views import test_view, all_students_view

urlpatterns = [
    path('', test_view, name="index"),
    path('test', test_view, name='test'),
    path('all_students', all_students_view, name="all_students_view")
]