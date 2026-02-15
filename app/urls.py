from django.urls import path
from .views import (test_view, all_students_view, rep_all_view, index_view, pm_students_view, vse_spiski_view,
all_students_report, ivt_students_view, itss_students_view, ib_students_view, upload_students,
clear_database, total_students, debug_students, view_students_direct)

urlpatterns = [
    path('', index_view, name="index"),
    path('test', test_view, name='test'),
    path('all_students', all_students_report, name="all_students_view"),
    path('rep_all', rep_all_view, name = "rep_all"),
    path('pm_students', pm_students_view, name = "pm_students_view"),
    path('vse_spiski', vse_spiski_view, name = "vse_spiski_view"),
    path("ivt_students", ivt_students_view, name='ivt_students_view'),
    path('itss_students', itss_students_view, name='itss_students'),
    path('ib_students', ib_students_view, name='ib_students'),
    #path('upload-students', upload_students, name='upload_students'),
    #path('clear-database', clear_database, name='clear_database'),

    # API endpoints
    path('api/upload-students/', upload_students, name='upload_students'),
    path('api/clear-database/', clear_database, name='clear_database'),
    path('api/total-students/', total_students, name='total_students'),
    path('api/debug-students/', debug_students, name='debug_students'),
    path('view-students/', view_students_direct, name='view_students'),

]