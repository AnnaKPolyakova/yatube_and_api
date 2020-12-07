from django import forms

from .models import Comment, Follow, Post


class PostForm(forms.ModelForm):

    class Meta:

        model = Post
        fields = ('group', 'text', 'image')


class CommentForm(forms.ModelForm):

    class Meta:

        model = Comment
        fields = ('text',)
