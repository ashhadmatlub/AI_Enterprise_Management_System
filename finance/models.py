from django.db import models


class FinanceTransaction(models.Model):

    class TransactionType(models.TextChoices):
        INCOME = "income", "Income"
        EXPENSE = "expense", "Expense"

    transaction_date = models.DateField()

    type = models.CharField(max_length=10, choices=TransactionType.choices)

    category = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    amount = models.DecimalField(max_digits=14, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type} - {self.amount}"

    class Meta:
        ordering = ["-transaction_date", "-created_at"]
