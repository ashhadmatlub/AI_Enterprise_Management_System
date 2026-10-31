from django.db import models


class Employee(models.Model):

    class EmployeeStatus(models.TextChoices):
        ACTIVE = "active", "Active"
        ON_LEAVE = "on_leave", "On Leave"
        INACTIVE = "inactive", "Inactive"

    full_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    department = models.CharField(max_length=100)
    job_title = models.CharField(max_length=100)
    salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    join_date = models.DateField()

    status = models.CharField(
        max_length=20, choices=EmployeeStatus.choices, default=EmployeeStatus.ACTIVE
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name

    class Meta:
        ordering = ["-created_at"]


class EmployeeRequest(models.Model):

    class RequestType(models.TextChoices):
        LEAVE = "leave", "Leave"
        EQUIPMENT = "equipment", "Equipment"
        REIMBURSEMENT = "reimbursement", "Reimbursement"
        OTHER = "other", "Other"

    class RequestStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="requests"
    )

    request_type = models.CharField(max_length=30, choices=RequestType.choices)

    description = models.TextField()

    status = models.CharField(
        max_length=20, choices=RequestStatus.choices, default=RequestStatus.PENDING
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.full_name} - {self.request_type}"


class EmployeeTask(models.Model):

    class TaskStatus(models.TextChoices):
        TODO = "todo", "To Do"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"

    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="tasks"
    )

    task_title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    status = models.CharField(
        max_length=20, choices=TaskStatus.choices, default=TaskStatus.TODO
    )

    due_date = models.DateField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.task_title
