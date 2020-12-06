from django.test import TestCase

from posts.models import Group, Post, User, Comment, Follow

SLUG = 'test'
NAME = 'test'
NAME2 = 'test2'


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Название_тест',
            slug=SLUG,
            description='Тестовое описание группы',
        )

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        field_verboses = {
            'title': 'Группа',
            'slug': 'Адрес для страницы с задачей',
            'description': 'Описание'
        }
        for value, expected in field_verboses.items():
            with self.subTest():
                self.assertEqual(
                    self.group._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        field_help_texts = {
            'title': 'Не более 200 символов',
            'slug': 'Не более 40 символов',
            'description': 'Краткое описание',
        }
        for value, expected in field_help_texts.items():
            with self.subTest():
                self.assertEqual(
                    self.group._meta.get_field(value).help_text, expected)

    def test_str(self):
        """Метод str выводит ожидаемые значения."""
        group = str(GroupModelTest.group)
        field_help_texts = {
            'title': 'Название_тест'
        }
        for value, expected in field_help_texts.items():
            with self.subTest():
                self.assertEqual(
                    group, expected)


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(NAME, 'test@test.com', 'pass')
        cls.post = Post.objects.create(
            text='1234567891123456',
            author=cls.user,
        )

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст',
            'pub_date': 'Дата публикации',
            'author': "Автор",
            'group': 'Группа',
        }
        for value, expected in field_verboses.items():
            with self.subTest():
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Поведуйте миру о себе. <p> '
                    '*Поле обязательно для заполнения. </p>',
            'group': 'Возможно, будет уместно выбрать '
                     'соответствубщую Вашему посту группу.'
        }
        for value, expected in field_help_texts.items():
            with self.subTest():
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)

    def test_str(self):
        """Метод str выводит ожидаемые значения."""
        post = self.post
        expected_object_name = (f'{post.text[:15]} @{post.author} '
                                f'#{post.group} {post.pub_date}')
        self.assertEquals(expected_object_name, str(post))


class CommentModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(NAME, 'test@test.com', 'pass')
        cls.post = Post.objects.create(
            text='Test',
            author=cls.user,
        )
        cls.comment = Comment.objects.create(
            text='Test',
            author=cls.user,
            post=cls.post,
        )

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        comment = CommentModelTest.comment
        field_verboses = {
            'post': 'Пост',
            'author': 'Автор',
            'text': "Текст",
            'created': 'Дата публикации',
        }
        for value, expected in field_verboses.items():
            with self.subTest():
                self.assertEqual(
                    comment._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        comment = CommentModelTest.comment
        field_help_texts = {
            'text': 'Добавье свой комментарий. '
                    '<p> *Поле обязательно для заполнения. </p>',
        }
        for value, expected in field_help_texts.items():
            with self.subTest():
                self.assertEqual(
                    comment._meta.get_field(value).help_text, expected)

    def test_str(self):
        """Метод str выводит ожидаемые значения."""
        comment = self.comment
        expected_object_name = (f'{comment.text[:15]} @{comment.author} '
                                f'#{comment.post} {comment.created}')
        self.assertEquals(expected_object_name, str(comment))


class FollowModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(NAME, 'test@test.com', 'pass')
        cls.user2 = User.objects.create_user(NAME2, 'test2@test.com', 'pass')
        cls.follow = Follow.objects.create(
            author=cls.user,
            user=cls.user2,
        )

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        follow = FollowModelTest.follow
        field_verboses = {
            'user': 'Подписчик',
            'author': 'Пользователь на которого подписались',
        }
        for value, expected in field_verboses.items():
            with self.subTest():
                self.assertEqual(
                    follow._meta.get_field(value).verbose_name, expected)

    def test_str(self):
        """Метод str выводит ожидаемые значения."""
        follow = self.follow
        expected_object_name = (f'@{follow.user} @{follow.author}')
        self.assertEquals(expected_object_name, str(follow))
