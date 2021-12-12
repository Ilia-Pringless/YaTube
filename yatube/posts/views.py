from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post

COUNT_POST = settings.COUNT_POST


User = get_user_model()


def index(request):
    post_list = Post.objects.all()
    # Показывать по 10 записей на странице
    paginator = Paginator(post_list, COUNT_POST)
    # Из URL извлекаем номер запрошенной страницы - это значение параметра page
    page_number = request.GET.get('page')
    # Получаем набор записей для страницы с запрошенным номером
    page_obj = paginator.get_page(page_number)
    template = 'posts/index.html'
    title = 'Последние обновления на сайте'
    heading = 'Последние обновления на сайте'
    context = {
        'heading': heading,
        'title': title,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    # Подключен Paginator
    post_list = group.posts.all()
    paginator = Paginator(post_list, COUNT_POST)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    heading = group.title

    context = {
        'title': f'Записи сообщества {group.title}',
        'group': group,
        'page_obj': page_obj,
        'heading': heading,
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    # Подключен Paginator
    post_list = Post.objects.filter(author=author)
    paginator = Paginator(post_list, COUNT_POST)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    following = request.user.is_authenticated and author.following.exists()
    context = {
        'title': 'Профайл пользователя',
        'post_list': post_list,
        'author': author,
        'page_obj': page_obj,
        'following': following,
        'user_profile': request.user,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    get_post = Post.objects.get(id=post_id)
    author = get_post.author
    posts = Post.objects.filter(author=author)
    text = get_post.text
    created = get_post.created
    group = get_post.group
    form = CommentForm(request.POST or None)
    title = f'Пост: {text[0:29]}'
    comments = Comment.objects.filter(post=get_post)
    context = {
        'title': title,
        'created': created,
        'author': author,
        'posts': posts,
        'group': group,
        'get_post': get_post,
        'text': text,
        'form': form,
        'comments': comments,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.author = username = request.user
            post.save()
            return redirect('posts:profile', username=username)
    return render(request, template, {'form': form})


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    get_post = get_object_or_404(Post, id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=get_post
    )

    if get_post.author == request.user:
        is_edit = True
        if request.method == 'POST':
            if form.is_valid():
                post = form.save(commit=False)
                post.author = request.user
                form.save()
                return redirect('posts:post_detail', post_id=post_id)
            return (render(request, template,
                    {'form': form, 'is_edit': is_edit}))
        return render(request, template, {'form': form, 'is_edit': is_edit})
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def add_comment(request, post_id):
    post = Post.objects.get(id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    user = request.user
    author = user.follower.values('author')
    # Подключен paginator
    post_list = Post.objects.filter(author__id__in=author)
    paginator = Paginator(post_list, COUNT_POST)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    title = 'Новые записи ваших авторов'
    heading = 'Новые записи ваших авторов'
    template = 'posts/follow.html'
    context = {
        'heading': heading,
        'title': title,
        'page_obj': page_obj,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = User.objects.get(username=username)
    if author != request.user:
        Follow.objects.get_or_create(
            user=request.user,
            author=author,
        )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = User.objects.get(username=username)
    Follow.objects.filter(
        user=request.user,
        author=author,
    ).delete()
    return redirect('posts:profile', username=username)
