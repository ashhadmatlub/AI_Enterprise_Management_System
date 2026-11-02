from datetime import timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from hr.models import Employee
from finance.models import (
    bills,
    licensing,
    raw_material,
    sales,
    contracts,
)


class Command(BaseCommand):
    help = "Seed sample financial data for testing weekly, monthly, and yearly dashboards."

    def handle(self, *args, **options):
        now = timezone.now()

        # 1. Active Employees (Payroll)
        employees_data = [
            ("Sarah Connor", "sarah@example.com", "Engineering", "Lead Architect", Decimal("6500.00")),
            ("John Doe", "john@example.com", "Sales", "Account Executive", Decimal("4200.00")),
            ("Jane Smith", "jane@example.com", "Operations", "Operations Manager", Decimal("5000.00")),
        ]
        for name, email, dept, title, salary in employees_data:
            Employee.objects.get_or_create(
                email=email,
                defaults={
                    "full_name": name,
                    "department": dept,
                    "job_title": title,
                    "salary": salary,
                    "join_date": (now - timedelta(days=120)).date(),
                    "status": Employee.EmployeeStatus.ACTIVE,
                },
            )

        # 2. Transactions distributed across time
        # Timestamps: 2 days ago (Weekly), 15 days ago (Monthly), 60 days ago (Yearly)
        transactions = [
            # Recent (this week)
            {"model": bills, "data": {"utility": "E", "bill_amount": Decimal("350.000")}, "days_ago": 2},
            {"model": bills, "data": {"utility": "I", "bill_amount": Decimal("120.000")}, "days_ago": 4},
            {"model": licensing, "data": {"company": "M", "bill_amount": Decimal("450.000")}, "days_ago": 3},
            {"model": raw_material, "data": {"material": "S", "bill_amount": Decimal("1200.000")}, "days_ago": 2},
            {"model": sales, "data": {"product_name": "Enterprise Suite v2", "product_id": "PRD-001", "amount": Decimal("4800.000")}, "days_ago": 1},
            {"model": sales, "data": {"product_name": "Cloud Connector", "product_id": "PRD-002", "amount": Decimal("2400.000")}, "days_ago": 3},
            {"model": contracts, "data": {"client_name": "Apex Corp", "client_id": "CLI-101", "description": "Annual Platform License", "amount": Decimal("15000.000")}, "days_ago": 2},

            # Earlier this month (between 8 and 28 days ago)
            {"model": bills, "data": {"utility": "G", "bill_amount": Decimal("220.000")}, "days_ago": 12},
            {"model": bills, "data": {"utility": "M", "bill_amount": Decimal("500.000")}, "days_ago": 18},
            {"model": licensing, "data": {"company": "A", "bill_amount": Decimal("800.000")}, "days_ago": 14},
            {"model": licensing, "data": {"company": "C", "bill_amount": Decimal("250.000")}, "days_ago": 20},
            {"model": raw_material, "data": {"material": "W", "bill_amount": Decimal("900.000")}, "days_ago": 16},
            {"model": sales, "data": {"product_name": "Security Module", "product_id": "PRD-003", "amount": Decimal("3100.000")}, "days_ago": 11},
            {"model": contracts, "data": {"client_name": "Blue Sky Ltd", "client_id": "CLI-102", "description": "Custom Implementation", "amount": Decimal("12500.000")}, "days_ago": 19},

            # Earlier this year (between 35 and 180 days ago)
            {"model": bills, "data": {"utility": "E", "bill_amount": Decimal("400.000")}, "days_ago": 45},
            {"model": licensing, "data": {"company": "T", "bill_amount": Decimal("1500.000")}, "days_ago": 60},
            {"model": raw_material, "data": {"material": "R", "bill_amount": Decimal("1400.000")}, "days_ago": 70},
            {"model": sales, "data": {"product_name": "Hardware Gateway", "product_id": "PRD-004", "amount": Decimal("6200.000")}, "days_ago": 50},
            {"model": contracts, "data": {"client_name": "Omega Global", "client_id": "CLI-103", "description": "Multi-year Support Contract", "amount": Decimal("28000.000")}, "days_ago": 90},
        ]

        count = 0
        for item in transactions:
            model = item["model"]
            data = item["data"]
            days_ago = item["days_ago"]
            obj = model.objects.create(**data)
            # Update created_at directly via update() to bypass auto_now_add
            model.objects.filter(id=obj.id).update(created_at=now - timedelta(days=days_ago))
            count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully seeded {count} financial transactions and 3 active employees!"
            )
        )
