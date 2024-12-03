from django.contrib.contenttypes.models import ContentType
from datetime import date

from .models import ActivityLog

def log_activity(user, action, object_instance=None):
    # Get the content type of the object_instance if provided
    content_type = None
    object_id = None
    
    if object_instance:
        content_type = ContentType.objects.get_for_model(object_instance)
        object_id = object_instance.id

    # Create an instance of ActivityLog
    activity_log = ActivityLog.objects.create(
        user=user,
        action=action,
        content_type=content_type,
        object_id=object_id,
    )
    return activity_log



def generate_invoice_number(prefix="YNGSTA", counter=1):
    # Determine the financial year
    current_year = date.today().year
    current_month = date.today().month
    if current_month < 4:
        financial_year = f"{current_year-1 % 100:02d}{current_year % 100:02d}"
    else:
        financial_year = f"{current_year % 100:02d}{(current_year + 1) % 100:02d}"
    
    # Generate the serial number
    serial_number = f"{prefix}{financial_year}{counter:03d}"
    return serial_number