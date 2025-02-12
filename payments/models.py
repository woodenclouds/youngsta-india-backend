from django.db import models
from main.models import *
from datetime import date
from activities.models import Purchase


class Wallet(BaseModel):
    user = models.ForeignKey("accounts.UserProfile", on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default="0")

    class Meta:
        db_table = "payment_wallet"
        managed = True
        verbose_name = "wallet"
        verbose_name_plural = "wallets"

    def __str__(self):
        return f"{self.user.first_name}'s wallet"
    
class WalletTransaction(BaseModel):
    WALLET_TRANSACTION_STATUS = (
        ('processing','Processing'),
        ('success','Success'),
        ('failed','Failed'),
    )
    user = models.ForeignKey("accounts.UserProfile", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default="0")
    transaction_mode = models.CharField(max_length=155, blank=True,null=True)
    transaction_type = models.CharField(max_length=155, blank=True,null=True)
    transaction_id = models.CharField(max_length=155, blank=True,null=True)
    transaction_status = models.CharField(choices=WALLET_TRANSACTION_STATUS,max_length=155, blank=True, null=True)
    transaction_description = models.CharField(max_length=155, blank=True, null=True)
    success = models.BooleanField(default=False)
    credit = models.BooleanField(default=True, blank=True, null=True)
    class Meta:
        db_table = "payment_wallet_transaction"
        managed = True
        verbose_name = "Wallet Transaction"
        verbose_name_plural = "Wallet Transactions"

    def __str__(self):
        return f"{self.amount}-{self.user.first_name}'s transaction"


class Payments(BaseModel):
    user = models.ForeignKey("accounts.UserProfile", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default="0")

    class Meta:
        db_table = "payment_payments"
        managed = True
        verbose_name = "Payment"
        verbose_name_plural = "Payments"

    def __str__(self):
        return f"{self.user.name}"


class Transaction(BaseModel):
    user = models.ForeignKey("accounts.UserProfile", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default="0")
    transaction_mode = models.CharField(max_length=155, blank=True,null=True)
    transaction_type = models.CharField(max_length=155, blank=True,null=True)
    transaction_id = models.CharField(max_length=155, blank=True,null=True)
    transaction_status = models.CharField(max_length=155, blank=True, null=True)
    transaction_description = models.CharField(max_length=155, blank=True, null=True)
    success = models.BooleanField(default=False)
    credit = models.BooleanField(default=True, blank=True, null=True)
    purchase = models.ForeignKey(Purchase, null=True, blank=True, on_delete=models.CASCADE,related_name="transactions")
    class Meta:
        db_table = "payment_transaction"
        managed = True
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"

    def __str__(self):
        return f"{self.amount}-{self.created_at}'s transaction"


# coins models
# log
# point amount boolean isactive or inactive
# wallet


class Invoice(models.Model):
    invoice_no = models.CharField(max_length=128, unique=True)
    issued_at = models.DateTimeField(default=timezone.now)
    customer_name = models.CharField(max_length=255)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    purchase = models.ForeignKey(
        "activities.Purchase", on_delete=models.CASCADE, blank=True, null=True,related_name="invoices"
    )

    def save(self, *args, **kwargs):
        if not self.invoice_no:
            self.invoice_no = self.generate_unique_invoice_no()
            
            if self.purchase:
                self.purchase.invoice_no = self.invoice_no
                self.purchase.save()
        super().save(*args, **kwargs)

    @staticmethod
    def get_financial_year():
        current_year = date.today().year
        current_month = date.today().month
        if current_month < 4:
            return f"{current_year-1 % 100:02d}{current_year % 100:02d}"
        else:
            return f"{current_year % 100:02d}{(current_year + 1) % 100:02d}"

    def generate_unique_invoice_no(self):
        prefix = "YNGSTA"
        financial_year = self.get_financial_year()
        new_counter = 1

        # Get the maximum counter for the current financial year
        if Invoice.objects.filter(invoice_no__startswith=f"{prefix}{financial_year}").exists():
            last_invoice = (
                Invoice.objects.filter(invoice_no__startswith=f"{prefix}{financial_year}")
                .order_by("-invoice_no")
                .first()
            )

            last_counter = int(last_invoice.invoice_no[-3:])  # Extract the last 3 digits
            new_counter = last_counter + 1

        # Format the new invoice number
        return f"{prefix}{financial_year}{new_counter:03d}"

    def __str__(self):
        return f"Invoice {self.invoice_no} - {self.customer_name}"
