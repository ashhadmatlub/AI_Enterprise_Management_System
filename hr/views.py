from django.shortcuts import render


def hr_home(request):
    return render(request, "hr/home.html")