from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.core.paginator import Paginator
from .models import Post, Like, Message
from .forms import PostForm, MessageForm
from accounts.models import User

def home(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('HX-Request') and page_number:
        return render(request, 'microblog/partials/post_list.html', {'page_obj': page_obj})

    form = PostForm()
    return render(request, 'microblog/home.html', {'page_obj': page_obj, 'form': form})

@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            if request.headers.get('HX-Request'):
                return render(request, 'microblog/partials/post.html', {'post': post})
            return redirect('home')
    return redirect('home')

@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            if request.headers.get('HX-Request'):
                return render(request, 'microblog/partials/post.html', {'post': post})
            return redirect('home')
    else:
        form = PostForm(instance=post)

    if request.headers.get('HX-Request'):
        return render(request, 'microblog/partials/post_edit_form.html', {'form': form, 'post': post})
    return render(request, 'microblog/post_edit.html', {'form': form, 'post': post})

@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        return HttpResponseForbidden()

    if request.method == 'POST':
        post.delete()
        if request.headers.get('HX-Request'):
            return HttpResponse("")
        return redirect('home')
    return redirect('home')

def post_like(request, pk):
    post = get_object_or_404(Post, pk=pk)
    user = request.user if request.user.is_authenticated else None
    session_key = request.session.session_key

    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    if user:
        like_filter = {'post': post, 'user': user}
    else:
        like_filter = {'post': post, 'session_key': session_key}

    like = Like.objects.filter(**like_filter).first()
    if like:
        like.delete()
        liked = False
    else:
        Like.objects.create(**like_filter)
        liked = True

    if request.headers.get('HX-Request'):
        return render(request, 'microblog/partials/like_button.html', {'post': post, 'liked': liked})

    return redirect('home')

@login_required
def messages_view(request):
    received_messages = request.user.received_messages.all()
    sent_messages = request.user.sent_messages.all()
    return render(request, 'microblog/messages.html', {
        'received_messages': received_messages,
        'sent_messages': sent_messages
    })

@login_required
def message_send(request, username):
    recipient = get_object_or_404(User, username=username)
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.sender = request.user
            msg.recipient = recipient
            msg.save()
            return redirect('messages_view')
    else:
        form = MessageForm()
    return render(request, 'microblog/message_send.html', {'form': form, 'recipient': recipient})
