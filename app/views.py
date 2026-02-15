from django.shortcuts import render
from django.http.request import HttpRequest
from .models import Student
from django.utils import timezone
import json
from datetime import date
from django.db.models import Count, Q, Max
from datetime import date, timedelta
# Create your views here.
def index_view(request):
    return render(request, "index.html")

def pm_students_view(request):
    students = Student.objects.all().exclude(priority1=0)
    context = {"students" : students}
    return render(request, "pm_students.html", context = context)

def vse_spiski_view(request):
    context=dict()
    students = Student.objects.all()
    context["students"] = students
    priority1_pm = len(students.filter(priority1 = 1))
    priority1_ivt = len(students.filter(priority2 = 1))
    priority1_itss = len(students.filter(priority3 = 1))
    priority1_ib = len(students.filter(priority4 = 1))
    context['priority1_pm'] = priority1_pm
    context['priority1_ivt'] = priority1_ivt
    context['priority1_itss'] = priority1_itss
    context['priority1_ib'] = priority1_ib
    k_pm: int = len(students.exclude(priority1 = 0))
    k_ivt: int = len(students.exclude(priority2 = 0))
    k_itss: int = len(students.exclude(priority3 = 0))
    k_ib: int = len(students.exclude(priority4 = 0))
    context['k_pm'] = k_pm
    context['k_ivt'] = k_ivt
    context['k_itss'] = k_itss
    context['k_ib'] = k_ib
    return render(request, "vse_spiski.html", context=context)

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
    students = Student.objects.all()
    #print(sorted(students, key=lambda student: student.ball_sum))
    context = {"students":students}
    priority1_pm: int   = len(students.filter(priority1 = 1))
    priority2_pm: int   = len(students.filter(priority1 = 2))
    priority3_pm: int   = len(students.filter(priority1 = 3))
    priority4_pm: int   = len(students.filter(priority1 = 4))
    priority1_ivt: int  = len(students.filter(priority2 = 1))
    priority2_ivt: int  = len(students.filter(priority2 = 2))
    priority3_ivt: int  = len(students.filter(priority2 = 3))
    priority4_ivt: int  = len(students.filter(priority2 = 4))
    priority1_itss: int = len(students.filter(priority3 = 1))
    priority2_itss: int = len(students.filter(priority3 = 2))
    priority3_itss: int = len(students.filter(priority3 = 3))
    priority4_itss: int = len(students.filter(priority3 = 4))
    priority1_ib: int   = len(students.filter(priority4 = 1))
    priority2_ib: int   = len(students.filter(priority4 = 1))
    priority3_ib: int   = len(students.filter(priority4 = 1))
    priority4_ib: int   = len(students.filter(priority4 = 1))
    context['priority1_pm'] = priority1_pm
    context['priority2_pm'] = priority2_pm
    context['priority3_pm'] = priority3_pm
    context['priority4_pm'] = priority4_pm
    context['priority1_ivt'] = priority1_ivt
    context['priority2_ivt'] = priority2_ivt
    context['priority3_ivt'] = priority3_ivt
    context['priority4_ivt'] = priority4_ivt
    context['priority1_itss'] = priority1_itss
    context['priority2_itss'] = priority2_itss
    context['priority3_itss'] = priority3_itss
    context['priority4_itss'] = priority4_itss
    context['priority1_ib'] = priority1_ib
    context['priority2_ib'] = priority2_ib
    context['priority3_ib'] = priority3_ib
    context['priority4_ib'] = priority4_ib
    
    return render(request, "all_students.html", context=context)

def all_students_report(request):
    students = Student.objects.all()
    context=dict()
    priority1_pm: int   = len(students.filter(priority1 = 1))
    priority2_pm: int   = len(students.filter(priority1 = 2))
    priority3_pm: int   = len(students.filter(priority1 = 3))
    priority4_pm: int   = len(students.filter(priority1 = 4))
    priority1_ivt: int  = len(students.filter(priority2 = 1))
    priority2_ivt: int  = len(students.filter(priority2 = 2))
    priority3_ivt: int  = len(students.filter(priority2 = 3))
    priority4_ivt: int  = len(students.filter(priority2 = 4))
    priority1_itss: int = len(students.filter(priority3 = 1))
    priority2_itss: int = len(students.filter(priority3 = 2))
    priority3_itss: int = len(students.filter(priority3 = 3))
    priority4_itss: int = len(students.filter(priority3 = 4))
    priority1_ib: int   = len(students.filter(priority4 = 1))
    priority2_ib: int   = len(students.filter(priority4 = 1))
    priority3_ib: int   = len(students.filter(priority4 = 1))
    priority4_ib: int   = len(students.filter(priority4 = 1))
    context['priority1_pm'] = priority1_pm
    context['priority2_pm'] = priority2_pm
    context['priority3_pm'] = priority3_pm
    context['priority4_pm'] = priority4_pm
    context['priority1_ivt'] = priority1_ivt
    context['priority2_ivt'] = priority2_ivt
    context['priority3_ivt'] = priority3_ivt
    context['priority4_ivt'] = priority4_ivt
    context['priority1_itss'] = priority1_itss
    context['priority2_itss'] = priority2_itss
    context['priority3_itss'] = priority3_itss
    context['priority4_itss'] = priority4_itss
    context['priority1_ib'] = priority1_ib
    context['priority2_ib'] = priority2_ib
    context['priority3_ib'] = priority3_ib
    context['priority4_ib'] = priority4_ib
    """
    Функция для формирования сводного отчёта приёмной комиссии
    """
    # Получаем всех абитуриентов, которые согласны на зачисление
    # (хотя бы одно согласие)
    students = Student.objects.filter(
        Q(agreement1=True) | Q(agreement2=True) | 
        Q(agreement3=True) | Q(agreement4=True)
    )
    
    # Коды направлений: ПМ - 1, ИВТ - 2, ИТСС - 3, ИБ - 4
    DIRECTIONS = {
        1: 'ПМ',
        2: 'ИВТ', 
        3: 'ИТСС',
        4: 'ИБ'
    }
    
    # 1. Общее количество заявлений по направлениям
    total_by_direction = {}
    for dir_code in DIRECTIONS.keys():
        total_by_direction[dir_code] = students.filter(
            Q(priority1=dir_code) | Q(priority2=dir_code) | 
            Q(priority3=dir_code) | Q(priority4=dir_code)
        ).count()
    
    # 2. Количество заявлений по приоритетам
    priority_stats = {}
    for dir_code in DIRECTIONS.keys():
        priority_stats[dir_code] = {
            'priority1': students.filter(priority1=dir_code).count(),
            'priority2': students.filter(priority2=dir_code).count(),
            'priority3': students.filter(priority3=dir_code).count(),
            'priority4': students.filter(priority4=dir_code).count(),
        }
    
    # 3. Зачисленные студенты по приоритетам
    enrolled_stats = {}
    for dir_code in DIRECTIONS.keys():
        enrolled_stats[dir_code] = {
            'priority1': students.filter(
                priority1=dir_code, 
                **{f'agreement{1}': True}
            ).count(),
            'priority2': students.filter(
                priority2=dir_code,
                **{f'agreement{2}': True}
            ).count(),
            'priority3': students.filter(
                priority3=dir_code,
                **{f'agreement{3}': True}
            ).count(),
            'priority4': students.filter(
                priority4=dir_code,
                **{f'agreement{4}': True}
            ).count(),
        }
    
    # 4. Динамика проходного балла за последние 4 дня
    dynamics_data = {}
    end_date = date.today()
    start_date = end_date - timedelta(days=3)
    
    for dir_code in DIRECTIONS.keys():
        dir_dynamics = []
        for i in range(4):
            current_date = start_date + timedelta(days=i)
            
            # Получаем всех абитуриентов с согласием на это направление до текущей даты
            candidates = Student.objects.filter(
                Q(priority1=dir_code, agreement1=True) |
                Q(priority2=dir_code, agreement2=True) |
                Q(priority3=dir_code, agreement3=True) |
                Q(priority4=dir_code, agreement4=True),
                date__lte=current_date
            ).order_by('-ball_sum')
            
            # Количество мест (можно вынести в отдельную модель)
            places = {
                1: 40,  # ПМ
                2: 50,  # ИВТ
                3: 30,  # ИТСС
                4: 20,  # ИБ
            }
            
            # Проходной балл - балл последнего зачисленного
            if candidates.count() >= places.get(dir_code, 0):
                passing_score = candidates[places.get(dir_code, 0) - 1].ball_sum
            elif candidates.count() > 0:
                passing_score = candidates.last().ball_sum
            else:
                passing_score = 0
                
            dir_dynamics.append(passing_score)
        
        dynamics_data[dir_code] = dir_dynamics
    
    # 5. Проходные баллы на сегодня
    today_passing = {}
    for dir_code in DIRECTIONS.keys():
        candidates = Student.objects.filter(
            Q(priority1=dir_code, agreement1=True) |
            Q(priority2=dir_code, agreement2=True) |
            Q(priority3=dir_code, agreement3=True) |
            Q(priority4=dir_code, agreement4=True)
        ).order_by('-ball_sum')
        
        places = {1: 40, 2: 50, 3: 30, 4: 20}
        
        if candidates.count() >= places.get(dir_code, 0):
            today_passing[dir_code] = candidates[places.get(dir_code, 0) - 1].ball_sum
        elif candidates.count() > 0:
            today_passing[dir_code] = candidates.last().ball_sum
        else:
            today_passing[dir_code] = 0
    
    # Подготавливаем данные для шаблона
    context = {
        # Общее количество заявлений
        'total_pm': total_by_direction.get(1, 0),
        'total_ivt': total_by_direction.get(2, 0),
        'total_itss': total_by_direction.get(3, 0),
        'total_ib': total_by_direction.get(4, 0),
        
        # Количество мест
        'places_pm': 40,
        'places_ivt': 50,
        'places_itss': 30,
        'places_ib': 20,
        
        # Проходные баллы на сегодня
        'passing_pm': today_passing.get(1, 0),
        'passing_ivt': today_passing.get(2, 0),
        'passing_itss': today_passing.get(3, 0),
        'passing_ib': today_passing.get(4, 0),
        
        # Заявления по приоритетам
        'priority1_pm': priority1_pm,
        'priority2_pm': priority2_pm,
        'priority3_pm': priority3_pm,
        'priority4_pm': priority4_pm,
        
        'priority1_ivt': priority1_ivt,
        'priority2_ivt': priority2_ivt,
        'priority3_ivt': priority3_ivt,
        'priority4_ivt': priority4_ivt,
        
        'priority1_itss': priority1_itss,
        'priority2_itss': priority2_itss,
        'priority3_itss': priority3_itss,
        'priority4_itss': priority4_itss,
        
        'priority1_ib': priority1_ib,
        'priority2_ib': priority2_ib,
        'priority3_ib': priority3_ib,
        'priority4_ib': priority4_ib,
        
        # Зачисленные по приоритетам
        'enrolled1_pm': enrolled_stats.get(1, {}).get('priority1', 0),
        'enrolled2_pm': enrolled_stats.get(1, {}).get('priority2', 0),
        'enrolled3_pm': enrolled_stats.get(1, {}).get('priority3', 0),
        'enrolled4_pm': enrolled_stats.get(1, {}).get('priority4', 0),
        
        'enrolled1_ivt': enrolled_stats.get(2, {}).get('priority1', 0),
        'enrolled2_ivt': enrolled_stats.get(2, {}).get('priority2', 0),
        'enrolled3_ivt': enrolled_stats.get(2, {}).get('priority3', 0),
        'enrolled4_ivt': enrolled_stats.get(2, {}).get('priority4', 0),
        
        'enrolled1_itss': enrolled_stats.get(3, {}).get('priority1', 0),
        'enrolled2_itss': enrolled_stats.get(3, {}).get('priority2', 0),
        'enrolled3_itss': enrolled_stats.get(3, {}).get('priority3', 0),
        'enrolled4_itss': enrolled_stats.get(3, {}).get('priority4', 0),
        
        'enrolled1_ib': enrolled_stats.get(4, {}).get('priority1', 0),
        'enrolled2_ib': enrolled_stats.get(4, {}).get('priority2', 0),
        'enrolled3_ib': enrolled_stats.get(4, {}).get('priority3', 0),
        'enrolled4_ib': enrolled_stats.get(4, {}).get('priority4', 0),
        
        # Данные для графиков динамики (в JSON формате для JavaScript)
        'dynamics_pm': json.dumps(dynamics_data.get(1, [0, 0, 0, 0])),
        'dynamics_ivt': json.dumps(dynamics_data.get(2, [0, 0, 0, 0])),
        'dynamics_itss': json.dumps(dynamics_data.get(3, [0, 0, 0, 0])),
        'dynamics_ib': json.dumps(dynamics_data.get(4, [0, 0, 0, 0])),
        
        # Даты для графиков
        'chart_dates': json.dumps([
            (date.today() - timedelta(days=3)).strftime('%d.%m'),
            (date.today() - timedelta(days=2)).strftime('%d.%m'),
            (date.today() - timedelta(days=1)).strftime('%d.%m'),
            date.today().strftime('%d.%m'),
        ]),
    }
    
    return render(request, 'all_students.html', context)

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