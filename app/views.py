from django.shortcuts import render
from django.http.request import HttpRequest
from .models import Student, Student1dayago, Student2dayago, Student3dayago, DynBal
from django.utils import timezone
import json
from datetime import date, datetime
from django.db.models import Count, Q, Max
from datetime import date, timedelta
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import csv
import os
from django.db import transaction
import logging
import traceback
# Create your views here.

logger = logging.getLogger(__name__)

def get_enrolled_for_date(target_date):
    """
    Возвращает словарь {direction: [студенты]} для даты target_date
    с учётом наивысшего приоритета и ограничений по местам.
    Каждый элемент списка содержит 'student', 'ball_sum', 'priority_level'.
    """
    places = {1: 40, 2: 50, 3: 30, 4: 20}
    enrolled_by_direction = {1: [], 2: [], 3: [], 4: []}

    # Все студенты с согласием на указанную дату или ранее
    all_students = Student.objects.filter(
        Q(agreement1=True) | Q(agreement2=True) | Q(agreement3=True) | Q(agreement4=True),
        date__lte=target_date
    )

    students_with_top_priority = []
    for student in all_students:
        top_priority = None
        priority_level = 0
        if student.agreement1 and student.priority1 > 0:
            top_priority = student.priority1
            priority_level = 1
        elif student.agreement2 and student.priority2 > 0:
            top_priority = student.priority2
            priority_level = 2
        elif student.agreement3 and student.priority3 > 0:
            top_priority = student.priority3
            priority_level = 3
        elif student.agreement4 and student.priority4 > 0:
            top_priority = student.priority4
            priority_level = 4

        if top_priority:
            students_with_top_priority.append({
                'student': student,
                'direction': top_priority,
                'ball_sum': student.ball_sum,
                'priority_level': priority_level
            })

    # Сортировка по убыванию баллов
    students_with_top_priority.sort(key=lambda x: x['ball_sum'], reverse=True)

    # Распределение по направлениям
    for s in students_with_top_priority:
        d = s['direction']
        if len(enrolled_by_direction[d]) < places.get(d, 0):
            enrolled_by_direction[d].append(s)

    return enrolled_by_direction

def update_passing_scores(target_date):
    """
    Рассчитывает проходные баллы для всех направлений на target_date
    и сохраняет их в таблицу DynBal.
    """
    places = {1: 40, 2: 50, 3: 30, 4: 20}
    enrolled = get_enrolled_for_date(target_date)

    for direction, students in enrolled.items():
        passing = None
        if len(students) >= places[direction]:
            # Проходной балл – балл последнего зачисленного (индекс places-1)
            passing = students[places[direction] - 1]['ball_sum']

        DynBal.objects.update_or_create(
            direction=direction,
            date=target_date,
            defaults={'passing_score': passing}
        )

def view_students_direct(request):
    """Прямой просмотр студентов в БД"""
    students = Student.objects.all()#.order_by('-ball_sum')
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Просмотр БД</title>
        <style>
            body {{ font-family: Arial; margin: 20px; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #4CAF50; color: white; }}
            tr:nth-child(even) {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        <h1>Студенты в базе данных (таблица: {Student._meta.db_table})</h1>
        <p>Всего записей: {students.count()}</p>
        <table>
            <tr>
                <th>ID</th>
                <th>Сумма баллов</th>
                <th>Приоритет 1</th>
                <th>Приоритет 2</th>
                <th>Приоритет 3</th>
                <th>Приоритет 4</th>
                <th>Согласие 1</th>
                <th>Согласие 2</th>
                <th>Согласие 3</th>
                <th>Согласие 4</th>
                <th>Дата</th>
            </tr>
    """
    
    for s in students:
        html += f"""
            <tr>
                <td>{s.student_id}</td>
                <td><strong>{s.ball_sum}</strong></td>
                <td>{s.priority1}</td>
                <td>{s.priority2}</td>
                <td>{s.priority3}</td>
                <td>{s.priority4}</td>
                <td>{'✅' if s.agreement1 else '❌'}</td>
                <td>{'✅' if s.agreement2 else '❌'}</td>
                <td>{'✅' if s.agreement3 else '❌'}</td>
                <td>{'✅' if s.agreement4 else '❌'}</td>
                <td>{s.date}</td>
            </tr>
        """
    
    html += """
        </table>
    </body>
    </html>
    """
    
    return HttpResponse(html)

def debug_students(request):
    """
    Временная функция для отладки - показывает всех студентов в БД
    """
    students = Student.objects.all().values('student_id', 'ball_sum', 'priority1', 'priority2', 'priority3', 'priority4')
    return JsonResponse({'students': list(students), 'count': students.count()})

@csrf_exempt
def upload_students(request):
    """
    Загрузка и обработка CSV файла со списком абитуриентов
    Формат файла: DD.MM_НАПРАВЛЕНИЕ.csv (например: 01.08_ИБ.csv)
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не поддерживается'}, status=405)
    
    # Для отладки - полная информация о запросе
    debug_info = {
        'request_method': request.method,
        'files_keys': list(request.FILES.keys()) if request.FILES else [],
        'has_file': 'file' in request.FILES,
    }
    
    try:
        # Получаем файл из запроса
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return JsonResponse({
                'error': 'Файл не найден',
                'debug': debug_info
            }, status=400)
        
        debug_info['filename'] = uploaded_file.name
        debug_info['file_size'] = uploaded_file.size
        debug_info['content_type'] = uploaded_file.content_type
        
        # Проверяем расширение файла
        if not uploaded_file.name.endswith('.csv'):
            return JsonResponse({
                'error': 'Файл должен быть в формате CSV',
                'debug': debug_info
            }, status=400)
        
        # Парсим имя файла для получения даты и направления
        filename = uploaded_file.name
        try:
            # Ожидаемый формат: DD.MM_НАПРАВЛЕНИЕ.csv
            file_part = filename.replace('.csv', '')
            date_part, direction = file_part.split('_')
            day, month = map(int, date_part.split('.'))
            
            # Определяем год (текущий)
            current_year = datetime.now().year
            file_date = datetime(current_year, month, day).date()
            print(file_date)
            debug_info['direction'] = direction
            debug_info['file_date'] = str(file_date)
            
        except Exception as e:
            return JsonResponse({
                'error': 'Неверный формат имени файла. Ожидается: DD.MM_НАПРАВЛЕНИЕ.csv',
                'details': str(e),
                'debug': debug_info
            }, status=400)
        
        # Определяем соответствие направления и полей в БД
        direction_mapping = {
            'ПМ': {'priority_field': 'priority1', 'agreement_field': 'agreement1', 'priority_value': 1},
            'ИВТ': {'priority_field': 'priority2', 'agreement_field': 'agreement2', 'priority_value': 2},
            'ИТСС': {'priority_field': 'priority3', 'agreement_field': 'agreement3', 'priority_value': 3},
            'ИБ': {'priority_field': 'priority4', 'agreement_field': 'agreement4', 'priority_value': 4},
        }
        
        if direction not in direction_mapping:
            return JsonResponse({
                'error': f'Неизвестное направление: {direction}. Допустимые: ПМ, ИВТ, ИТСС, ИБ',
                'debug': debug_info
            }, status=400)
        
        priority_info = direction_mapping[direction]
        
        # Читаем CSV файл
        try:
            # Читаем файл как байты и декодируем
            file_content = uploaded_file.read()
            
            # Пробуем разные кодировки
            decoded_content = None
            encodings = ['utf-8-sig', 'windows-1251', 'utf-8', 'cp1251']
            
            for encoding in encodings:
                try:
                    decoded_content = file_content.decode(encoding)
                    debug_info['encoding_used'] = encoding
                    break
                except UnicodeDecodeError:
                    continue
            
            if decoded_content is None:
                return JsonResponse({
                    'error': 'Не удалось прочитать файл ни в одной из кодировок',
                    'debug': debug_info
                }, status=400)
            
            # Разбиваем на строки
            lines = decoded_content.splitlines()
            debug_info['lines_count'] = len(lines)
            
            if len(lines) < 2:
                return JsonResponse({
                    'error': 'Файл слишком короткий',
                    'debug': debug_info
                }, status=400)
            
            # Создаем DictReader
            reader = csv.DictReader(lines)
            fieldnames = reader.fieldnames
            debug_info['fieldnames'] = fieldnames
            
            if not fieldnames:
                return JsonResponse({
                    'error': 'CSV файл не содержит заголовков',
                    'debug': debug_info
                }, status=400)
            
        except Exception as e:
            return JsonResponse({
                'error': f'Ошибка чтения CSV файла: {str(e)}',
                'debug': debug_info
            }, status=400)
        
        # Проверяем подключение к БД
        try:
            # Пробуем создать тестовую запись
            test_before = Student.objects.count()
            debug_info['db_count_before'] = test_before
            debug_info['db_table'] = Student._meta.db_table
        except Exception as e:
            return JsonResponse({
                'error': f'Ошибка подключения к БД: {str(e)}',
                'debug': debug_info
            }, status=500)
        
        students_processed = 0
        students_created = 0
        students_updated = 0
        errors = []
        saved_ids = []
        
        # Обрабатываем каждую строку в транзакции
        with transaction.atomic():
            for row_num, row in enumerate(reader, start=2):
                try:
                    # Проверяем наличие всех необходимых колонок
                    required_fields = ['ID', 'Согласие', 'Приоритет', 'Балл Физика/ИКТ', 
                                      'Балл Русский язык', 'Балл Математика', 
                                      'Балл за индивидуальные достижения', 'Сумма баллов']
                    
                    for field in required_fields:
                        if field not in row:
                            raise KeyError(f"Отсутствует колонка '{field}'. Доступные колонки: {list(row.keys())}")
                    
                    # Извлекаем данные из строки CSV
                    student_id = int(row['ID'].strip())
                    
                    # Преобразуем согласие (Да/Нет) в boolean
                    agreement_text = row['Согласие'].strip().upper()
                    agreement = agreement_text == 'ДА'
                    
                    # Баллы - обрабатываем случай, если поле пустое
                    ball_pro = int(float(row['Балл Физика/ИКТ'].strip())) if row['Балл Физика/ИКТ'].strip() else 0
                    ball_rus = int(float(row['Балл Русский язык'].strip())) if row['Балл Русский язык'].strip() else 0
                    ball_mat = int(float(row['Балл Математика'].strip())) if row['Балл Математика'].strip() else 0
                    ball_ind = int(float(row['Балл за индивидуальные достижения'].strip())) if row['Балл за индивидуальные достижения'].strip() else 0
                    ball_sum = int(float(row['Сумма баллов'].strip())) if row['Сумма баллов'].strip() else 0
                    
                    # Проверяем, существует ли студент
                    student, created = Student.objects.update_or_create(
                        student_id=student_id,
                        defaults={
                            'ball_pro': ball_pro,
                            'ball_rus': ball_rus,
                            'ball_mat': ball_mat,
                            'ball_ind': ball_ind,
                            'ball_sum': ball_sum,
                            'date': file_date,
                        }
                    )
                    
                    # Обновляем поля в зависимости от направления
                    if priority_info['priority_field'] == 'priority1':
                        student.priority1 = priority_info['priority_value']
                        student.agreement1 = agreement
                    elif priority_info['priority_field'] == 'priority2':
                        student.priority2 = priority_info['priority_value']
                        student.agreement2 = agreement
                    elif priority_info['priority_field'] == 'priority3':
                        student.priority3 = priority_info['priority_value']
                        student.agreement3 = agreement
                    elif priority_info['priority_field'] == 'priority4':
                        student.priority4 = priority_info['priority_value']
                        student.agreement4 = agreement
                    
                    # Сохраняем все изменения
                    student.save()
                    
                    saved_ids.append(student_id)
                    students_processed += 1
                    if created:
                        students_created += 1
                    else:
                        students_updated += 1
                        
                except KeyError as e:
                    errors.append(f"Строка {row_num}: {str(e)}")
                except ValueError as e:
                    errors.append(f"Строка {row_num}: ошибка преобразования данных - {str(e)}")
                except Exception as e:
                    errors.append(f"Строка {row_num}: {str(e)}")
        
        # Проверяем, что записи действительно сохранились
        count_after = Student.objects.count()
        debug_info['db_count_after'] = count_after
        debug_info['saved_ids_sample'] = saved_ids[:5] if saved_ids else []
        
        # Проверяем последнюю запись
        if saved_ids:
            try:
                last_student = Student.objects.filter(student_id=saved_ids[-1]).first()
                if last_student:
                    debug_info['last_saved'] = {
                        'id': last_student.student_id,
                        'sum': last_student.ball_sum,
                        'priority1': last_student.priority1,
                        'priority2': last_student.priority2,
                        'priority3': last_student.priority3,
                        'priority4': last_student.priority4,
                    }
            except Exception as e:
                debug_info['last_saved_error'] = str(e)
        
        # Формируем ответ
        response_data = {
            'success': True,
            'message': f'Файл {filename} обработан',
            'statistics': {
                'processed': students_processed,
                'created': students_created,
                'updated': students_updated,
                'errors': len(errors)
            },
            'direction': direction,
            'date': file_date.strftime('%d.%m.%Y'),
            'debug': debug_info
        }
        
        if errors:
            response_data['errors'] = errors[:20]
            response_data['message'] = f'Файл обработан с {len(errors)} ошибками'
        
        # Логируем успех
        logger.info(f"Загружено {students_processed} записей в таблицу {Student._meta.db_table}")
        last_date = Student.objects.aggregate(Max('date'))['date__max']
        if last_date:
            update_passing_scores(last_date)
        return JsonResponse(response_data)
        
    except Exception as e:
        # Получаем полную информацию об ошибке
        error_traceback = traceback.format_exc()
        logger.error(f"Ошибка при обработке файла: {str(e)}\n{error_traceback}")
        
        return JsonResponse({
            'error': f'Ошибка при обработке файла: {str(e)}',
            'traceback': error_traceback,
            'debug': debug_info
        }, status=500)


@csrf_exempt
def clear_database(request):
    """
    Полная очистка базы данных от всех записей
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не поддерживается'}, status=405)
    
    try:
        # Получаем количество записей до удаления
        count_before = Student.objects.count()
        
        # Удаляем все записи
        Student.objects.all().delete()
        DynBal.objects.all().delete()
        # Проверяем, что записи действительно удалены
        count_after = Student.objects.count()

        
        
        return JsonResponse({
            'success': True,
            'message': f'✅ База данных успешно очищена. Удалено записей: {count_before}',
            'deleted_count': count_before,
            'current_count': count_after
        })
        
    except Exception as e:
        logger.error(f"Ошибка при очистке базы данных: {str(e)}")
        return JsonResponse({'error': f'Ошибка при очистке базы данных: {str(e)}'}, status=500)


def total_students(request):
    """
    API для получения общего количества студентов в БД
    """
    try:
        total = Student.objects.count()
        return JsonResponse({'total': total})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

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
                'priority': student_data['priority_level'],
                'student_id': student.student_id
            })
    
    # Сортируем зачисленных по баллам (для каждого направления)
    for direction in enrolled_by_direction:
        enrolled_by_direction[direction].sort(key=lambda x: x['ball_sum'], reverse=True)
    
    return enrolled_by_direction


def index_view(request):
    return render(request, "index.html")

def pm_students_view(request):
    students = Student.objects.all().exclude(priority1=0)
    context = {"students": students}
    return render(request, "pm_students.html", context=context)

def ivt_students_view(request):
    students = Student.objects.all().exclude(priority2=0)
    context = {"students": students}
    return render(request, "ivt_students.html", context=context)

def itss_students_view(request):
    students = Student.objects.all().exclude(priority3=0)
    context = {"students": students}
    return render(request, "itss_students.html", context=context)

def ib_students_view(request):
    students = Student.objects.all().exclude(priority4=0)
    context = {"students": students}
    return render(request, "ib_students.html", context=context)

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
    for direction, students_list in enrolled_by_direction.items():
        for student_data in students_list:
            student = student_data['student']
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

        # Определяем максимальную дату в БД
    max_date = Student.objects.aggregate(Max('date'))['date__max']
    if max_date:
        end_date = max_date
    else:
        end_date = date.today()

    start_date = end_date - timedelta(days=3)

    # Формируем даты для графиков (4 дня: start_date, start_date+1, start_date+2, end_date)
    chart_dates = [
        (start_date + timedelta(days=i)).strftime('%d.%m')
        for i in range(4)
    ]

    # Динамика проходного балла за последние 4 дня (используем те же даты)
    dynamics_data = {}
    places = {1: 40, 2: 50, 3: 30, 4: 20}

    for dir_code in DIRECTIONS.keys():
        dir_dynamics = []
        for i in range(4):
            current_date = start_date + timedelta(days=i)
            enrolled = get_enrolled_for_date(current_date)
            students_on_dir = enrolled.get(dir_code, [])
            if len(students_on_dir) >= places[dir_code]:
                passing_score = students_on_dir[places[dir_code] - 1]['ball_sum']
            elif students_on_dir:
                passing_score = students_on_dir[-1]['ball_sum']
            else:
                passing_score = 0
            dir_dynamics.append(passing_score)
        dynamics_data[dir_code] = dir_dynamics
    
    # 5. Проходные баллы на сегодня с учётом реального зачисления
    today_passing = {}
    for dir_code in DIRECTIONS.keys():
        # Берём зачисленных студентов на это направление
        enrolled_students = enrolled_by_direction.get(dir_code, [])
        enrolled_students_sorted = sorted(enrolled_students, key=lambda x: x['ball_sum'], reverse=True)
        
        places = {1: 40, 2: 50, 3: 30, 4: 20}
        total_places = places.get(dir_code, 0)
        
        # Проверяем, хватает ли абитуриентов
        if len(enrolled_students_sorted) >= total_places:
            # Есть конкурс - показываем проходной балл (балл последнего зачисленного)
            today_passing[dir_code] = enrolled_students_sorted[total_places - 1]['ball_sum']
        else:
            # Недобор
            today_passing[dir_code] = "НЕДОБОР"
    
    # 6. Формируем списки зачисленных абитуриентов по каждому направлению
    enrolled_lists = {}
    for dir_code in DIRECTIONS.keys():
        # Получаем зачисленных студентов для этого направления
        enrolled_students = enrolled_by_direction.get(dir_code, [])
        
        # Формируем список словарей с ID и баллами (уже отсортировано)
        enrolled_lists[dir_code] = [
            {
                'id': student_data['student'].student_id,
                'ball_sum': student_data['ball_sum'],
                'priority': student_data['priority']
            }
            for student_data in enrolled_students
        ]
    
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
        
        # Списки зачисленных абитуриентов
        'enrolled_pm': enrolled_lists.get(1, []),
        'enrolled_ivt': enrolled_lists.get(2, []),
        'enrolled_itss': enrolled_lists.get(3, []),
        'enrolled_ib': enrolled_lists.get(4, []),
        
        # Количество зачисленных (для заголовков)
        'enrolled_pm_count': len(enrolled_lists.get(1, [])),
        'enrolled_ivt_count': len(enrolled_lists.get(2, [])),
        'enrolled_itss_count': len(enrolled_lists.get(3, [])),
        'enrolled_ib_count': len(enrolled_lists.get(4, [])),

        'chart_dates': json.dumps(chart_dates),
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