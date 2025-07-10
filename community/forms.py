from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Query, Answer, Message

# ----------------- User Registration -----------------
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'role', 'college']


# ----------------- Query Form (only one!) -----------------
class QueryForm(forms.ModelForm):
    class Meta:
        model = Query
        fields = ['title', 'body', 'is_anonymous']


# ----------------- Answer Form -----------------
class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['body']


# ----------------- Chat Message Form -----------------
class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Type a message...'
            }),
        }

from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'body']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write your experience, tip, or article...'}),
        }
