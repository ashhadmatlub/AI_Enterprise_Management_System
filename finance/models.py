from datetime import timedelta
from decimal import Decimal
from django.db import models
from django.db.models import Sum
from django.utils import timezone
from hr.models import Employee


class bills(models.Model):
    utilities = {
        "E": "Electricity",
        "G": "GAS",
        "M": "Maintenance",
        "I": "Internet",
    }
    utility = models.CharField(max_length=1, choices=utilities)
    bill_amount = models.DecimalField(max_digits=12, decimal_places=3)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_utility_display()} - {self.bill_amount}"


class licensing(models.Model):
    companies = {
        "T": "TCS",
        "A": "Anthropic",
        "M": "Microsoft",
        "C": "Cloudfare",
    }
    company = models.CharField(max_length=1, choices=companies)
    bill_amount = models.DecimalField(max_digits=10, decimal_places=3)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_company_display()} - {self.bill_amount}"


class raw_material(models.Model):
    materials = {
        "S": "Steel",
        "W": "Wood",
        "R": "Resin",
        "P": "Plastic",
    }
    material = models.CharField(max_length=1, choices=materials)
    bill_amount = models.DecimalField(max_digits=10, decimal_places=3)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_material_display()} - {self.bill_amount}"


class sales(models.Model):
    product_name = models.CharField(max_length=100)
    product_id = models.CharField(max_length=12)
    amount = models.DecimalField(max_digits=12, decimal_places=3)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product_name} - {self.amount}"


class contracts(models.Model):
    client_name = models.CharField(max_length=100)
    client_id = models.CharField(max_length=12)
    description = models.CharField(max_length=600)
    amount = models.DecimalField(max_digits=12, decimal_places=3)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.client_name} - {self.amount}"


class Expenses(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def _apply_date_filter(queryset, start_date=None, end_date=None):
        if start_date and end_date:
            return queryset.filter(created_at__range=(start_date, end_date))
        if start_date:
            return queryset.filter(created_at__gte=start_date)
        if end_date:
            return queryset.filter(created_at__lte=end_date)
        return queryset

    @classmethod
    def get_payroll_total(cls, period='monthly', days=None):
        active_payroll = Employee.objects.filter(status='active').aggregate(
            total=Sum('salary')
        )['total'] or Decimal('0.00')

        if period == 'weekly':
            return (active_payroll * Decimal('12')) / Decimal('52')
        elif period == 'monthly':
            return active_payroll
        elif period == 'yearly':
            return active_payroll * Decimal('12')
        elif days is not None:
            return (active_payroll * Decimal(days)) / Decimal('30')
        return active_payroll

    @classmethod
    def get_bills_total(cls, start_date=None, end_date=None):
        qs = cls._apply_date_filter(bills.objects.all(), start_date, end_date)
        return qs.aggregate(total=Sum('bill_amount'))['total'] or Decimal('0.00')

    @classmethod
    def get_licensing_total(cls, start_date=None, end_date=None):
        qs = cls._apply_date_filter(licensing.objects.all(), start_date, end_date)
        return qs.aggregate(total=Sum('bill_amount'))['total'] or Decimal('0.00')

    @classmethod
    def get_raw_material_total(cls, start_date=None, end_date=None):
        qs = cls._apply_date_filter(raw_material.objects.all(), start_date, end_date)
        return qs.aggregate(total=Sum('bill_amount'))['total'] or Decimal('0.00')

    @classmethod
    def calculate(cls, start_date=None, end_date=None, period='monthly'):
        days = None
        if start_date and end_date:
            days = (end_date - start_date).days or 1

        b = cls.get_bills_total(start_date, end_date)
        l = cls.get_licensing_total(start_date, end_date)
        rm = cls.get_raw_material_total(start_date, end_date)
        payroll = cls.get_payroll_total(period=period, days=days if (start_date and end_date) else None)

        total = b + l + rm + payroll
        return {
            "bills": b,
            "licensing": l,
            "raw_material": rm,
            "payroll": payroll,
            "total": total,
        }

    # Backward compatibility properties
    @property
    def employee_salaries(self):
        return self.get_payroll_total(period='monthly')

    @property
    def bills(self):
        return self.get_bills_total()

    @property
    def licensing_costs(self):
        return self.get_licensing_total()

    @property
    def raw_material(self):
        return self.get_raw_material_total()

    @property
    def total_expense(self):
        return self.calculate(period='monthly')["total"]


class Revenue(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def _apply_date_filter(queryset, start_date=None, end_date=None):
        if start_date and end_date:
            return queryset.filter(created_at__range=(start_date, end_date))
        if start_date:
            return queryset.filter(created_at__gte=start_date)
        if end_date:
            return queryset.filter(created_at__lte=end_date)
        return queryset

    @classmethod
    def get_sales_total(cls, start_date=None, end_date=None):
        qs = cls._apply_date_filter(sales.objects.all(), start_date, end_date)
        return qs.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    @classmethod
    def get_contracts_total(cls, start_date=None, end_date=None):
        qs = cls._apply_date_filter(contracts.objects.all(), start_date, end_date)
        return qs.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    @classmethod
    def calculate(cls, start_date=None, end_date=None):
        s = cls.get_sales_total(start_date, end_date)
        c = cls.get_contracts_total(start_date, end_date)
        return {
            "sales": s,
            "contracts": c,
            "total": s + c,
        }

    # Backward compatibility property
    @property
    def revenue(self):
        return self.calculate()["total"]


class Profit(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def get_date_range(cls, period='monthly'):
        now = timezone.now()
        if period == 'weekly':
            return now - timedelta(days=7), now
        elif period == 'monthly':
            return now - timedelta(days=30), now
        elif period == 'yearly':
            return now - timedelta(days=365), now
        elif period == 'all':
            return None, None
        return None, None

    @classmethod
    def calculate(cls, start_date=None, end_date=None, period='monthly'):
        rev_data = Revenue.calculate(start_date=start_date, end_date=end_date)
        exp_data = Expenses.calculate(start_date=start_date, end_date=end_date, period=period)

        total_rev = rev_data["total"]
        total_exp = exp_data["total"]
        net = total_rev - total_exp

        return {
            "period": period,
            "start_date": start_date,
            "end_date": end_date,
            "revenue": rev_data,
            "expenses": exp_data,
            "total_revenue": total_rev,
            "total_expense": total_exp,
            "net_profit": net,
        }

    @classmethod
    def calculate_for_period(cls, period='monthly'):
        start_date, end_date = cls.get_date_range(period)
        return cls.calculate(start_date=start_date, end_date=end_date, period=period)

    # Backward compatibility properties
    @property
    def total_revenue(self):
        return Revenue().revenue

    @property
    def total_expense(self):
        return Expenses().total_expense

    @property
    def net_profit(self):
        return self.total_revenue - self.total_expense
