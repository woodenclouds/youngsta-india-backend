from celery import shared_task
import datetime
from activities.models import *
from accounts.models import *
from payments.models import *

@shared_task
def process_referral_rewards():
    today = datetime.date.today()
    purchase_items = PurchaseItems.objects.filter(is_returned=False)
    for item in purchase_items:
        if Transaction.objects.filter(
                        purchase=item.purchase,  
                        transaction_status="SUCCESS"
                    ).exists():
            
            if( referal := Referral.objects.filter(product=item.product, order= item.purchase,is_paid=False)).exists():
                referal = Referral.objects.filter(product=item.product, order= item.purchase,is_paid=False)
                return_days_number = item.product.return_in
                return_day = item.created_at.date() + datetime.timedelta(days=return_days_number)

                if return_day + datetime.timedelta(days=1) <= today:
                    user_refered = UserProfile.objects.get(user=referal.referred_by)
                    wallet = Wallet.objects.get(user=user_refered)
                    wallet.balance += item.product.referal_Amount
                    wallet.save()
                    referal.is_paid=True
                    referal.save()
                    WalletTransaction.objects.create(user=user_refered,
                                                     amount= referal.referral_amount,
                                                     success=True,
                    )


