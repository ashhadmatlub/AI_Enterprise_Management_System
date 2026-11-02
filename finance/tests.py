from datetime import timedelta
from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from hr.models import Employee
from finance.models import (
    bills,
    licensing,
    raw_material,
    sales,
    contracts,
    Expenses,
    Revenue,
    Profit,
)


class FinanceCalculationsTestCase(TestCase):
    def setUp(self):
        # Create an active employee
        self.employee = Employee.objects.create(
            full_name="Alice Smith",
            email="alice@example.com",
            department="Engineering",
            job_title="Software Engineer",
            salary=Decimal("5200.00"),
            join_date=timezone.now().date(),
            status=Employee.EmployeeStatus.ACTIVE,
        )

        # Create transactions
        self.bill = bills.objects.create(
            utility="E",
            bill_amount=Decimal("150.000"),
        )
        self.license = licensing.objects.create(
            company="M",
            bill_amount=Decimal("300.000"),
        )
        self.raw = raw_material.objects.create(
            material="S",
            bill_amount=Decimal("500.000"),
        )
        self.sale = sales.objects.create(
            product_name="Product A",
            product_id="PROD001",
            amount=Decimal("1200.000"),
        )
        self.contract = contracts.objects.create(
            client_name="Acme Corp",
            client_id="CLI001",
            description="Consulting contract",
            amount=Decimal("8000.000"),
        )

    def test_empty_calculations_return_zero_without_type_error(self):
        """Ensure calculations with no data don't fail or crash with Decimal/float errors."""
        bills.objects.all().delete()
        licensing.objects.all().delete()
        raw_material.objects.all().delete()
        sales.objects.all().delete()
        contracts.objects.all().delete()
        Employee.objects.all().delete()

        rev = Revenue.calculate()
        self.assertEqual(rev["total"], Decimal("0.00"))

        exp = Expenses.calculate(period="monthly")
        self.assertEqual(exp["total"], Decimal("0.00"))

        prof = Profit.calculate_for_period("monthly")
        self.assertEqual(prof["net_profit"], Decimal("0.00"))

    def test_backward_compatibility_properties(self):
        """Ensure model properties still work as expected."""
        revenue_obj = Revenue()
        self.assertEqual(revenue_obj.revenue, Decimal("9200.000"))

        expense_obj = Expenses()
        # bills(150) + licensing(300) + raw(500) + salary(5200) = 6150
        self.assertEqual(expense_obj.total_expense, Decimal("6150.000"))

        profit_obj = Profit()
        self.assertEqual(profit_obj.net_profit, Decimal("9200.000") - Decimal("6150.000"))

    def test_payroll_scaling(self):
        """Test payroll scaling across monthly, weekly, and yearly periods."""
        # Monthly payroll should equal 5200
        monthly_payroll = Expenses.get_payroll_total(period="monthly")
        self.assertEqual(monthly_payroll, Decimal("5200.00"))

        # Weekly payroll: 5200 * 12 / 52 = 1200
        weekly_payroll = Expenses.get_payroll_total(period="weekly")
        self.assertEqual(weekly_payroll, Decimal("1200.00"))

        # Yearly payroll: 5200 * 12 = 62400
        yearly_payroll = Expenses.get_payroll_total(period="yearly")
        self.assertEqual(yearly_payroll, Decimal("62400.00"))

    def test_periodic_profit_calculations(self):
        """Test Profit.calculate_for_period for weekly, monthly, and yearly."""
        weekly_summary = Profit.calculate_for_period("weekly")
        self.assertEqual(weekly_summary["period"], "weekly")
        self.assertEqual(weekly_summary["total_revenue"], Decimal("9200.000"))
        # Weekly expense: 150 + 300 + 500 + 1200 = 2150
        self.assertEqual(weekly_summary["total_expense"], Decimal("2150.000"))
        self.assertEqual(weekly_summary["net_profit"], Decimal("9200.000") - Decimal("2150.000"))

        yearly_summary = Profit.calculate_for_period("yearly")
        self.assertEqual(yearly_summary["period"], "yearly")
        self.assertEqual(yearly_summary["total_revenue"], Decimal("9200.000"))
        # Yearly expense: 150 + 300 + 500 + 62400 = 63350
        self.assertEqual(yearly_summary["total_expense"], Decimal("63350.000"))
        self.assertEqual(yearly_summary["net_profit"], Decimal("9200.000") - Decimal("63350.000"))

    def test_str_representations(self):
        """Verify model string representations."""
        self.assertIn("Electricity", str(self.bill))
        self.assertIn("Microsoft", str(self.license))
        self.assertIn("Steel", str(self.raw))
        self.assertEqual(str(self.sale), "Product A - 1200.000")
        self.assertEqual(str(self.contract), "Acme Corp - 8000.000")

    def test_finance_home_view(self):
        """Verify finance view handles period query parameter properly."""
        for period in ["weekly", "monthly", "yearly", "all"]:
            response = self.client.get(f"/finance/?period={period}")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context["period"], period)
            self.assertIn("summary", response.context)

    def test_add_entry(self):
        """Test adding different stream entries via POST."""
        # Add sale
        response = self.client.post("/finance/add/sales/", {
            "product_name": "New Widget",
            "product_id": "WID-999",
            "amount": "99.990",
            "period": "monthly",
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(sales.objects.filter(product_id="WID-999").exists())

        # Add bill
        response = self.client.post("/finance/add/bills/", {
            "utility": "I",
            "bill_amount": "85.500",
            "period": "weekly",
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(bills.objects.filter(utility="I", bill_amount=Decimal("85.500")).exists())

    def test_edit_entry(self):
        """Test updating an existing entry via POST."""
        response = self.client.post(f"/finance/edit/sales/{self.sale.id}/", {
            "product_name": "Product A Updated",
            "product_id": "PROD001",
            "amount": "1500.000",
            "period": "monthly",
        })
        self.assertEqual(response.status_code, 302)
        self.sale.refresh_from_db()
        self.assertEqual(self.sale.product_name, "Product A Updated")
        self.assertEqual(self.sale.amount, Decimal("1500.000"))

    def test_delete_entry(self):
        """Test deleting an entry via POST."""
        bill_id = self.bill.id
        response = self.client.post(f"/finance/delete/bills/{bill_id}/", {
            "period": "monthly",
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(bills.objects.filter(id=bill_id).exists())


