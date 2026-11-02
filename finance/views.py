from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from hr.models import Employee

from .forms import (
    BillForm,
    ContractForm,
    LicensingForm,
    RawMaterialForm,
    SalesForm,
)
from .models import Profit, bills, contracts, licensing, raw_material, sales

STREAM_MODELS = {
    "bills": (bills, BillForm, "Utility Bill"),
    "licensing": (licensing, LicensingForm, "Software License"),
    "raw_material": (raw_material, RawMaterialForm, "Raw Material"),
    "sales": (sales, SalesForm, "Product Sale"),
    "contracts": (contracts, ContractForm, "Client Contract"),
}


def finance_home(request):
    period = request.GET.get("period", "monthly")
    if period not in ["weekly", "monthly", "yearly", "all"]:
        period = "monthly"

    summary = Profit.calculate_for_period(period)
    start_date, end_date = Profit.get_date_range(period)

    # Filter querysets according to the active period
    def apply_filter(qs):
        if start_date and end_date:
            return qs.filter(created_at__range=(start_date, end_date))
        return qs

    bills_qs = apply_filter(bills.objects.all()).order_by("-created_at")
    licensing_qs = apply_filter(licensing.objects.all()).order_by("-created_at")
    raw_material_qs = apply_filter(raw_material.objects.all()).order_by("-created_at")
    sales_qs = apply_filter(sales.objects.all()).order_by("-created_at")
    contracts_qs = apply_filter(contracts.objects.all()).order_by("-created_at")

    # Profit margin calculation
    total_rev = summary["total_revenue"]
    net_prof = summary["net_profit"]
    margin = (net_prof / total_rev * 100) if total_rev > 0 else 0

    active_employees_count = Employee.objects.filter(status="active").count()

    context = {
        "period": period,
        "summary": summary,
        "margin": margin,
        "active_employees_count": active_employees_count,
        "bills_list": bills_qs,
        "licensing_list": licensing_qs,
        "raw_material_list": raw_material_qs,
        "sales_list": sales_qs,
        "contracts_list": contracts_qs,
        # Blank forms for the Add Modals
        "bill_form": BillForm(),
        "licensing_form": LicensingForm(),
        "raw_material_form": RawMaterialForm(),
        "sales_form": SalesForm(),
        "contract_form": ContractForm(),
    }
    return render(request, "finance/home.html", context)


@require_POST
def add_entry(request, stream_type):
    period = request.POST.get("period", "monthly")
    if stream_type not in STREAM_MODELS:
        messages.error(request, "Invalid financial stream specified.")
        return redirect(f"{reverse('finance:home')}?period={period}")

    model_class, form_class, label = STREAM_MODELS[stream_type]
    form = form_class(request.POST)
    if form.is_valid():
        form.save()
        messages.success(request, f"{label} added successfully.")
    else:
        messages.error(request, f"Could not add {label}. Please review your inputs.")

    return redirect(f"{reverse('finance:home')}?period={period}")


@require_POST
def edit_entry(request, stream_type, item_id):
    period = request.POST.get("period", "monthly")
    if stream_type not in STREAM_MODELS:
        messages.error(request, "Invalid financial stream specified.")
        return redirect(f"{reverse('finance:home')}?period={period}")

    model_class, form_class, label = STREAM_MODELS[stream_type]
    obj = get_object_or_404(model_class, id=item_id)
    form = form_class(request.POST, instance=obj)
    if form.is_valid():
        form.save()
        messages.success(request, f"{label} updated successfully.")
    else:
        messages.error(request, f"Could not update {label}. Please check the fields.")

    return redirect(f"{reverse('finance:home')}?period={period}")


@require_POST
def delete_entry(request, stream_type, item_id):
    period = request.POST.get("period", "monthly")
    if stream_type not in STREAM_MODELS:
        messages.error(request, "Invalid financial stream specified.")
        return redirect(f"{reverse('finance:home')}?period={period}")

    model_class, _, label = STREAM_MODELS[stream_type]
    obj = get_object_or_404(model_class, id=item_id)
    obj.delete()
    messages.success(request, f"{label} deleted successfully.")

    return redirect(f"{reverse('finance:home')}?period={period}")
