from django.test import TestCase

from ..models import Comment, Follow, Group, Post, User

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
        cls.user2 = User.objects.create_user(username='User2')
        cls.group = Group.objects.create(
            title=TEST_TITLE,
            slug=TEST_SLUG,
            description=TEST_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=TEST_TEXT,
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text=TEST_TEXT,
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        group = PostModelTest.group
        post = PostModelTest.post
        comment = PostModelTest.comment
        expected_group_title = group.title
        expected_post_title = post.text[:15]
        expected_comment_title = comment.text[:15]
        self.assertEqual(expected_group_title, str(group.title))
        self.assertEqual(expected_post_title, str(post.text[:15]))
        self.assertEqual(expected_comment_title, str(comment.text[:15]))


class FollowModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=TEST_USERNAME)
        cls.user2 = User.objects.create_user(username='User2')
        cls.post = Post.objects.create(
            author=cls.user,
            text=TEST_TEXT,
        )
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.user2
        )

    def test_follow_model(self):
        """Пользователь подписывается на автора"""
        follower = FollowModelTest.user
        following = FollowModelTest.user2
        follow_model = FollowModelTest.follow
        expected_follower_username = follower.username
        expected_following_username = following.username
        self.assertEqual(
            expected_follower_username, follow_model.user.username
        )
        self.assertEqual(
            expected_following_username, follow_model.author.username
        )
