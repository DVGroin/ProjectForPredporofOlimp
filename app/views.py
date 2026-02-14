from django.shortcuts import render
from django.http.request import HttpRequest
from .models import Student
from django.utils import timezone
import json
# Create your views here.

def test_view(request):
    return render(request, "index.html")

def all_students_view(request: HttpRequest):
    everything = Student.objects.all()
    obsch_kz = 0
    #for i in everything:
    #    if i
    context = {"students":everything}
    return render(request, "all_students.html", context=context)

def rep_all_view(request: HttpRequest):
    context=dict()
    report_date = timezone.now()
    data = {
        'pm': {
            'total_applications': 156,
            'places': 40,
            'priority_1_apps': 45,
            'priority_2_apps': 40,
            'priority_3_apps': 35,
            'priority_4_apps': 36,
            'enrolled_1': 25,
            'enrolled_2': 10,
            'enrolled_3': 5,
            'enrolled_4': 0,
            'last_day_score': 195,  # Проходной балл за последний день
        },
        'ivt': {
            'total_applications': 203,
            'places': 50,
            'priority_1_apps': 60,
            'priority_2_apps': 55,
            'priority_3_apps': 50,
            'priority_4_apps': 38,
            'enrolled_1': 30,
            'enrolled_2': 12,
            'enrolled_3': 8,
            'enrolled_4': 0,
            'last_day_score': 178,
        },
        'itss': {
            'total_applications': 98,
            'places': 30,
            'priority_1_apps': 25,
            'priority_2_apps': 30,
            'priority_3_apps': 25,
            'priority_4_apps': 18,
            'enrolled_1': 15,
            'enrolled_2': 8,
            'enrolled_3': 5,
            'enrolled_4': 2,
            'last_day_score': 165,
        },
        'ib': {
            'total_applications': 145,
            'places': 20,
            'priority_1_apps': 40,
            'priority_2_apps': 35,
            'priority_3_apps': 30,
            'priority_4_apps': 40,
            'enrolled_1': 12,
            'enrolled_2': 5,
            'enrolled_3': 3,
            'enrolled_4': 0,
            'last_day_score': 188,
        }
    }
    
    # Данные для графиков (динамика за 4 дня)
    dynamics_dates = ['11.02', '12.02', '13.02', '14.02']
    dynamics = {
        'pm': json.dumps([185, 192, 188, 195]),
        'ivt': json.dumps([170, 175, 182, 178]),
        'itss': json.dumps([155, 160, 158, 165]),
        'ib': json.dumps([190, 185, 193, 188]),
    }
    
    # Последняя дата для проходного балла
    last_day_date = timezone.now().date()
    
    context = {
        'report_date': report_date,
        'data': data,
        'dynamics_dates': json.dumps(dynamics_dates),
        'dynamics': dynamics,
        'last_day_date': last_day_date,
    }
    return render(request, "rep_all.html", context = context)