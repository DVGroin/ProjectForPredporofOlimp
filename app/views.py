from django.shortcuts import render
from django.http.request import HttpRequest
from .models import Student, Student1dayago, Student2dayago, Student3dayago
from django.utils import timezone
import json
from datetime import date
from django.db.models import Count, Q, Max
from datetime import date, timedelta
# Create your views here.

def get_enrolled_students_by_priority():
    """
    Возвращает словарь с зачисленными студентами по каждому направлению,
    учитывая только наивысший приоритет, по которому студент проходит
    """
    # Все студенты с хотя бы одним согласием
    all_students = Student.objects.filter(
        Q(agreement1=True) | Q(agreement2=True) | 
        Q(agreement3=True) | Q(agreement4=True)
    )
    
    # Количество мест по направлениям
    places = {1: 40, 2: 50, 3: 30, 4: 20}
    
    # Словари для хранения зачисленных по каждому направлению
    enrolled_by_direction = {1: [], 2: [], 3: [], 4: []}
    
    # Сначала собираем всех студентов с их наивысшим приоритетом
    students_with_top_priority = []
    
    for student in all_students:
        # Определяем наивысший приоритет, по которому есть согласие
        top_priority = None
        if student.agreement1 and student.priority1 > 0:
            top_priority = student.priority1
        elif student.agreement2 and student.priority2 > 0:
            top_priority = student.priority2
        elif student.agreement3 and student.priority3 > 0:
            top_priority = student.priority3
        elif student.agreement4 and student.priority4 > 0:
            top_priority = student.priority4
        
        if top_priority:
            students_with_top_priority.append({
                'student': student,
                'direction': top_priority,
                'ball_sum': student.ball_sum,
                'priority_level': 1 if student.agreement1 and student.priority1 == top_priority else
                                2 if student.agreement2 and student.priority2 == top_priority else
                                3 if student.agreement3 and student.priority3 == top_priority else 4
            })
    
    # Сортируем всех студентов по баллам (от высшего к низшему)
    students_with_top_priority.sort(key=lambda x: x['ball_sum'], reverse=True)
    
    # Распределяем по направлениям с учётом лимитов мест
    for student_data in students_with_top_priority:
        direction = student_data['direction']
        student = student_data['student']
        
        # Если ещё есть места на этом направлении
        if len(enrolled_by_direction[direction]) < places.get(direction, 0):
            enrolled_by_direction[direction].append({
                'student': student,
                'ball_sum': student.ball_sum,
                'priority': student_data['priority_level']
            })
    
    # Сортируем зачисленных по баллам (для каждого направления)
    for direction in enrolled_by_direction:
        enrolled_by_direction[direction].sort(key=lambda x: x['ball_sum'], reverse=True)
    
    return enrolled_by_direction


def index_view(request):
    return render(request, "index.html")

def pm_students_view(request):
    students = Student.objects.all().exclude(priority1=0)
    context = {"students" : students}
    return render(request, "pm_students.html", context = context)

def vse_spiski_view(request):
    num_op = {
        1:"ПМ",
        2:"ИВТ",
        3:"ИТСС",
        4:"ИБ",
    }
    context=dict()
    context['num_op'] = num_op
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
    
    # 2. Количество заявлений по приоритетам (ВСЕ поданные заявления)
    priority_stats = {}
    for dir_code in DIRECTIONS.keys():
        priority_stats[dir_code] = {
            'priority1': students.filter(priority1=dir_code).count(),
            'priority2': students.filter(priority2=dir_code).count(),
            'priority3': students.filter(priority3=dir_code).count(),
            'priority4': students.filter(priority4=dir_code).count(),
        }
    
    # 3. Зачисленные студенты по приоритетам (с учётом только высшего приоритета)
    enrolled_by_direction = get_enrolled_students_by_priority()

    # Инициализируем статистику по приоритетам для каждого направления
    enrolled_stats = {}
    for dir_code in DIRECTIONS.keys():
        enrolled_stats[dir_code] = {
            'priority1': 0,
            'priority2': 0,
            'priority3': 0,
            'priority4': 0,
        }

    # Подсчитываем зачисленных по каждому приоритету
    for direction, students in enrolled_by_direction.items():
        for student in students:
            # Определяем, по какому приоритету студент зачислен
            if student.priority1 == direction and student.agreement1:
                enrolled_stats[direction]['priority1'] += 1
            elif student.priority2 == direction and student.agreement2:
                enrolled_stats[direction]['priority2'] += 1
            elif student.priority3 == direction and student.agreement3:
                enrolled_stats[direction]['priority3'] += 1
            elif student.priority4 == direction and student.agreement4:
                enrolled_stats[direction]['priority4'] += 1
    
    # 4. Динамика проходного балла за последние 4 дня
    dynamics_data = {}
    end_date = date.today()
    start_date = end_date - timedelta(days=3)
    places = {1: 40, 2: 50, 3: 30, 4: 20}

    for dir_code in DIRECTIONS.keys():
        dir_dynamics = []
        
        for i in range(4):
            current_date = start_date + timedelta(days=i)
            
            # Получаем всех студентов с согласием на эту дату
            students_on_date = Student.objects.filter(
                Q(agreement1=True) | Q(agreement2=True) | 
                Q(agreement3=True) | Q(agreement4=True),
                date__lte=current_date
            )
            
            # Определяем зачисленных на эту дату (аналогично основной логике)
            temp_enrolled = {1: [], 2: [], 3: [], 4: []}
            temp_students = []
            
            for student in students_on_date:
                top_priority = None
                if student.agreement1 and student.priority1 > 0:
                    top_priority = student.priority1
                elif student.agreement2 and student.priority2 > 0:
                    top_priority = student.priority2
                elif student.agreement3 and student.priority3 > 0:
                    top_priority = student.priority3
                elif student.agreement4 and student.priority4 > 0:
                    top_priority = student.priority4
                
                if top_priority:
                    temp_students.append({
                        'student': student,
                        'direction': top_priority,
                        'ball_sum': student.ball_sum
                    })
            
            # Сортируем и распределяем
            temp_students.sort(key=lambda x: x['ball_sum'], reverse=True)
            for s_data in temp_students:
                dir_code_temp = s_data['direction']
                if len(temp_enrolled[dir_code_temp]) < places.get(dir_code_temp, 0):
                    temp_enrolled[dir_code_temp].append(s_data['student'])
            
            # Берём зачисленных на конкретное направление
            enrolled_on_date = temp_enrolled.get(dir_code, [])
            enrolled_on_date_sorted = sorted(enrolled_on_date, key=lambda x: x.ball_sum, reverse=True)
            
            total_places = places.get(dir_code, 0)
            
            # Определяем проходной балл на эту дату
            if len(enrolled_on_date_sorted) >= total_places:
                passing_score = enrolled_on_date_sorted[total_places - 1].ball_sum
            elif len(enrolled_on_date_sorted) > 0:
                passing_score = enrolled_on_date_sorted[-1].ball_sum
            else:
                passing_score = 0
                
            dir_dynamics.append(passing_score)
        
        dynamics_data[dir_code] = dir_dynamics
    
        # 5. Проходные баллы на сегодня с учётом реального зачисления
    today_passing = {}
    for dir_code in DIRECTIONS.keys():
        # Берём зачисленных студентов на это направление
        enrolled_students = enrolled_by_direction.get(dir_code, [])
        enrolled_students_sorted = sorted(enrolled_students, key=lambda x: x.ball_sum, reverse=True)
        
        places = {1: 40, 2: 50, 3: 30, 4: 20}
        total_places = places.get(dir_code, 0)
        
        # Проверяем, хватает ли абитуриентов
        if len(enrolled_students_sorted) >= total_places:
            # Есть конкурс - показываем проходной балл (балл последнего зачисленного)
            today_passing[dir_code] = enrolled_students_sorted[total_places - 1].ball_sum
        else:
            # Недобор
            today_passing[dir_code] = "НЕДОБОР"
    
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
        'passing_pm': today_passing.get(1, "НЕДОБОР"),
        'passing_ivt': today_passing.get(2, "НЕДОБОР"),
        'passing_itss': today_passing.get(3, "НЕДОБОР"),
        'passing_ib': today_passing.get(4, "НЕДОБОР"),
        
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