from datetime import date
from typing import Optional
from django.db.models import QuerySet
from django.utils import timezone

from .models import (
    Employee,
    EmployeeRequest,
    EmployeeTask,
    JobPosition,
    TrainingEnrollment,
    TrainingProgram,
)



# EMPLOYEE SERVICES 

def get_employees(
    status: Optional[str] = None,
    department: Optional[str] = None,
    search_query: Optional[str] = None,
) -> QuerySet[Employee]:
    """
    Retrieve employees with optional filtering by status, department, or keyword search.
    """
    queryset = Employee.objects.all()

    if status:
        queryset = queryset.filter(status=status)

    if department:
        queryset = queryset.filter(department__icontains=department)

    if search_query:
        queryset = queryset.filter(
            full_name__icontains=search_query
        ) | queryset.filter(
            email__icontains=search_query
        ) | queryset.filter(
            job_title__icontains=search_query
        )

    return queryset


def get_employee_by_id(employee_id: int) -> Optional[Employee]:
    """Retrieve a single employee by their ID."""
    try:
        return Employee.objects.get(pk=employee_id)
    except Employee.DoesNotExist:
        return None


def create_employee(data: dict) -> Employee:
    """Create and return a new employee."""
    return Employee.objects.create(**data)


def update_employee(employee: Employee, data: dict) -> Employee:
    """Update fields on an existing employee."""
    for field, value in data.items():
        setattr(employee, field, value)
    employee.save()
    return employee


def delete_employee(employee: Employee) -> bool:
    """Delete an employee from the database."""
    employee.delete()
    return True



# EMPLOYEE REQUEST SERVICES


def get_requests(
    status: Optional[str] = None,
    request_type: Optional[str] = None,
) -> QuerySet[EmployeeRequest]:
    """
    Retrieve employee requests, ordered newest first.
    Optimized with select_related for related employee data.
    """
    queryset = EmployeeRequest.objects.select_related("employee").all().order_by("-created_at")

    if status:
        queryset = queryset.filter(status=status)

    if request_type:
        queryset = queryset.filter(request_type=request_type)

    return queryset


def get_request_by_id(request_id: int) -> Optional[EmployeeRequest]:
    """Retrieve a single request by ID."""
    try:
        return EmployeeRequest.objects.select_related("employee").get(pk=request_id)
    except EmployeeRequest.DoesNotExist:
        return None


def update_request_status(request_obj: EmployeeRequest, new_status: str) -> EmployeeRequest:
    """Update the status of an employee request (pending, approved, rejected)."""
    request_obj.status = new_status
    request_obj.save()
    return request_obj



# EMPLOYEE TASK SERVICES


def get_tasks(
    status: Optional[str] = None,
    employee_id: Optional[int] = None,
) -> QuerySet[EmployeeTask]:
    """
    Retrieve employee tasks with optional filtering by status or employee.
    """
    queryset = EmployeeTask.objects.select_related("employee").all().order_by("-id")

    if status:
        queryset = queryset.filter(status=status)

    if employee_id:
        queryset = queryset.filter(employee_id=employee_id)

    return queryset


def get_task_by_id(task_id: int) -> Optional[EmployeeTask]:
    """Retrieve a single task by ID."""
    try:
        return EmployeeTask.objects.select_related("employee").get(pk=task_id)
    except EmployeeTask.DoesNotExist:
        return None


def create_task(data: dict) -> EmployeeTask:
    """Create and return a new task."""
    return EmployeeTask.objects.create(**data)


def update_task_status(task_obj: EmployeeTask, new_status: str) -> EmployeeTask:
    """
    Update status of a task (todo, in_progress, completed).
    Automatically records completed_at timestamp when marked completed.
    """
    task_obj.status = new_status
    if new_status == EmployeeTask.TaskStatus.COMPLETED and not task_obj.completed_at:
        task_obj.completed_at = timezone.now()
    elif new_status != EmployeeTask.TaskStatus.COMPLETED:
        task_obj.completed_at = None
    task_obj.save()
    return task_obj



#  JOB POSITION & TRAINING SERVICES


def get_job_positions(active_only: bool = False) -> QuerySet[JobPosition]:
    """Retrieve all job positions ordered by department and title."""
    queryset = JobPosition.objects.select_related("reports_to").all().order_by("department", "title")
    if active_only:
        queryset = queryset.filter(is_active=True)
    return queryset


def get_training_programs(active_only: bool = False) -> QuerySet[TrainingProgram]:
    """Retrieve training programs prefetching enrollments."""
    queryset = TrainingProgram.objects.prefetch_related("enrollments__employee").all().order_by("-start_date")
    if active_only:
        queryset = queryset.filter(is_active=True)
    return queryset