import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Comment, Follow, Group, Post, User

SLUG = 'test'
SLUG2 = 'test2'
NAME = 'test'
NAME2 = 'test2'

INDEX_URL = reverse('index')
GROUP_POSTS_URL = reverse('group_post', kwargs={'slug': SLUG})
GROUP_POSTS_URL2 = reverse('group_post', kwargs={'slug': SLUG2})
PROFILE_URL = reverse('profile', kwargs={'username': NAME})
NEW_POST_URL = reverse('new_post')
FOLLOW_INDEX_URL = reverse('follow_index')
PROFILE_FOLLOW_URL = reverse('profile_follow', kwargs={'username': NAME2})
PROFILE_UNFOLLOW_URL = reverse('profile_unfollow', kwargs={'username': NAME2})

SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x01\x00'
    b'\x01\x00\x00\x00\x00\x21\xf9\x04'
    b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
    b'\x00\x00\x01\x00\x01\x00\x00\x02'
    b'\x02\x4c\x01\x00\x3b'
)


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
        cls.UPLOADED = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        cls.UPLOADED2 = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        cls.follow = Follow.objects.create(
            user=cls.user2,
            author=cls.user,
        )

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
            image=self.UPLOADED,
        )
        self.POST_URL = reverse('post', kwargs={'username': NAME,
                                                'post_id': self.post.id})
        self.POST_EDIT_URL = reverse('post_edit',
                                     kwargs={'username': NAME,
                                             'post_id': self.post.id})
        self.ADD_COMMENT_URL = reverse('add_comment',
                                       kwargs={'username': NAME,
                                               'post_id': self.post.id})

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_authorized_client_create_post(self):
        """Валидная форма создает запись в Post, редирект работает."""
        uploaded = self.UPLOADED2
        data = {
            'text': 'Test2',
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

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_post_edit_can_cange_post(self):
        """Форма сохраняет измененную запись в Post."""
        new_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x4b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=new_gif,
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
        self.assertEqual(self.post.image.size, form_data['image'].size)
        print(form_data['image'])
        print(self.post.image)

    def test_pages_get_image(self):
        """На страницах index, profile, post, group_post,
        profile_follow отображается картинка."""
        self.authorized_client.force_login(self.user2)
        text = '<img'
        text_code = str.encode(text, encoding='utf-8')
        url = (
            INDEX_URL,
            GROUP_POSTS_URL,
            PROFILE_URL,
            self.POST_URL,
            FOLLOW_INDEX_URL,
        )
        for url in url:
            with self.subTest('Ошибка' + url):
                response = self.authorized_client.get(url)
                self.assertContains(response, text)

    def test_authorized_client_can_subscribe_to_other_users(self):
        """Авторизованный пользователь может подписаться
        на других пользователей."""
        count = Follow.objects.count()
        response = self.authorized_client.get(PROFILE_FOLLOW_URL)
        follow = Follow.objects.filter(user=self.user,
                                       author=self.user2).exists()
        self.assertEqual(count+1, Follow.objects.count())
        self.assertEqual(True, follow)

    def test_authorized_client_can_unsubscribe_to_other_users(self):
        """Авторизованный пользователь может отписываться
        от пользователя."""
        follow = Follow.objects.create(
            user=self.user,
            author=self.user2,
        )
        count = Follow.objects.count()
        response = self.authorized_client.post(PROFILE_UNFOLLOW_URL)
        follow = Follow.objects.filter(
            user=self.user,
            author=self.user2).exists()
        self.assertEqual(count-1, Follow.objects.count())
        self.assertEqual(False, follow)

    def test_authorized_client_can_add_comment(self):
        """Авторизованный пользователь может
        добавить комментарий к посту."""
        data = {
            'text': 'Test_comment'
        }
        count = self.user.comments.count()
        response = self.authorized_client.post(
            self.ADD_COMMENT_URL,
            data=data,
            follow=True
        )
        count_comments_response = response.context['comments'].count()
        self.assertEqual(count + 1, self.user.comments.count())
        comment = response.context['comments'][0]
        self.assertEqual(comment.text, data['text'])
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.post, self.post)
        self.assertEqual(count_comments_response, 1)

    def test_gest_client_can_not_add_comment(self):
        """Не авторизованный пользователь неможет
        добавить комментарий к посту."""
        form_data = {
            'text': 'Test_comment'
        }
        count = self.user.comments.count()
        response = self.guest_client.post(
            self.ADD_COMMENT_URL,
            data=form_data,
        )
        self.assertEqual(count, self.user.comments.count())
