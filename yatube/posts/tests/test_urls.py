from mixer.backend.django import mixer
from django.core.cache import cache
from django.test import TestCase, Client
from http import HTTPStatus

from ..models import Post, Group, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = mixer.blend(Group)
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.PAGE_INDEX = '/'
        cls.PAGE_GROUP = f'/group/{cls.group.slug}/'
        cls.PAGE_PROFILE = f'/profile/{cls.post.author}/'
        cls.PAGE_POST = f'/posts/{cls.post.pk}/'
        cls.PAGE_CREATE = '/create/'
        cls.PAGE_EDIT = f'/posts/{cls.post.pk}/edit/'

        cls.URL_TEMPLATE = (
            (cls.PAGE_INDEX, 'posts/index.html'),
            (cls.PAGE_GROUP, 'posts/group_list.html'),
            (cls.PAGE_PROFILE, 'posts/profile.html'),
            (cls.PAGE_POST, 'posts/post_detail.html'),
            (cls.PAGE_CREATE, 'posts/create_post.html'),
            (cls.PAGE_EDIT, 'posts/create_post.html'),
        )

    def setUp(self):
        self.anon = Client()
        self.auth = Client()
        self.auth.force_login(PostURLTests.user)

    def test_page_for_guest(self):
        """Проверяем страницы для неавторизованных пользователей"""
        list_page_guest = [
            self.PAGE_INDEX,
            self.PAGE_GROUP,
            self.PAGE_PROFILE,
            self.PAGE_POST
        ]
        for page in list_page_guest:
            with self.subTest(page=page):
                response = self.anon.get(page)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_page_for_authorized(self):
        """Проверяем страницы для авторизованных пользователей"""
        list_page_authorized = [
            self.PAGE_CREATE,
            self.PAGE_EDIT
        ]
        for page in list_page_authorized:
            with self.subTest(page=page):
                response = self.auth.get(page)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_page_unexisting(self):
        """Проверяем запрос, который обращается к несуществующей странице"""
        response = self.anon.get('/unexisting_page/')
        self.assertTemplateUsed(response, 'core/404.html')

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        cache.clear()
        for url, template in self.URL_TEMPLATE:
            with self.subTest(url=url):
                response = self.auth.get(url)
                self.assertTemplateUsed(response, template)
