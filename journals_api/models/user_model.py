from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.hashers import make_password, check_password

# Create your models here.
class UserProfile(models.Model):
    """
    Represents a user profile with additional information such as streak and PIN.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_content_date = models.DateField(null=True, blank=True)
    pin = models.CharField(max_length=500)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def set_pin(self, raw_pin: str):
        """Hashes and sets the user's PIN."""
        self.pin = make_password(raw_pin)
        self.save()

    def check_pin(self, raw_pin: str) -> bool:
        """Checks if the provided raw PIN matches the stored hash."""
        if not self.pin or not raw_pin:
            return False
        return check_password(raw_pin, self.pin)

    @property
    def has_pin(self) -> bool:
        """A convenient property for API schemas to check if a PIN is set."""
        return bool(self.pin)

    
@receiver(post_save, sender=User)
def create_covertuser(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        
@receiver(post_save, sender=User)
def save_covertuser(sender, instance, created, **kwargs):
    instance.user_profile.save()
