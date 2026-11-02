from django import forms
from .models import bills, licensing, raw_material, sales, contracts


class BillForm(forms.ModelForm):
    class Meta:
        model = bills
        fields = ["utility", "bill_amount"]
        labels = {
            "utility": "Utility Type",
            "bill_amount": "Bill Amount ($)",
        }
        widgets = {
            "utility": forms.Select(attrs={"class": "form-select"}),
            "bill_amount": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.001", "placeholder": "e.g. 250.000"}
            ),
        }


class LicensingForm(forms.ModelForm):
    class Meta:
        model = licensing
        fields = ["company", "bill_amount"]
        labels = {
            "company": "Vendor / Company",
            "bill_amount": "License Cost ($)",
        }
        widgets = {
            "company": forms.Select(attrs={"class": "form-select"}),
            "bill_amount": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.001", "placeholder": "e.g. 450.000"}
            ),
        }


class RawMaterialForm(forms.ModelForm):
    class Meta:
        model = raw_material
        fields = ["material", "bill_amount"]
        labels = {
            "material": "Material Type",
            "bill_amount": "Total Cost ($)",
        }
        widgets = {
            "material": forms.Select(attrs={"class": "form-select"}),
            "bill_amount": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.001", "placeholder": "e.g. 1200.000"}
            ),
        }


class SalesForm(forms.ModelForm):
    class Meta:
        model = sales
        fields = ["product_name", "product_id", "amount"]
        labels = {
            "product_name": "Product Name",
            "product_id": "Product ID / SKU",
            "amount": "Sale Amount ($)",
        }
        widgets = {
            "product_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g. Cloud Connector v2"}
            ),
            "product_id": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g. PRD-001"}
            ),
            "amount": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.001", "placeholder": "e.g. 4800.000"}
            ),
        }


class ContractForm(forms.ModelForm):
    class Meta:
        model = contracts
        fields = ["client_name", "client_id", "description", "amount"]
        labels = {
            "client_name": "Client Name",
            "client_id": "Client Account ID",
            "description": "Scope & Deliverables",
            "amount": "Contract Value ($)",
        }
        widgets = {
            "client_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g. Acme Corporation"}
            ),
            "client_id": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g. CLI-201"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Brief description of deliverables or SLA terms...",
                }
            ),
            "amount": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.001", "placeholder": "e.g. 15000.000"}
            ),
        }
