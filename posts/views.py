from django.conf.urls import handler404, handler500
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User, Like


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'index.html',
        {'page': page, 'paginator': paginator}
    )


def group_post(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {
        'group': group,
        'page': page,
        'paginator': paginator,
    })


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if not form.is_valid():
        return render(request, 'new_post.html', {'form': form})
    form.instance.author = request.user
    form.save()
    return redirect('index')


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    following = (request.user.is_authenticated and
                 author != request.user and
                 Follow.objects.filter(author=author,
                                       user=request.user).exists())
    return render(request, 'profile.html', {
        'author': author,
        'page': page,
        'paginator': paginator,
        'following': following,
    })


def post_view(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    comments = post.comments.all()
    form = CommentForm(request.POST or None)
    like = (request.user.is_authenticated and
            Like.objects.filter(author__username=request.user.username,
                                post=post).exists())
    return render(request, 'post.html', {
        'post': post,
        'author': post.author,
        'form': form,
        'comments': comments,
        'like': like,
    })


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    form = CommentForm(request.POST or None)
    if not form.is_valid():
        return render(request, 'comments.html',
                      {'form': form,
                       'author': post.author,
                       'post': post})
    form.instance.author = request.user
    form.instance.post = post
    form.save()
    return redirect('post', username, post_id)


@login_required
def post_edit(request, username, post_id):
    if request.user.username != username:
        return redirect('post', username, post_id)
    post = get_object_or_404(Post,
                             id=post_id,
                             author__username=username)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    if not form.is_valid():
        return render(request, "new_post.html", {'form': form, 'post': post})
    form.instance.author = request.user
    form.save()
    return redirect('post', username, post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'follow.html', {
        'page': page,
        'paginator': paginator,
    })


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user and not Follow.objects.filter(
            author=author,
            user=request.user).exists():
        Follow.objects.create(
            user=request.user,
            author=author,
        )
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    follow = get_object_or_404(Follow,
                               author__username=username,
                               user=request.user)
    follow.delete()
    return redirect('profile', username=username)


def page_not_found(request, exception):
    # Переменная exception содержит отладочную информацию,
    # выводить её в шаблон пользователской страницы 404 мы не станем
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(
        request,
        "misc/500.html",
        status=500
    )


@login_required
def post_like(request, username, post_id):
    author = get_object_or_404(User, username=request.user)
    post = get_object_or_404(Post, id=post_id, author__username=username)
    Like.objects.get_or_create(
                post=post,
                author=author,
            )
    return redirect('post', username, post_id)


@login_required
def post_delete_like(request, username, post_id):
    like = get_object_or_404(Like,
                             author=request.user,
                             post__id=post_id)
    like.delete()
    return redirect('post', username, post_id)
