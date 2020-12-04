from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):

    class Meta:

        model = Post
        fields = ('group', 'text', 'image')


class AddCommentForm(forms.ModelForm):

    class Meta:

        model = Comment
        fields = ('text',)