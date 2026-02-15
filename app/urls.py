from django.urls import path
from .views import test_view, all_students_view, rep_all_view, index_view, pm_students_view, vse_spiski_view

urlpatterns = [
    path('', index_view, name="index"),
    path('test', test_view, name='test'),
    path('all_students', all_students_view, name="all_students_view"),
    path('rep_all', rep_all_view, name = "rep_all"),
    path('pm_students', pm_students_view, name = "pm_students_view"),
    path('vse_spiski', vse_spiski_view, name = "vse_spiski_view"),
]