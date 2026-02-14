from django.db import models

# Create your models here.

class Student(models.Model):
    """
    ID : айди человека
    agreement1 : соглашения на поступление
    agreement2
    agreement3
    agreement4
    ball_pro : баллы за проф, рус, математику, индивидульный проект, сумма балов
    ball_rus 
    ball_mat 
    ball_ind 
    ball_sum 
    priority1 : приоритеты на поступления (соответсвуют с соглашениями)
    priority2
    priority3 
    priority4 
    """
    student_id = models.IntegerField(primary_key=True)
    agreement1 = models.BooleanField(default=False)
    agreement2 = models.BooleanField(default=False)
    agreement3 = models.BooleanField(default=False)
    agreement4 = models.BooleanField(default=False)
    ball_pro = models.IntegerField(default=0)
    ball_rus = models.IntegerField(default=0)
    ball_mat = models.IntegerField(default=0)
    ball_ind = models.IntegerField(default=0)
    ball_sum = models.IntegerField(default=0)
    priority1 = models.IntegerField(default=0)
    priority2 = models.IntegerField(default=0)
    priority3 = models.IntegerField(default=0)
    priority4 = models.IntegerField(default=0)
    date = models.DateField()