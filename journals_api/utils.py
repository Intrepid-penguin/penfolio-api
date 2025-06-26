from datetime import timedelta
from django.utils import timezone

from journals_api.models.user_model import UserProfile


def update_streak_on_creation(user):
    """Updates the current and longest streak for a user when content is created."""
    try:
        user_profile = user.user_profile
    except UserProfile.DoesNotExist:
        return  # Should not happen due to signals, but for safety

    today = timezone.now().date()

    if user_profile.last_content_date == today:
        # User already created content today, no streak change
        return

    if user_profile.last_content_date == today - timedelta(days=1):
        # Streak continues
        user_profile.current_streak += 1
    else:
        # Streak broken or this is the first content
        user_profile.current_streak = 1

    user_profile.longest_streak = max(user_profile.longest_streak, user_profile.current_streak)
    user_profile.last_content_date = today
    user_profile.save()
