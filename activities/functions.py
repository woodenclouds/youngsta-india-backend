from django.contrib.contenttypes.models import ContentType
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
