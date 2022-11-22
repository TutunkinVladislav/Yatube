from mixer.backend.django import mixer
from django.core.cache import cache
from django.test import TestCase, Client
from django.urls import reverse
from django import forms

from ..models import Post, Group, User, Follow
from ..constants import SHOW_TEN_POSTS, SHOW_THREE_POSTS


class PostViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = mixer.blend(Group)
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )
        cls.INDEX_URL = (
            'posts:index',
            'posts/index.html',
            None,
        )
        cls.GROUP_URL = (
            'posts:group_list',
            'posts/group_list.html',
            (cls.group.slug,),
        )
        cls.PROFILE_URL = (
            'posts:profile',
            'posts/profile.html',
            (cls.post.author,),
        )
        cls.POST_URL = (
            'posts:post_detail',
            'posts/post_detail.html',
            (cls.post.pk,),
        )
        cls.EDIT_URL = (
            'posts:post_edit',
            'posts/create_post.html',
            (cls.post.pk,),
        )
        cls.CREATE_URL = (
            'posts:post_create',
            'posts/create_post.html',
            None,
        )

    def setUp(self):
        cache.clear()
        self.anon = Client()
        self.auth = Client()
        self.auth.force_login(PostViewsTest.user)

    def test_pages_templates(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            reverse(self.INDEX_URL[0]): self.INDEX_URL[1],

            reverse(
                self.GROUP_URL[0], args=self.GROUP_URL[2]
            ): self.GROUP_URL[1],

            reverse(
                self.PROFILE_URL[0], args=self.PROFILE_URL[2]
            ): self.PROFILE_URL[1],

            reverse(
                self.POST_URL[0], args=self.POST_URL[2]
            ): self.POST_URL[1],

            reverse(
                self.EDIT_URL[0], args=self.EDIT_URL[2]
            ): self.EDIT_URL[1],

            reverse(self.CREATE_URL[0]): self.CREATE_URL[1],
        }
        for reverse_name, template in templates_page_names.items():
            with self.subTest(template=template):
                response = self.auth.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.anon.get(reverse(self.INDEX_URL[0]))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author
        post_group_0 = first_object.group
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_author_0, self.post.author)
        self.assertEqual(post_group_0, self.post.group)
        self.assertEqual(post_image_0, self.post.image)

    def test_group_list_page(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.anon.get(
            reverse(
                self.GROUP_URL[0], args=self.GROUP_URL[2]
            )
        )
        self.assertEqual(response.context['group'].title, self.group.title)
        self.assertEqual(response.context['group'].slug, self.group.slug)
        self.assertEqual(
            response.context['group'].description, self.group.description
        )
        self.assertEqual(
            response.context['page_obj'][0].image, self.post.image
        )

    def test_profile_page(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.auth.get(
            reverse(
                self.PROFILE_URL[0], args=self.PROFILE_URL[2]
            )
        )
        self.assertEqual(
            response.context['author'].username, self.user.username
        )
        self.assertEqual(
            response.context['page_obj'][0].image, self.post.image
        )

    def test_post_detail_page(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.anon.get(
            reverse(
                self.POST_URL[0], args=self.POST_URL[2]
            )
        )
        self.assertEqual(response.context['post'].text, self.post.text)
        self.assertEqual(response.context['post'].pk, self.post.pk)
        self.assertEqual(response.context['post'].author, self.post.author)
        self.assertEqual(response.context['post'].group, self.post.group)
        self.assertEqual(response.context['post'].image, self.post.image)
        self.assertEqual(response.context['post'].comments, self.post.comments)

    def test_create_page(self):
        """Шаблон create сформирован с правильным контекстом."""
        response_create = self.auth.get(
            reverse(self.CREATE_URL[0])
        )
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response_create.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_edit_page(self):
        """Шаблон edit сформирован с правильным контекстом."""
        response_edit = self.auth.get(
            reverse(self.EDIT_URL[0], args=self.EDIT_URL[2])
        )
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response_edit.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_check_post_in_pages(self):
        """Проверяем создание поста на страницах с выбранной группой"""
        form_fields = {
            reverse(
                self.INDEX_URL[0]
            ): Post.objects.get(group=self.post.group),
            reverse(
                self.GROUP_URL[0], args=self.GROUP_URL[2]
            ): Post.objects.get(group=self.post.group),
            reverse(
                self.PROFILE_URL[0], args=self.PROFILE_URL[2]
            ): Post.objects.get(group=self.post.group),
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                response = self.auth.get(value)
                form_field = response.context["page_obj"]
                self.assertIn(expected, form_field)

    def test_check_post_if_not_group(self):
        """Проверяем чтобы созданный пост с группой не попап в чужую группу."""
        form_fields = {
            reverse(
                self.GROUP_URL[0], args=self.GROUP_URL[2]
            ): Post.objects.exclude(group=self.post.group),
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                response = self.auth.get(value)
                form_field = response.context["page_obj"]
                self.assertNotIn(expected, form_field)

    def test_cache_index(self):
        """Проверка кэша для index."""
        response = self.anon.get(reverse('posts:index'))
        posts = response.content
        Post.objects.get(id=self.post.id).delete()
        response_old = self.anon.get(reverse('posts:index'))
        old_posts = response_old.content
        self.assertEqual(old_posts, posts)
        cache.clear()
        response_new = self.anon.get(reverse('posts:index'))
        new_posts = response_new.content
        self.assertNotEqual(old_posts, new_posts)

    def test_follow_and_new_post_in_follow(self):
        """Подписка на пользователя и появление нового поста в подписке"""
        Follow.objects.all().delete()
        Follow.objects.create(user=self.user, author=self.post.author)
        response = self.auth.get(reverse('posts:follow_index'))
        follow_page = response.context['page_obj']
        self.assertIn(self.post, follow_page)

    def test_unfollow(self):
        """Удаление подписок"""
        Follow.objects.filter(user=self.user, author=self.post.author).delete()
        response = self.auth.get(reverse('posts:follow_index'))
        follow_page = response.context['page_obj']
        self.assertNotIn(self.post, follow_page)

    def test_check_new_post_in_unfollow(self):
        """Новый пост не появляется у пользователя который не подписан"""
        Follow.objects.create(user=self.user, author=self.post.author)
        new_user = User.objects.create(username='NewUser')
        self.auth.force_login(new_user)
        response = self.auth.get(reverse('posts:follow_index'))
        follow_page = response.context['page_obj']
        self.assertNotIn(self.post, follow_page)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = mixer.blend(Group)

        cls.post = Post.objects.bulk_create([
            Post(
                author=cls.user,
                text=f'Тестовый пост {i}',
                group=cls.group
            ) for i in range(SHOW_TEN_POSTS + SHOW_THREE_POSTS)
        ])

    def test_first_page_contains_ten_records(self):
        """Проверяем что на первой странице отображается 10 постов"""
        cache.clear()
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), SHOW_TEN_POSTS)

        response = self.client.get(
            reverse('posts:group_list', args=[self.group.slug])
        )
        self.assertEqual(len(response.context['page_obj']), SHOW_TEN_POSTS)

        response = self.client.get(
            reverse('posts:profile', args=[self.user.username])
        )
        self.assertEqual(len(response.context['page_obj']), SHOW_TEN_POSTS)

    def test_second_page_contains_three_records(self):
        """Проверяем что на второй странице отображается 3 поста"""
        cache.clear()
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), SHOW_THREE_POSTS)

        response = self.client.get(reverse(
            'posts:group_list', args=[self.group.slug]) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), SHOW_THREE_POSTS)

        response = self.client.get(reverse(
            'posts:profile', args=[self.user.username]) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), SHOW_THREE_POSTS)
