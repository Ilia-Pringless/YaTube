from django.test import TestCase

from ..models import Group, Post, User

TEST_USERNAME = 'HasNoName'
TEST_TITLE = 'test title'
TEST_SLUG = 'test-slug'
TEST_DESCRIPTION = 'test description'
TEST_TEXT = 'Тестовый тeкст'


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=TEST_USERNAME)
        cls.group = Group.objects.create(
            title=TEST_TITLE,
            slug=TEST_SLUG,
            description=TEST_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=TEST_TEXT,
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        group = PostModelTest.group
        post = PostModelTest.post
        expected_group_title = group.title
        expected_post_title = post.text[:15]
        self.assertEqual(expected_group_title, str(group.title))
        self.assertEqual(expected_post_title, str(post.text[:15]))
