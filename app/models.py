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
    ID = models.IntegerField(primary_key=True)
    agreement1 = models.BooleanField()
    agreement2 = models.BooleanField()
    agreement3 = models.BooleanField()
    agreement4 = models.BooleanField()
    ball_pro = models.IntegerField()
    ball_rus = models.IntegerField()
    ball_mat = models.IntegerField()
    ball_ind = models.IntegerField()
    ball_sum = models.IntegerField()
    priority1 = models.IntegerField()
    priority2 = models.IntegerField()
    priority3 = models.IntegerField()
    priority4 = models.IntegerField()
    date = models.DateField()