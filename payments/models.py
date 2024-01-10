from django.db import models
from main.models import *


class Wallet(BaseModel):
    user = models.ForeignKey('accounts.UserProfile', on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default='0')

    class Meta:
        db_table = 'payment_wallet'
        managed = True
        verbose_name = 'wallet'
        verbose_name_plural = 'wallets'

    def __str__(self):
        return f"{self.user.name}'s wallet"
    
class Payments(BaseModel):
    user = models.ForeignKey('accounts.UserProfile', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default='0')
    
    class Meta:
        db_table = 'payment_payments'
        managed = True
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'

    def __str__(self):
        return f"{self.user.name}"
    

class Transaction(BaseModel):
    user = models.ForeignKey('accounts.UserProfile', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default='0')
    success = models.BooleanField(default=False)

    class Meta:
        db_table = 'payment_transaction'
        managed = True
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
    def __str__(self):
        return f"{self.user.name}-{self.amount}-{self.created_at}'s transaction"
    

    
# coins models
# log
# point amount boolean isactive or inactive
# wallet