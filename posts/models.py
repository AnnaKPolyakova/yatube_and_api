from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Группа',
        help_text='Не более 200 символов',
    )
    slug = models.SlugField(
        unique=True,
        max_length=40,
        verbose_name='Адрес для страницы с задачей',
        help_text='Не более 40 символов',
    )
    description = models.TextField(
        verbose_name='Описание',
        help_text='Краткое описание',
    )

    class Meta:
        verbose_name_plural = 'Группы'

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст',
        help_text='Поведуйте миру о себе. '
                  '<p> *Поле обязательно для заполнения. </p>',
    )
    pub_date = models.DateTimeField(
        verbose_name="Дата публикации",
        auto_now_add=True,
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='posts',
        verbose_name="Автор",
    )
    group = models.ForeignKey(
        Group, on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='Группа',
        help_text='Возможно, будет уместно выбрать '
                  'соответствубщую Вашему посту группу.',
    )
    image = models.ImageField(
        upload_to='posts/',
        blank=True,
        null=True)

    class Meta:
        ordering = ('-pub_date',)
        verbose_name_plural = 'Посты'
        verbose_name = 'пост'

    def __str__(self):
        return f'{self.text[:15]} @{self.author} #{self.group} {self.pub_date}'


class Comment(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE,
        related_name='comments',
        verbose_name="Пост",
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='comments',
        verbose_name="Автор",
    )
    text = models.TextField(
        verbose_name='Текст',
        help_text='Добавье свой комментарий. '
                  '<p> *Поле обязательно для заполнения. </p>',
    )
    created = models.DateTimeField(
        verbose_name="Дата публикации",
        auto_now_add=True,
    )

    class Meta:
        ordering = ('-created',)
        verbose_name_plural = 'Комментарии'
        verbose_name = 'Комментарий'

    def __str__(self):
        return f'{self.text[:15]} @{self.author} #{self.post} {self.created}'


class Follow (models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='follower',
        verbose_name="Подписчик",
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='following',
        verbose_name="Пользователь на которого подписались",
    )

    class Meta:
        verbose_name_plural = 'Подписки'
        verbose_name = 'Подписка'

    def __str__(self):
        return f'@{self.user} @{self.author}'
