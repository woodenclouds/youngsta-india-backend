from django.db import models
import uuid
import datetime
from datetime import timedelta
from django.utils import timezone

# Create your models here.
class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_deleted = models.BooleanField(default=False, blank=True, null=True)
    created_at = models.DateTimeField( db_index=True, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
        
    
class SlugModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.CharField(unique=True, max_length=100)
    is_deleted = models.BooleanField(default=False, blank=True, null=True)
    created_at = models.DateTimeField( db_index=True, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True    


class Otp(BaseModel):
    otp = models.CharField(max_length=6)
    email = models.EmailField()
    attempt = models.PositiveIntegerField(default=0)
    expiration_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "main_otp"
        verbose_name = "Otp"
        verbose_name_plural = "Otps"

    def __str__(self):
        return f"{self.email}-{self.otp}"

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = timezone.now()  # Set created_at if it's None
        if not self.expiration_time:
            # Calculate expiration time (3 minutes from created_at)
            self.expiration_time = self.created_at + timedelta(minutes=3)
        super().save(*args, **kwargs)  # Use super without passing parameters

    def is_expired(self):
        if self.expiration_time:
            return self.expiration_time <= timezone.now()
        return False