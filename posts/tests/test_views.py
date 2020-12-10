import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Comment, Follow, Group, Post, User

SLUG = 'test'
SLUG2 = 'test2'
NAME = 'test'
NAME2 = 'test2'

INDEX_URL = reverse('index')
GROUP_POSTS_URL = reverse('group_post', kwargs={'slug': SLUG})
GROUP_POSTS_URL2 = reverse('group_post', kwargs={'slug': SLUG2})
ABOUT_AUTHOR = '/about-author/'
ABOUT_AUTHOR_URL = reverse('about-author')
TECHNOLOGIES = '/about-spec/'
TECHNOLOGIES_URL = reverse('about-spec')
PROFILE_URL = reverse('profile', kwargs={'username': NAME})
NEW_POST_URL = reverse('new_post')
FOLLOW_INDEX_URL = reverse('follow_index')
SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x01\x00'
    b'\x01\x00\x00\x00\x00\x21\xf9\x04'
    b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
    b'\x00\x00\x01\x00\x01\x00\x00\x02'
    b'\x02\x4c\x01\x00\x3b'
)


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # на момент теста медиа папка будет перопределена
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.user = User.objects.create_user(
            username=NAME,
            first_name='test_name',
            last_name='test_last_name'
        )
        cls.user2 = User.objects.create_user(
            username=NAME2,
            first_name='test_name',
            last_name='test_last_name'
        )
        cls.group = Group.objects.create(
            title='Название_тест',
            slug=SLUG,
            description='Тестовое описание группы',
        )
        cls.group2 = Group.objects.create(
            title='Название_тест2',
            slug=SLUG2,
            description='Тестовое описание группы2',
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        cls.site = Site(id=1, name='site', domain='127.0.0.1:8000')
        cls.site.save()
        cls.about_author = FlatPage.objects.create(
            title='about_author',
            url=ABOUT_AUTHOR,
            content='about_author'
        )
        cls.technologies = FlatPage.objects.create(
            title='technologies',
            url=TECHNOLOGIES,
            content='about_spec'
        )
        cls.about_author.sites.add(cls.site)
        cls.technologies.sites.add(cls.site)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Рекурсивно удаляем временную после завершения тестов
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        # Создаём неавторизованного клиента
        self.guest_client = Client()
        # Создаём авторизованного клиента
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.follow = Follow.objects.create(
            user=self.user,
            author=self.user2,
        )
        self.post = Post.objects.create(
            text='Test',
            group=self.group,
            author=self.user,
            image=self.uploaded,
        )
        self.POST_URL = reverse('post', kwargs={
            'username': NAME,
            'post_id': self.post.id})
        self.POST_EDIT_URL = reverse('post_edit', kwargs={
            'username': NAME,
            'post_id': self.post.id})
        self.comment = Comment.objects.create(
            text='Test',
            author=self.user,
            post=self.post,
        )

    def test_new_post_show_correct_context(self):
        """Шаблон new_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(NEW_POST_URL)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest():
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        """Шаблон edit_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.POST_EDIT_URL)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest():
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_index_show_correct_object_list(self):
        """Шаблон index сформирован с нужным кол-вом потов."""
        for value in range(10):
            Post.objects.create(
                text='Test',
                author=self.user,
            )
        response = self.authorized_client.get(INDEX_URL)
        posts_count = len(response.context.get('page').object_list)
        self.assertLessEqual(posts_count, 10)

    def test_group_post_show_correct_context(self):
        """Шаблон group_post сформирован с правильным контекстом (group)."""
        response = self.authorized_client.get(GROUP_POSTS_URL)
        response_group = response.context.get('group')
        self.assertEqual(self.group, response_group)

    def test_index_and_group_posts_and_profile_show_correct_context_page(self):
        """Шаблон index, group_post, profile
        сформирован с правильным контекством (page)"""
        url = (
            INDEX_URL,
            GROUP_POSTS_URL,
            PROFILE_URL,
        )
        for url in url:
            with self.subTest('Ошибка'+url):
                response = self.authorized_client.get(url)
                count_page_response = len(response.context['page'].object_list)
                self.assertEqual(count_page_response, 1)
                post = response.context['page'][0]
                self.assertEqual(self.post,
                                 post,)

    def test_profile_and_post_show_correct_context_author(self):
        """Шаблон profile, post сформирован
        с правильным контекстом (author)."""
        url = (
            PROFILE_URL,
            self.POST_URL,
        )
        for url in url:
            with self.subTest('Ошибка:'+url):
                response = self.authorized_client.get(url)
                author_context = response.context.get('author')
                self.assertEqual(author_context,
                                 self.user)

    def test_post_show_correct_context(self):
        """Шаблон group_post сформирован с правильным
        контекстом (comments)."""
        response = self.authorized_client.get(self.POST_URL)
        count_comments_response = response.context['comments'].count()
        self.assertEqual(count_comments_response, 1)
        comments_context = response.context.get('comments')[0]
        self.assertEqual(self.comment, comments_context)

    def test_about_author_show_correct_context(self):
        """Шаблон about_author сформирован с правильным контекстом."""
        response = self.guest_client.get(ABOUT_AUTHOR_URL)
        self.assertEqual(self.about_author.content,
                         response.context.get('flatpage').content)
        self.assertEqual(self.about_author.title,
                         response.context.get('flatpage').title)
        self.assertEqual(self.about_author.url,
                         response.context.get('flatpage').url)

    def test_technologies_show_correct_context(self):
        """Шаблон technologies сформирован с правильным контекстом."""
        response = self.guest_client.get(TECHNOLOGIES_URL)
        self.assertEqual(self.technologies.content,
                         response.context.get('flatpage').content)
        self.assertEqual(self.technologies.title,
                         response.context.get('flatpage').title)
        self.assertEqual(self.technologies.url,
                         response.context.get('flatpage').url)

    def test_post_whith_group_do_not_get_to_group_post(self):
        # Удостоверимся, что на страницу group_post не передаётся
        # пост с отличающейся группой
        response = self.authorized_client.get(GROUP_POSTS_URL2)
        page_response = response.context.get('page')
        self.assertNotIn(self.post, page_response)

    def test_index_cash_is_working(self):
        # Удостоверимся, что на странице index работает cash  на вывод постов
        response = self.authorized_client.get(INDEX_URL)
        content_cash = response.content
        self.post2 = Post.objects.create(
            text='Test_cash',
            author=self.user,
        )
        response = self.authorized_client.get(INDEX_URL)
        content_new = response.content
        comments_count_response = response.content
        self.assertEqual(content_cash, content_new)
        cache.clear()
        response = self.authorized_client.get(INDEX_URL)
        content_update = response.content
        self.assertNotEqual(content_cash, content_update)

    def test_post_following_get_to_favorite_author_page(self):
        # Удостоверимся, что новая запись пользователя появляется
        # в ленте тех, кто на него подписан.
        self.post = Post.objects.create(
            text='Test',
            author=self.user2,
        )
        response = self.authorized_client.get(FOLLOW_INDEX_URL)
        page_response = response.context.get('page')
        self.assertIn(self.post, page_response)

    def test_post_following_do_not_get_to_not_favorite_author_page(self):
        # Удостоверимся, что новая запись пользователя
        # не появляется в ленте тех,
        # кто не подписан на него.
        self.follow.delete()
        self.authorized_client.force_login(self.user2)
        response = self.authorized_client.get(FOLLOW_INDEX_URL)
        page_response = response.context.get('page')
        self.assertNotIn(self.post, page_response)
