from django.shortcuts import render
from django.http.request import HttpRequest
from .models import Student

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

