from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User

SLUG = 'test'
NAME = 'test'
NAME2 = 'test2'

INDEX_URL = reverse('index')
GROUP_POSTS_URL = reverse('group_post', kwargs={'slug': SLUG})
ABOUT_AUTHOR = '/about-author/'
ABOUT_AUTHOR_URL = reverse('about-author')
TECHNOLOGIES = '/about-spec/'
TECHNOLOGIES_URL = reverse('about-spec')
PROFILE_URL = reverse('profile', kwargs={'username': NAME})
NEW_POST_URL = reverse('new_post')
LOGIN_URL = reverse('login')
FOLLOW_INDEX_URL = reverse('follow_index')
PAGE_NOT_EXIST_URL = '/dfdvdfcv/'
NEXT_URL = '?next='
NEW_POST_REDIRECTS_URL = LOGIN_URL + NEXT_URL + NEW_POST_URL


class URLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(NAME, 'test@test.com', 'pass')
        cls.site = Site(id=1, name='Site', domain='127.0.0.1:8000')
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
        cls.user2 = User.objects.create_user(NAME2, 'test2@test.com', 'pass')
        cls.group = Group.objects.create(
            title='Название_тест',
            slug=SLUG,
            description='Тестовое описание группы2',
        )
        cls.post = Post.objects.create(
            text='Test',
            group=cls.group,
            author=cls.user,
        )
        cls.POST_URL = reverse('post', kwargs={'username': NAME,
                                               'post_id': cls.post.id})
        cls.POST_EDIT_URL = reverse('post_edit',
                                    kwargs={'username': NAME,
                                            'post_id': cls.post.id})
        cls.ADD_COMMENT_URL = reverse('add_comment',
                                      kwargs={'username': NAME,
                                              'post_id': cls.post.id})

    def setUp(self):
        # Создаем неавторизованного клиента
        self.guest_client = Client()
        # Создаем авторизованного клиента
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    # Проверяем общедоступные страницы
    def test_url_exists_at_desired_location(self):
        """Страницы 'index','group_post', 'profile', 'post',
        TECHNOLOGIES,ABOUT_AUTHOR_URL
        доступны любому пользователю."""
        url_status_code = [
            GROUP_POSTS_URL,
            PROFILE_URL,
            self.POST_URL,
            TECHNOLOGIES_URL,
            ABOUT_AUTHOR_URL,
            INDEX_URL,
        ]
        for url in url_status_code:
            response = self.guest_client.get(url)
            with self.subTest('Ошибка' + url):
                self.assertEqual(response.status_code, 200)

    # Проверяем доступность страниц для авторизованного пользователя
    def test_pages_detail_url_exists_at_desired_location_authorized(self):
        """Страницы 'new_post', 'follow_index',
        доступны авторизованному пользователю,
         'post_edit' авторизованному пользователю автору поста"""
        url_status_code = [
            NEW_POST_URL,
            self.POST_EDIT_URL,
            FOLLOW_INDEX_URL,
        ]
        for url in url_status_code:
            response = self.authorized_client.get(url)
            with self.subTest('Ошибка' + url):
                self.assertEqual(response.status_code, 200)

    # Проверяем редиректы для неавторизованного пользователя
    def test_new_post_url_redirect_anonymous_on_admin_login(self):
        """Страница /'new_post'/ перенаправит анонимного пользователя
        на страницу логина."""
        response = self.client.get(NEW_POST_URL, follow=True)
        self.assertRedirects(
            response, NEW_POST_REDIRECTS_URL)

    # Проверка вызываемых шаблонов для каждого адреса
    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            INDEX_URL: 'index.html',
            GROUP_POSTS_URL: 'group.html',
            NEW_POST_URL: 'new_post.html',
            PROFILE_URL: 'profile.html',
            self.POST_EDIT_URL: 'new_post.html',
            self.POST_URL: 'post.html',
            FOLLOW_INDEX_URL: 'follow.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest('Ошибка' + url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_post_page_get_not_author(self):
        """Страница '/post_edit/' не доступна
        авторизованному пользователю (не автору поста)."""
        self.authorized_client.force_login(self.user2)
        response = self.authorized_client.get(self.POST_EDIT_URL)
        self.assertEqual(response.status_code, 302)

    def test_post_edit_chek_redirect_page(self):
        """Страница '/post_edit/' не доступна
        не авторизованному пользователю."""
        url_status_code = [
            NEW_POST_URL,
            self.POST_EDIT_URL,
            FOLLOW_INDEX_URL,
        ]
        for url in url_status_code:
            response = self.guest_client.get(url)
            with self.subTest('Ошибка' + url):
                self.assertEqual(response.status_code, 302)

    def test_post_edit_page(self):
        """Страница '/post_edit/' перенаправит
        зарегистрированного пользователя, но не автора поста
        на страницу поста."""
        self.authorized_client.force_login(self.user2)
        response = self.authorized_client.get(self.POST_EDIT_URL, follow=True)
        self.assertRedirects(response, self.POST_URL)

    def test_chek_tatus_code_404(self):
        """Проверяем, возвращает ли сервер код 404 """
        response = self.guest_client.get(PAGE_NOT_EXIST_URL)
        self.assertEqual(response.status_code, 404)
