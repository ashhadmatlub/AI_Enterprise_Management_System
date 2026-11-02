from django.shortcuts import render
from hr.models import Employee, EmployeeRequest
from recruitment.models import Candidate
from finance.models import sales, contracts


def dashboard(request):
    context = {
        "employee_count": Employee.objects.count(),
        "pending_requests": EmployeeRequest.objects.filter(
            status="pending"
        ).count(),
        "candidate_count": Candidate.objects.count(),
        "transaction_count": sales.objects.count() + contracts.objects.count(),
    }

    return render(request, "core/dashboard.html", context)
