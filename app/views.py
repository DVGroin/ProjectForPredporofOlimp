from django.shortcuts import render
from django.http.request import HttpRequest
from .models import Student
from django.utils import timezone
import json
from datetime import date
# Create your views here.

def test_view(request):
    Student.objects.create(student_id=1,
        ball_pro=80,
        ball_rus=0,      # добавьте все поля
        ball_mat=0,
        ball_ind=0,
        ball_sum=0,
        priority1=1,
        priority2=0,     # все priority должны быть заполнены
        priority3=0,
        priority4=0,
        agreement1=True,
        agreement2=False,
        agreement3=True,
        agreement4=True,
        date=date(2025, 8, 1))
    '''try:
        
        newStudent = Student(
        student_id=1,
        ball_pro=80,
        ball_rus=0,      # добавьте все поля
        ball_mat=0,
        ball_ind=0,
        ball_sum=0,
        priority1=1,
        priority2=0,     # все priority должны быть заполнены
        priority3=0,
        priority4=0,
        agreement1=True,
        agreement2=False,
        agreement3=True,
        agreement4=True,
        date=date(2025, 8, 1)
    )
        newStudent.save()
        print("Запись успешно создана!")
        print(newStudent)
    except Exception as e:
        print(f"Ошибка: {e}")'''

    return render(request, "index.html")

def all_students_view(request: HttpRequest):
    everything = Student.objects.all()
    obsch_kz = 0
    #for i in everything:
    #    if i
    context = {"students":everything}
    return render(request, "all_students.html", context=context)

def rep_all_view(request: HttpRequest):
    students = Student.objects.all()
    context=dict()
    report_date = timezone.now()
    data: dict[dict[str | int | any]] = {
        'pm': {
            'total_applications': 0,#156,
            'places': 40,
            'priority_1_apps': 0,#45,
            'priority_2_apps': 0,#40,
            'priority_3_apps': 0,#35,
            'priority_4_apps': 0,#36,
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
    for student in students:
        if student.priority1 == 1:
            data['pm']['priority_1_apps']+=1
        elif student.priority1 == 2:
            data['pm']['priority_2_apps']+=1
        elif student.priority1 == 3:
            data['pm']['priority_3_apps']+=1
        elif student.priority1 == 4:
            data['pm']['priority_4_apps']+=1
    data['pm']['total_applications'] = data['pm']['priority_1_apps']+data['pm']['priority_2_apps']+data['pm']['priority_3_apps']+data['pm']['priority_4_apps']
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