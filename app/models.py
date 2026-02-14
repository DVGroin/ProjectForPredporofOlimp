from django.db import models

# Create your models here.

class Student(models.Model):
    ID = models.IntegerField()
    agreement = models.BooleanField()
    priority = models.IntegerField()
    ball_pro = models.IntegerField()
    ball_rus = models.IntegerField()
    ball_mat = models.IntegerField()
    ball_ind = models.IntegerField()
    ball_sum = models.IntegerField()
    napr = models.IntegerField()