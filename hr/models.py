from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
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



# JOB POSITION & CAPACITY MODEL


class JobPosition(models.Model):
    title = models.CharField(max_length=100)
    department = models.CharField(max_length=100)

    # Headcount management limits
    min_employees = models.PositiveIntegerField(
        default=1, help_text="Minimum planned headcount"
    )
    max_employees = models.PositiveIntegerField(
        default=10, help_text="Maximum approved headcount"
    )

    # Self-referencing foreign key for hierarchy
    reports_to = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sub_positions",
    )

    is_managerial = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["department", "title"]
        constraints = [
            models.UniqueConstraint(
                fields=["department", "title"],
                name="unique_job_position_per_department",
            )
        ]

    def __str__(self):
        return f"{self.title} - {self.department}"

    @property
    def current_headcount(self) -> int:
        """Dynamically computes headcount from the Employee table."""
        return Employee.objects.filter(
            department__iexact=self.department,
            job_title__iexact=self.title,
            status=Employee.EmployeeStatus.ACTIVE,
        ).count()

    @property
    def available_slots(self) -> int:
        """Returns open slots remaining before reaching max approved headcount."""
        return max(0, self.max_employees - self.current_headcount)

    def clean(self):
        """Model validation to ensure valid min/max and hierarchy."""
        if self.min_employees > self.max_employees:
            raise ValidationError("Minimum employees cannot exceed maximum employees.")
        if self.pk and self.reports_to_id == self.pk:
            raise ValidationError("A position cannot report to itself.")



#  TRAINING & DEVELOPMENT


class TrainingProgram(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    instructor = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    max_participants = models.PositiveIntegerField(default=20)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    @property
    def enrollment_count(self) -> int:
        return self.enrollments.count()


class TrainingEnrollment(models.Model):
    class EnrollmentStatus(models.TextChoices):
        ENROLLED = "enrolled", "Enrolled"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        DROPPED = "dropped", "Dropped"

    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="enrollments"
    )
    program = models.ForeignKey(
        TrainingProgram, on_delete=models.CASCADE, related_name="enrollments"
    )
    enrolled_at = models.DateField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=EnrollmentStatus.choices,
        default=EnrollmentStatus.ENROLLED,
    )

    class Meta:
        unique_together = ("employee", "program")

    def __str__(self):
        return f"{self.employee.full_name} -> {self.program.title}"


