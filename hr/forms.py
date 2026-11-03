import re
from django import forms
from .models import (
    Employee,
    EmployeeRequest,
    EmployeeTask,
    JobPosition,
    TrainingEnrollment,
    TrainingProgram,
)

# Standard departments commonly found in enterprises
STANDARD_DEPARTMENTS = [
    "Human Resources",
    "Engineering",
    "Finance",
    "Marketing",
    "Sales",
    "Operations",
    "Information Technology",
    "Legal",
    "Customer Support",
    "Product Management",
    "Administration",
]


def validate_text_field(value: str, field_name: str) -> str:
    """
    Real-world validation for corporate job titles and departments:
    1. Must be at least 2 characters long.
    2. Cannot be pure numbers or special symbols (e.g., '1234' or '@@@').
    3. Allows letters, spaces, hyphens, slashes, and ampersands (e.g. 'R&D', 'VP / Director', 'UI/UX').
    4. Automatically strips trailing/leading whitespaces and collapses multi-spaces.
    """
    if not value:
        return value

    cleaned = " ".join(value.strip().split())

    if len(cleaned) < 2:
        raise forms.ValidationError(f"{field_name} must be at least 2 characters long.")

    # Must contain at least one alphabet character (cannot be just digits or symbols)
    if not any(char.isalpha() for char in cleaned):
        raise forms.ValidationError(f"{field_name} must contain alphabetic letters.")

    # Only realistic characters: alphabets, digits, spaces, and standard corporate separators (-, /, &, ., ')
    pattern = r"^[A-Za-z0-9\s\-/\&\.\',()]+$"
    if not re.match(pattern, cleaned):
        raise forms.ValidationError(
            f"{field_name} contains invalid characters. Only letters, numbers, spaces, and -, /, &, ., ' are allowed."
        )

    return cleaned


# ==============================================================================
# 1. EMPLOYEE FORM
# ==============================================================================

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            "full_name",
            "email",
            "department",
            "job_title",
            "salary",
            "join_date",
            "status",
        ]
        widgets = {
            "full_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g. John Doe"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "e.g. john.doe@company.com"}
            ),
            "department": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. Engineering, Human Resources, Finance",
                    "list": "department-list",
                }
            ),
            "job_title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. Senior Software Engineer",
                }
            ),
            "salary": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "placeholder": "0.00"}
            ),
            "join_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "status": forms.Select(attrs={"class": "form-select"}),
        }

    def clean_full_name(self):
        name = self.cleaned_data.get("full_name", "")
        return validate_text_field(name, "Full Name")

    def clean_department(self):
        dept = self.cleaned_data.get("department", "")
        return validate_text_field(dept, "Department")

    def clean_job_title(self):
        title = self.cleaned_data.get("job_title", "")
        return validate_text_field(title, "Job Title")

    def clean_salary(self):
        salary = self.cleaned_data.get("salary")
        if salary is not None and salary < 0:
            raise forms.ValidationError("Salary cannot be negative.")
        return salary


# ==============================================================================
# 2. EMPLOYEE REQUEST FORM
# ==============================================================================

class EmployeeRequestForm(forms.ModelForm):
    class Meta:
        model = EmployeeRequest
        fields = ["employee", "request_type", "description"]
        widgets = {
            "employee": forms.Select(attrs={"class": "form-select"}),
            "request_type": forms.Select(attrs={"class": "form-select"}),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Provide details of your request...",
                }
            ),
        }


# ==============================================================================
# 3. EMPLOYEE TASK FORM
# ==============================================================================

class EmployeeTaskForm(forms.ModelForm):
    class Meta:
        model = EmployeeTask
        fields = ["employee", "task_title", "description", "due_date", "status"]
        widgets = {
            "employee": forms.Select(attrs={"class": "form-select"}),
            "task_title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g. Prepare monthly audit"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Task instructions and expectations...",
                }
            ),
            "due_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "status": forms.Select(attrs={"class": "form-select"}),
        }

    def clean_task_title(self):
        title = self.cleaned_data.get("task_title", "")
        return validate_text_field(title, "Task Title")


# ==============================================================================
# 4. JOB POSITION FORM (WITH HEADCOUNT LIMITS & VALIDATIONS)
# ==============================================================================

class JobPositionForm(forms.ModelForm):
    class Meta:
        model = JobPosition
        fields = [
            "title",
            "department",
            "min_employees",
            "max_employees",
            "reports_to",
            "is_managerial",
            "is_active",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g. Technical Lead"}
            ),
            "department": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. Engineering",
                    "list": "department-list",
                }
            ),
            "min_employees": forms.NumberInput(
                attrs={"class": "form-control", "min": 0}
            ),
            "max_employees": forms.NumberInput(
                attrs={"class": "form-control", "min": 1}
            ),
            "reports_to": forms.Select(attrs={"class": "form-select"}),
            "is_managerial": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "is_active": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        }

    def clean_title(self):
        title = self.cleaned_data.get("title", "")
        return validate_text_field(title, "Job Title")

    def clean_department(self):
        dept = self.cleaned_data.get("department", "")
        return validate_text_field(dept, "Department")

    def clean(self):
        cleaned_data = super().clean()
        min_emp = cleaned_data.get("min_employees")
        max_emp = cleaned_data.get("max_employees")
        title = cleaned_data.get("title")
        dept = cleaned_data.get("department")

        if min_emp is not None and max_emp is not None and min_emp > max_emp:
            raise forms.ValidationError(
                {"max_employees": "Maximum headcount cannot be less than minimum planned headcount."}
            )

        # Check duplicate position within the same department (case-insensitive)
        if title and dept:
            existing = JobPosition.objects.filter(
                title__iexact=title,
                department__iexact=dept,
            )
            if self.instance and self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError(
                    {"title": f"A job position '{title}' already exists in the '{dept}' department."}
                )

        return cleaned_data


# ==============================================================================
# 5. TRAINING FORMS
# ==============================================================================

class TrainingProgramForm(forms.ModelForm):
    class Meta:
        model = TrainingProgram
        fields = [
            "title",
            "description",
            "instructor",
            "start_date",
            "end_date",
            "max_participants",
            "is_active",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g. Agile Leadership"}
            ),
            "description": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "placeholder": "Course syllabus / objectives..."}
            ),
            "instructor": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g. Dr. Alex Mercer"}
            ),
            "start_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "end_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "max_participants": forms.NumberInput(
                attrs={"class": "form-control", "min": 1}
            ),
            "is_active": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        }

    def clean_title(self):
        title = self.cleaned_data.get("title", "")
        return validate_text_field(title, "Program Title")

    def clean_instructor(self):
        inst = self.cleaned_data.get("instructor", "")
        return validate_text_field(inst, "Instructor Name")

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start_date")
        end = cleaned_data.get("end_date")

        if start and end and end < start:
            raise forms.ValidationError({"end_date": "End date cannot be earlier than start date."})
        return cleaned_data


class TrainingEnrollmentForm(forms.ModelForm):
    class Meta:
        model = TrainingEnrollment
        fields = ["employee", "program", "status"]
        widgets = {
            "employee": forms.Select(attrs={"class": "form-select"}),
            "program": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }
