from django.shortcuts import render


def finance_home(request):
    return render(request, "finance/home.html")