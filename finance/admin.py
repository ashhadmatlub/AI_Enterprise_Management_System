from django.contrib import admin
from .models import (
    bills,
    licensing,
    raw_material,
    sales,
    contracts,
    Expenses,
    Revenue,
    Profit,
)

admin.site.register(bills)
admin.site.register(licensing)
admin.site.register(raw_material)
admin.site.register(sales)
admin.site.register(contracts)
admin.site.register(Expenses)
admin.site.register(Revenue)
admin.site.register(Profit)
