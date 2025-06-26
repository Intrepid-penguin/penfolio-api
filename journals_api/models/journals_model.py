from django.db import models
from django.contrib.auth.models import User

class Journal(models.Model):
    """
    Represents a single journal entry in the application.
    """
    class MoodTag(models.TextChoices):
        """
        Represents the mood tag choices for a journal entry.
        """
        MERRY = 'ME', 'Merry'
        GLOOMY = 'GL', 'Gloomy'
        COVERT = 'CO', 'Covert'

    owner: 'User' = models.ForeignKey(User, on_delete=models.CASCADE, related_name='journals')
    title = models.CharField(max_length=200)
    content = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    mood_tag = models.CharField(
        max_length=2,
        choices=MoodTag.choices,
        default=MoodTag.MERRY,
    )

    class Meta:
        ordering = ['-date_added']

    def __str__(self):
        return f'"{self.title}"' # by {self.owner.username} on {self.date_added.strftime("%Y-%m-%d")}'
