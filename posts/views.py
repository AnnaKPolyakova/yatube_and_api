from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.conf.urls import handler404, handler500
from django.core.exceptions import ObjectDoesNotExist

from .forms import PostForm, CommentForm
from .models import Group, Post, User, Follow


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
    # post_list = Post.objects.all().select_related("group").filter(group=get_object_or_404(Group, slug=slug))
    # post_comment = Post.objects.all().select_related("comments")
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
    try:
        following = Follow.objects.filter(author=author.id, user=request.user.id)
        return render(request, 'profile.html', {
            'author': author,
            'page': page,
            'paginator': paginator,
            'following' : following
        })
    except ObjectDoesNotExist:
        return render(request, 'profile.html', {
            'author': author,
            'page': page,
            'paginator': paginator
        })


# def post_view(request, username, post_id):
#     post = get_object_or_404(Post, id=post_id, author__username=username)
#     author = post.author
#     post_comments = post.comments.all()
#     form = AddCommentForm(request.POST or None)
#     if not form.is_valid():
#         return render(request, 'post.html', {
#             'post': post,
#             'author': author,
#             'form': form,
#             'comments': post_comments,
#         })
#     form.instance.author = request.user
#     form.instance.post = post
#     form.save()
#     return redirect('post', username, post_id)

def post_view(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    author = post.author
    post_comments = post.comments.all()
    form = CommentForm(request.POST or None)
    return render(request, 'post.html', {
            'post': post,
            'author': author,
            'form': form,
            'comments': post_comments,
        })


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    author = post.author
    form = CommentForm(request.POST or None)
    if not form.is_valid():
        return render(request, 'comments.html',
                      {'form': form,
                       'author': author,
                       'post': post})
    form.instance.author = request.user
    form.instance.post = post
    form.save()
    return redirect('post', username, post_id)


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    if not request.user.username == username:
        return redirect('post', username, post_id)
    form = PostForm(request.POST or None, files=request.FILES or None, instance=post)
    if form.is_valid():
        form.instance.author = request.user
        form.instance.post = post
        form.save()
        return redirect('post', username, post_id)
    return render(request, "new_post.html", {'form': form, 'post': post})


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'follow.html', {
        'page': page,
        'paginator': paginator
    })


@login_required
def profile_follow(request, username):
    author = User.objects.get(username=username)
    if author == request.user:
        return render(request, "profile.html", {'author': author})
    else:
        if Follow.objects.filter(author=author.id, user=request.user.id).exists():
            return render(request, "profile.html", {'author': author})
        else:
            Follow.objects.create(
                    user=request.user,
                    author=author,
                )
            return redirect('profile',username=username)


@login_required
def profile_unfollow(request, username):
    author = User.objects.get(username=username)
    follow_dell = Follow.objects.get(author=author.id, user=request.user.id)
    follow_dell.delete()
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
