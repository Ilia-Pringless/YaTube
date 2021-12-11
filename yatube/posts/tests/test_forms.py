import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Comment, Post, User

TEST_USERNAME = 'HasNoName'
TEST_TITLE = 'test title'
TEST_SLUG = 'test-slug'
TEST_DESCRIPTION = 'test description'
TEST_TEXT = 'Тестовый текст'

MAIN = '/'
GROUP_LIST = f'/group/{TEST_SLUG}/'
PROFILE = f'/profile/{TEST_USERNAME}/'
CREATE = '/create/'


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create(username=TEST_USERNAME)
        Post.objects.create(
            text=TEST_TEXT,
            author=User.objects.get(username=TEST_USERNAME)
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.user = User.objects.get(username=TEST_USERNAME)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post = Post.objects.get(author=self.user)
        self.POST_EDIT = f'posts/{self.post.id}/edit/'
        self.POST_DETAIL = f'/posts/{self.post.id}/'

    def test_create_post(self):
        """Валидная форма создает запись в Post"""
        posts_count = Post.objects.count()

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        form_data = {
            'text': 'Тестовый текст 2',
            'image': uploaded,
        }

        response = self.authorized_client.post(
            CREATE,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, PROFILE)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст 2',
                image='posts/small.gif'
            ).exists()
        )

    def test_edit_post(self):
        """Валидная форма изменит существующую запись"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Новый тестовый текст',
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=[self.post.id]),
            data=form_data,
            follow=True)
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertRedirects(response,
                             self.POST_DETAIL)
        self.assertTrue(
            (Post.objects.get(id=self.post.id).text == form_data['text']))
        self.assertEqual(response.status_code, HTTPStatus.OK)


class CommentCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create(username=TEST_USERNAME)
        Post.objects.create(
            text=TEST_TEXT,
            author=User.objects.get(username=TEST_USERNAME)
        )
        Comment.objects.create(
            post=Post.objects.get(text=TEST_TEXT),
            author=User.objects.get(username=TEST_USERNAME),
            text=TEST_TEXT,
        )

    def setUp(self):
        self.user = User.objects.get(username=TEST_USERNAME)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post = Post.objects.get(author=self.user)
        self.POST_DETAIL = f'/posts/{self.post.id}/'
        self.ADD_COMMENT = f'/posts/{self.post.id}/comment/'

    def test_create_comment(self):
        """Валидная форма создаст новую запись в Comment"""
        comment_count = Comment.objects.count()
        form_data = {
            'post': self.post,
            'text': 'Тестовый текст 2',
            'author': self.user,
        }
        response = self.authorized_client.post(
            self.ADD_COMMENT,
            data=form_data,
            follow=True
        )
        response_get = self.authorized_client.get(self.POST_DETAIL)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, self.POST_DETAIL)
        self.assertEqual(
            response_get.context['get_post'].comments, self.post.comments
        )
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                post=self.post,
                text='Тестовый текст 2',
            ).exists()
        )
