from mixer.backend.django import mixer
from django.test import TestCase

from ..models import Group, Post, User
from ..constants import FIFTEEN_CHARACTERS, MODEL_INFO


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = mixer.blend(Group)
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост'
        )

    def test_model_post_have_correct_object_name(self):
        """Проверяем, что у модели Post корректно работает __str__."""
        object_name_post = self.post.text[:FIFTEEN_CHARACTERS]
        self.assertEqual(object_name_post, str(self.post))

    def test_model_group_have_correct_object_name(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        self.assertEqual(self.group.title, str(self.group))

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        for field, verbose, help in MODEL_INFO:
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).verbose_name, verbose)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        for field, verbose, help in MODEL_INFO:
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).help_text, help)
