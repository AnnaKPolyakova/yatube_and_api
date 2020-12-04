from django.test import Client, TestCase
from django.urls import reverse
import shutil
import tempfile
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from posts.forms import PostForm
from posts.models import Group, Post, User

SLUG = 'test'
SLUG2 = 'test2'
NAME = 'test'
NAME2 = 'test2'

INDEX_URL = reverse('index')
GROUP_POSTS_URL = reverse('group_post', kwargs={'slug': SLUG})
GROUP_POSTS_URL2 = reverse('group_post', kwargs={'slug': SLUG2})
PROFILE_URL = reverse('profile', kwargs={'username': NAME})
NEW_POST_URL = reverse('new_post')


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # на момент теста медиа папка будет перопределена
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.user = User.objects.create_user(NAME, 'test@test.com', 'pass')
        cls.user2 = User.objects.create_user(NAME2, 'test@test.com', 'pass')
        cls.group = Group.objects.create(
            title='Название_тест',
            slug=SLUG,
            description='Тестовое описание группы',
        )
        cls.group2 = Group.objects.create(
            title='Название_тест2',
            slug=SLUG2,
            description='Тестовое описание группы',
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Рекурсивно удаляем временную после завершения тестов
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=False)

    def setUp(self):
        # Создаём неавторизованного клиента
        self.guest_client = Client()
        # Создаём авторизованного клиента
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post = Post.objects.create(
            text='Test',
            group=self.group,
            author=self.user,
        )
        self.POST_URL = reverse('post', kwargs={'username': NAME,
                                                'post_id': self.post.id})
        self.POST_EDIT_URL = reverse('post_edit',
                                     kwargs={'username': NAME,
                                             'post_id': self.post.id})

    def test_authorized_client_create_post(self):
        """Валидная форма создает запись в Post, редирект работает."""
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        data = {
            'text': 'Test',
            'group': self.group.id,
            'image': uploaded,
        }
        self.post.delete()
        response = self.authorized_client.post(
            NEW_POST_URL,
            data=data,
            follow=True
        )
        post = response.context['page'][0]
        self.assertEqual(post.text, data['text'])
        self.assertEqual(post.group.id, data['group'])
        self.assertIsNotNone(post.image)
        self.assertRedirects(response, INDEX_URL)
        self.assertEqual(Post.objects.count(), 1)

    def test_post_edit_can_cange_post(self):
        """Форма сохраняет измененную запись в Post."""
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x4b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Test_new',
            'group': self.group2.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            self.POST_EDIT_URL,
            data=form_data,
            follow=True
        )
        self.post.refresh_from_db()
        self.assertRedirects(response, self.POST_URL)
        self.assertEqual(form_data['text'], self.post.text)
        self.assertEqual(form_data['group'], self.post.group.id)
        self.assertEqual(form_data['group'], self.post.group.id)


