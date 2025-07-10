from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser


# ------------------ USER ------------------
class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('Junior', 'Junior'),
        ('Senior', 'Senior'),
        ('Doctor', 'Doctor'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    college = models.CharField(max_length=100, blank=True)
    profile_picture = models.ImageField(upload_to='avatars/', default='avatars/default.png')
    def __str__(self):
        return self.username

    @property
    def notifications_unread(self):
        return self.notifications.filter(is_read=False)


# ------------------ PROFILE (Follow system) ------------------
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    following = models.ManyToManyField('self', symmetrical=False, related_name='followers', blank=True)

    def following_count(self):
        return self.following.count()

    def followers_count(self):
        return self.followers.count()

    def __str__(self):
        return f"{self.user.username}'s Profile"


# ------------------ QUERY ------------------
class Query(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_anonymous = models.BooleanField(default=False)  # ✅

    def display_author(self):
        return "Anonymous" if self.is_anonymous else self.author.username

    def __str__(self):
        return self.title


# ------------------ ANSWER ------------------
class Answer(models.Model):
    query = models.ForeignKey(Query, on_delete=models.CASCADE, related_name='answers')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Answer by {self.author.username} on {self.query.title}"


# ------------------ MESSAGE ------------------
class Message(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.sender.username} to {self.receiver.username} at {self.timestamp}"

# ------------------ BLOG/EXPLORE POST ------------------
class Post(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

from django.db import models
from django.conf import settings

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('answer', 'Answer'),
        ('follow', 'Follow'),
        ('message', 'Message'),
    )

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type} to {self.recipient.username} from {self.sender}"
