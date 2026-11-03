
# from django.shortcuts import render
# from .models import Employee, EmployeeRequest, EmployeeTask, JobPosition


# def home(request):
#     context = {
#         "total_employees": Employee.objects.count(),
#         "active_employees": Employee.objects.filter(status="active").count(),
#         "pending_requests": EmployeeRequest.objects.filter(
#             status="pending"
#         ).count(),
#         "total_tasks": EmployeeTask.objects.count(),
#         "total_positions": JobPosition.objects.filter(
#             is_active=True
#         ).count(),
#     }

#     return render(request, "hr/home.html", context)


# def position_list(request):
#     positions = JobPosition.objects.filter(is_active=True)

#     context = {
#         "positions": positions,
#     }

#     return render(request, "hr/positions.html", context)

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from . import services
from .forms import (
    EmployeeForm,
    EmployeeRequestForm,
    EmployeeTaskForm,
    JobPositionForm,
    TrainingEnrollmentForm,
    TrainingProgramForm,
)
from .models import Employee, EmployeeRequest, EmployeeTask, JobPosition, TrainingProgram



# HR DASHBOARD OVERVIEW


def home(request):
    """Main HR Overview dashboard with key metrics and quick navigation."""
    context = {
        "total_employees": services.get_employees().count(),
        "active_employees": services.get_employees(status=Employee.EmployeeStatus.ACTIVE).count(),
        "pending_requests": services.get_requests(status=EmployeeRequest.RequestStatus.PENDING).count(),
        "total_tasks": services.get_tasks().count(),
        "total_positions": services.get_job_positions(active_only=True).count(),
        "active_trainings": services.get_training_programs(active_only=True).count(),
    }
    return render(request, "hr/home.html", context)



# EMPLOYEE MANAGEMENT (CONTAINS ALL CRUD OPERATIONS FOR EMPLOYEE)


def employee_list(request):
    """Displays all employees with search and status filtering."""
    q = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()

    employees = services.get_employees(
        status=status or None,
        search_query=q or None,
    )
    context = {
        "employees": employees,
        "q": q, 
        "status": status,
        "status_choices": Employee.EmployeeStatus.choices,
    }
    return render(request, "hr/employee_list.html", context)


def employee_detail(request, pk):
    """Detailed profile of an employee with requests, tasks, and enrollments."""
    emp = get_object_or_404(Employee, pk=pk)
    context = {
        "employee": emp,
        "requests": emp.requests.all(),
        "tasks": emp.tasks.all(),
        "enrollments": emp.enrollments.select_related("program").all(),
    }
    return render(request, "hr/employee_detail.html", context)


def employee_create(request):
    """Add a new employee."""
    form = EmployeeForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        emp = form.save()
        messages.success(request, f"Employee '{emp.full_name}' was added successfully.")
        return redirect("hr:employee_detail", pk=emp.pk)
    return render(request, "hr/employee_form.html", {"form": form, "action": "Add"})


def employee_update(request, pk):
    """Edit existing employee details."""
    emp = get_object_or_404(Employee, pk=pk)
    form = EmployeeForm(request.POST or None, instance=emp)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"Employee '{emp.full_name}' updated successfully.")
        return redirect("hr:employee_detail", pk=emp.pk)
    return render(request, "hr/employee_form.html", {"form": form, "employee": emp, "action": "Edit"})


def employee_delete(request, pk):
    """Delete an employee with confirmation."""
    emp = get_object_or_404(Employee, pk=pk)
    if request.method == "POST":
        name = emp.full_name
        services.delete_employee(emp)
        messages.success(request, f"Employee '{name}' deleted successfully.")
        return redirect("hr:employee_list")
    return render(request, "hr/employee_confirm_delete.html", {"employee": emp})



#  EMPLOYEE REQUESTS


def request_list(request):
    """List employee requests with status filter."""
    status = request.GET.get("status", "").strip()
    requests_qs = services.get_requests(status=status or None)
    context = {
        "requests": requests_qs,
        "status_filter": status,
        "status_choices": EmployeeRequest.RequestStatus.choices,
    }
    return render(request, "hr/request_list.html", context)


def request_create(request):
    """Submit a request for an employee."""
    initial_data = {}
    emp_id = request.GET.get("employee_id")
    if emp_id:
        initial_data["employee"] = emp_id

    form = EmployeeRequestForm(request.POST or None, initial=initial_data)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Employee request submitted successfully.")
        return redirect("hr:request_list")
    return render(request, "hr/request_form.html", {"form": form})


def request_update_status(request, pk):
    """Update request status (Pending/Approved/Rejected)."""
    req_obj = get_object_or_404(EmployeeRequest, pk=pk)
    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in dict(EmployeeRequest.RequestStatus.choices):
            services.update_request_status(req_obj, new_status)
            messages.success(request, f"Request status changed to '{req_obj.get_status_display()}'.")
        else:
            messages.error(request, "Invalid status submitted.")
    return redirect("hr:request_list")


#  EMPLOYEE TASK TRACKING


def task_list(request):
    """Display employee tasks with status and employee filtering."""
    status = request.GET.get("status", "").strip()
    emp_id = request.GET.get("employee_id", "").strip()

    tasks_qs = services.get_tasks(
        status=status or None,
        employee_id=int(emp_id) if emp_id.isdigit() else None,
    )
    context = {
        "tasks": tasks_qs,
        "employees": services.get_employees(),
        "status_filter": status,
        "employee_filter": emp_id,
        "status_choices": EmployeeTask.TaskStatus.choices,
    }
    return render(request, "hr/task_list.html", context)


def task_create(request):
    """Assign a new task to an employee."""
    initial_data = {}
    emp_id = request.GET.get("employee_id")
    if emp_id:
        initial_data["employee"] = emp_id

    form = EmployeeTaskForm(request.POST or None, initial=initial_data)
    if request.method == "POST" and form.is_valid():
        task = form.save()
        messages.success(request, f"Task '{task.task_title}' assigned successfully.")
        return redirect("hr:task_list")
    return render(request, "hr/task_form.html", {"form": form})


def task_update_status(request, pk):
    """Update task status (To Do / In Progress / Completed)."""
    task = get_object_or_404(EmployeeTask, pk=pk)
    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in dict(EmployeeTask.TaskStatus.choices):
            services.update_task_status(task, new_status)
            messages.success(request, f"Task marked as '{task.get_status_display()}'.")
    referer = request.META.get("HTTP_REFERER")
    return redirect(referer or "hr:task_list")



# JOB POSITIONS & CAPACITY

def position_list(request):
    """View all job positions and active headcount."""
    positions = services.get_job_positions()
    return render(request, "hr/positions.html", {"positions": positions})


def position_create(request):
    """Create a new job position."""
    form = JobPositionForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        pos = form.save()
        messages.success(request, f"Job Position '{pos.title}' created.")
        return redirect("hr:positions")
    return render(request, "hr/position_form.html", {"form": form, "action": "Add"})


def position_update(request, pk):
    """Edit existing job position and headcount limits."""
    pos = get_object_or_404(JobPosition, pk=pk)
    form = JobPositionForm(request.POST or None, instance=pos)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"Job Position '{pos.title}' updated.")
        return redirect("hr:positions")
    return render(request, "hr/position_form.html", {"form": form, "position": pos, "action": "Edit"})


def position_delete(request, pk):
    """Delete a job position with confirmation."""
    pos = get_object_or_404(JobPosition, pk=pk)
    if request.method == "POST":
        title = pos.title
        pos.delete()
        messages.success(request, f"Position '{title}' deleted successfully.")
        return redirect("hr:positions")
    return render(request, "hr/position_confirm_delete.html", {"position": pos})



#  TRAINING & ENROLLMENT


def training_list(request):
    """Display training programs and enrolled participants."""
    programs = services.get_training_programs()
    return render(request, "hr/training_list.html", {"programs": programs})


def training_create(request):
    """Add a new training program."""
    form = TrainingProgramForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        program = form.save()
        messages.success(request, f"Training program '{program.title}' created.")
        return redirect("hr:training_list")
    return render(request, "hr/training_form.html", {"form": form})


def training_enroll(request):
    """Enroll an employee into a training program."""
    initial_data = {}
    program_id = request.GET.get("program_id")
    emp_id = request.GET.get("employee_id")
    if program_id:
        initial_data["program"] = program_id
    if emp_id:
        initial_data["employee"] = emp_id

    form = TrainingEnrollmentForm(request.POST or None, initial=initial_data)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Employee enrolled successfully.")
        return redirect("hr:training_list")
    return render(request, "hr/training_enroll.html", {"form": form})






