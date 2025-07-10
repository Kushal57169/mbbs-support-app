from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Q, Max
from django.utils.timezone import now
from django.http import HttpResponseForbidden

from .models import CustomUser, Profile, Query, Answer, Message, Post
from .forms import CustomUserCreationForm, QueryForm, AnswerForm, MessageForm, PostForm
from .utils import send_notification  # ✅ For notifications

User = get_user_model()

# ------------------ REGISTER ------------------
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'community/register.html', {'form': form})


# ------------------ DASHBOARD ------------------
@login_required
def dashboard_view(request):
    user_queries = Query.objects.filter(author=request.user).order_by('-created_at')
    following_count = request.user.profile.following.count()
    followers_count = request.user.profile.followers.count()
    return render(request, 'community/dashboard.html', {
        'queries': user_queries,
        'following_count': following_count,
        'followers_count': followers_count
    })


# ------------------ FOLLOW SYSTEM ------------------
@login_required
def user_list(request):
    users = CustomUser.objects.exclude(id=request.user.id)
    return render(request, 'community/user_list.html', {'users': users})


from .utils import send_notification  # Make sure this is imported

@login_required
def follow_user(request, user_id):
    target_user = get_object_or_404(CustomUser, id=user_id)
    profile = request.user.profile

    if target_user.profile in profile.following.all():
        profile.following.remove(target_user.profile)
    else:
        profile.following.add(target_user.profile)

        # ✅ Send notification for following
        send_notification(
            recipient=target_user,
            sender=request.user,
            type='follow',
            message=f"{request.user.username} started following you."
        )

    return redirect('all_users')



# ------------------ QUERIES ------------------
@login_required
def create_query(request):
    if request.method == 'POST':
        form = QueryForm(request.POST)
        if form.is_valid():
            query = form.save(commit=False)
            query.author = request.user
            query.save()
            return redirect('query_list')
    else:
        form = QueryForm()
    return render(request, 'community/create_query.html', {'form': form})


@login_required
def query_list(request):
    user_college = request.user.college
    show_all = request.GET.get('all')
    if show_all == '1':
        queries = Query.objects.all().order_by('-created_at')
    else:
        queries = Query.objects.filter(author__college=user_college).order_by('-created_at')
    return render(request, 'community/query_list.html', {
        'queries': queries,
        'showing_all': show_all == '1'
    })


@login_required
def query_detail(request, query_id):
    query = get_object_or_404(Query, id=query_id)
    answers = query.answers.order_by('-created_at')
    can_answer = request.user.role in ['Senior', 'Doctor']

    if request.method == 'POST' and can_answer:
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.query = query
            answer.author = request.user
            answer.save()

            # ✅ Notify query author
            send_notification(
                recipient=query.author,
                sender=request.user,
                type='answer',
                message=f"{request.user.username} answered your query: {query.title}"
            )


            return redirect('query_detail', query_id=query.id)
    else:
        form = AnswerForm()

    return render(request, 'community/query_detail.html', {
        'query': query,
        'answers': answers,
        'form': form,
        'can_answer': can_answer
    })


@login_required
def delete_query(request, query_id):
    query = get_object_or_404(Query, id=query_id)
    if query.author == request.user:
        query.delete()
    return redirect('query_list')


# ------------------ INBOX & CHAT ------------------
@login_required
def inbox(request):
    user = request.user
    latest_messages = (
        Message.objects
        .filter(Q(sender=user) | Q(receiver=user))
        .values('sender', 'receiver')
        .annotate(last_sent=Max('timestamp'))
        .order_by('-last_sent')
    )

    chat_partners = set()
    for msg in latest_messages:
        if msg['sender'] == user.id:
            chat_partners.add(msg['receiver'])
        else:
            chat_partners.add(msg['sender'])

    users = CustomUser.objects.filter(id__in=chat_partners)
    inbox_data = []

    for chat_user in users:
        last_msg = Message.objects.filter(
            Q(sender=user, receiver=chat_user) | Q(sender=chat_user, receiver=user)
        ).order_by('-timestamp').first()

        inbox_data.append({
            'user': chat_user,
            'last_message': last_msg.content if last_msg else '',
            'timestamp': last_msg.timestamp if last_msg else now(),
        })

    inbox_data.sort(key=lambda x: x['timestamp'], reverse=True)
    return render(request, 'inbox.html', {'inbox_data': inbox_data})


from .models import Message
from .forms import MessageForm  # make sure it's imported
from .utils import send_notification

@login_required
def chat_view(request, username):
    other_user = get_object_or_404(CustomUser, username=username)

    messages = Message.objects.filter(
        Q(sender=request.user, receiver=other_user) |
        Q(sender=other_user, receiver=request.user)
    ).order_by('timestamp')

    if request.method == 'POST':
        content = request.POST.get("content")
        if content:
            Message.objects.create(
                sender=request.user,
                receiver=other_user,
                content=content
            )

            # ✅ Send notification
            send_notification(
                recipient=other_user,
                sender=request.user,
                type='message',
                message=f"{request.user.username} sent you a message."
            )

            return redirect('chat_view', username=other_user.username)

    return render(request, 'community/chat.html', {
        'messages': messages,
        'other_user': other_user
    })



# ------------------ PROFILE ------------------
@login_required
def all_users_view(request):
    users = CustomUser.objects.exclude(id=request.user.id)
    following = request.user.profile.following.all()
    return render(request, 'community/all_users.html', {'users': users, 'following': following})


@login_required
def user_profile_view(request, username):
    user_profile = get_object_or_404(CustomUser, username=username)
    queries = Query.objects.filter(author=user_profile).order_by('-created_at')
    answers = Answer.objects.filter(author=user_profile).order_by('-created_at')
    followers = user_profile.profile.followers.all()
    following = user_profile.profile.following.all()

    is_following = request.user.profile.following.filter(user=user_profile).exists()
    tab = request.GET.get('tab', 'queries')

    return render(request, 'community/user_profile.html', {
        'user_profile': user_profile,
        'queries': queries,
        'answers': answers,
        'followers': followers,
        'following': following,
        'is_following': is_following,
        'tab': tab
    })


# ------------------ DELETE MESSAGE ------------------
@login_required
def delete_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    if message.sender != request.user:
        return HttpResponseForbidden("You can't delete this message.")
    message.delete()
    return redirect('chat_view', username=message.receiver.username if message.receiver != request.user else message.sender.username)


# ------------------ MY QUERIES ------------------
@login_required
def my_queries_view(request):
    user_queries = Query.objects.filter(author=request.user).order_by('-created_at')
    return render(request, 'community/my_queries.html', {'queries': user_queries})


# ------------------ SEARCH ------------------
@login_required
def search_view(request):
    query = request.GET.get('q', '')

    query_results = Query.objects.filter(
        Q(title__icontains=query) | Q(body__icontains=query)
    )

    user_results = CustomUser.objects.filter(
        Q(username__icontains=query) | Q(college__icontains=query)
    )

    return render(request, 'community/search_results.html', {
        'query': query,
        'query_results': query_results,
        'user_results': user_results
    })


# ------------------ EXPLORE ------------------
def explore_view(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'community/explore.html', {'posts': posts})


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('explore')
    else:
        form = PostForm()
    return render(request, 'community/create_post.html', {'form': form})


from .models import Notification

@login_required
def notifications_view(request):
    notifications = Notification.objects.filter(recipient=request.user)
    # Mark all as read
    notifications.update(is_read=True)
    return render(request, "notifications.html", {"notifications": notifications})

from .models import Notification

def post_answer(request, query_id):
    query = get_object_or_404(Query, id=query_id)

    if request.method == "POST":
        content = request.POST.get("content")
        answer = Answer.objects.create(
            author=request.user,
            query=query,
            body=content
        )

        # ✅ Create notification correctly
        if request.user != query.author:
            Notification.objects.create(
                recipient=query.author,
                sender=request.user,
                type='answer',
                message=f"{request.user.username} answered your query: '{query.title}'"
            )

        return redirect("query_detail", query_id=query.id)

    # 🚨 Missing return added below
    return redirect("query_detail", query_id=query.id)


@login_required
def start_chat_view(request, username):
    other_user = get_object_or_404(CustomUser, username=username)
    if other_user == request.user:
        return redirect('inbox')  # Can't chat with self

    return redirect('chat_view', username=other_user.username)

# ------------------ DELETE ANSWER ------------------
@login_required
def delete_answer(request, answer_id):
    answer = get_object_or_404(Answer, id=answer_id)

    if answer.author != request.user:
        return HttpResponseForbidden("You can only delete your own answers.")

    query_id = answer.query.id
    answer.delete()

    return redirect('query_detail', query_id=query_id)
