import shutil
import tempfile

from mixer.backend.django import mixer
from django.test import TestCase, Client, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.urls import reverse
from http import HTTPStatus

from ..models import Post, Group, User, Comment
from ..constants import ONE_POST

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
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

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.auth = Client()
        self.auth.force_login(PostFormTests.user)

    def test_post_create(self):
        """Валидная форма создает запись в Post."""
        Post.objects.all().delete()
        posts_count = Post.objects.count()
        picture = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='picture.gif',
            content=picture,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Новый текст поста',
            'image': uploaded,
        }
        response = self.auth.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', args=[self.user.username])
        )
        self.assertEqual(Post.objects.count(), posts_count + ONE_POST)
        self.assertTrue(
            Post.objects.filter(
                text='Новый текст поста',
                image='posts/picture.gif'
            ).exists()
        )

    def test_post_edit(self):
        """Валидная форма редактирует запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Редактируемый текст поста',
            'group': self.group.pk
        }
        response = self.auth.post(
            reverse('posts:post_edit', args=[self.post.pk]),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk})
        )
        self.assertEqual(Post.objects.count(), posts_count)
        post_obj = Post.objects.get(pk=self.post.pk)
        self.assertEqual(post_obj.text, 'Редактируемый текст поста')
        self.assertEqual(post_obj.group, self.post.group)
        self.assertEqual(post_obj.author, self.post.author)

    def test_new_comment_auth_user(self):
        """Новый комментарий на странице поста,"""
        """созданный авторизованным пользователем"""
        Comment.objects.all().delete()
        comment_count = Comment.objects.count()

        form_data = {
            'text': 'Новый текст комментария'
        }
        response = self.auth.post(
            reverse('posts:add_comment', args=[self.post.pk]),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, reverse(
            'posts:post_detail', args=[self.post.pk])
        )
        self.assertEqual(Comment.objects.count(), comment_count + ONE_POST)
        self.assertTrue(
            Comment.objects.filter(
                text='Новый текст комментария',
            ).exists()
        )
