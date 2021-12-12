import shutil
import tempfile
from http import HTTPStatus

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Comment, Follow, Group, Post, User

COUNT_POST = settings.COUNT_POST

TEST_USERNAME = 'HasNoName'
TEST_TITLE = 'test title'
TEST_SLUG = 'test-slug'
TEST_DESCRIPTION = 'test description'
TEST_TEXT = 'Тестовый текст'
SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)

MAIN = '/'
GROUP_LIST = f'/group/{TEST_SLUG}/'
PROFILE = f'/profile/{TEST_USERNAME}/'
CREATE = '/create/'
FOLLOW_INDEX = '/follow/'

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create(username=TEST_USERNAME)
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif')
        Group.objects.create(
            title=TEST_TITLE,
            slug=TEST_SLUG,
            description=TEST_DESCRIPTION,
        )
        Post.objects.create(
            text=TEST_TEXT,
            author=User.objects.get(username=TEST_USERNAME),
            pk=9,
            group=Group.objects.get(title=TEST_TITLE),
            image=uploaded,
        )
        Comment.objects.create(
            post=Post.objects.get(text=TEST_TEXT),
            text=TEST_TEXT,
            author=User.objects.get(username=TEST_USERNAME)
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.group = Group.objects.get(title=TEST_TITLE)
        self.guest_client = Client()
        self.user = User.objects.get(username=TEST_USERNAME)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post = Post.objects.get(author=self.user)
        self.POST_DETAIL = f'/posts/{self.post.id}/'
        self.POST_EDIT = f'posts/{self.post.id}/edit/'

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'posts/index.html': MAIN,
            'posts/group_list.html': GROUP_LIST,
            'posts/profile.html': PROFILE,
            'posts/post_detail.html': self.POST_DETAIL,
            'posts/create_post.html': CREATE,
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_posts_post_id_uses_correct_template(self):
        """Страница по адресу posts:post_detail использует
           шаблон posts/post_detail.html"""
        if self.authorized_client == self.user:
            response = self.authorized_client.get(self.POST_DETAIL)
            self.assertTemplateUsed(response, 'posts/post_detail.html')

    def test_posts_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(MAIN)
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author
        post_group_0 = first_object.group
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, TEST_TEXT)
        self.assertEqual(post_author_0, self.user)
        self.assertEqual(post_group_0, self.group)
        self.assertEqual(post_image_0, self.post.image)

    def test_posts_group_posts_correct_context(self):
        """Шаблон group_posts сформирован с правильным контекстом."""
        response = self.authorized_client.get(GROUP_LIST)
        check_group = response.context.get('group')
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author
        post_group_0 = first_object.group
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, TEST_TEXT)
        self.assertEqual(post_author_0, self.user)
        self.assertEqual(post_group_0, self.group)
        self.assertEqual(post_image_0, self.post.image)
        # Проверка соответствия группы
        self.assertEqual(check_group, self.group)

    def test_posts_profile_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(PROFILE)
        check_author = response.context.get('author')
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author
        post_group_0 = first_object.group
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, TEST_TEXT)
        self.assertEqual(post_author_0, self.user)
        self.assertEqual(post_group_0, self.group)
        self.assertEqual(post_image_0, self.post.image)
        # Проверка соответсвия автора
        self.assertEqual(check_author, self.user)

    def test_posts_post_detail_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.POST_DETAIL)
        self.assertEqual(response.context['get_post'].text, TEST_TEXT)
        self.assertEqual(response.context['get_post'].author, self.user)
        self.assertEqual(response.context['get_post'].group, self.group)
        self.assertEqual(response.context['get_post'].image, self.post.image)
        # Проверка наличия комментария
        self.assertEqual(
            response.context['get_post'].comments, self.post.comments
        )
        # Проверка соответствия id
        self.assertEqual(response.context['get_post'].id, 9)

    def test_posts_edit_post_correct_context(self):
        """Страница post_edit использует правильный контекст"""
        if self.authorized_client == self.post.author:
            response = self.authorized_client.get(self.POST_EDIT)
            form_fields = {
                'text': forms.fields.CharField,
                'group': forms.fields.ChoiceField,
            }
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context['form'].fields[value]
                    self.assertIsInstance(form_field, expected)

    def test_posts_create_post_correct_context(self):
        """Страница post_create использует правильный контекст"""
        response = self.authorized_client.get(CREATE)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_in_main(self):
        """Созданый пост есть на главной странице"""
        response = self.authorized_client.get(MAIN)
        post = response.context['page_obj'][0]
        self.assertTrue(self.post == post)

    def test_post_in_group_list(self):
        """Созданый пост есть на странице group_list"""
        response = self.authorized_client.get(GROUP_LIST)
        post = response.context['page_obj'][0]
        if self.group == self.post.group:
            self.assertTrue(self.post == post)
        else:
            self.assertFalse(self.post == post)

    def test_post_in_profile(self):
        """Созданый пост есть на странице автора поста"""
        response = self.authorized_client.get(PROFILE)
        post = response.context['page_obj'][0]
        if self.user == self.post.author:
            self.assertTrue(self.post == post)
        else:
            self.assertFalse(self.post == post)


class PostsPaginatorTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # создание User
        User.objects.create(username=TEST_USERNAME)
        # Создание Group
        Group.objects.create(
            title=TEST_TITLE,
            slug=TEST_SLUG,
            description=TEST_DESCRIPTION,
        )
        # Создание Post(13)
        author = User.objects.get(username=TEST_USERNAME)
        group = Group.objects.get(title=TEST_TITLE)
        cls.posts = []
        for id in range(13):
            cls.post = Post.objects.create(
                id=id,
                text=TEST_TEXT,
                author=author,
                group=group
            )
            cls.posts.append(cls.post)

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.get(username=TEST_USERNAME)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_records(self):
        """Paginator на первой странице работает правильно"""
        # index
        response_index = self.client.get(MAIN)
        count_posts_index = len(response_index.context['page_obj'])
        # group_list
        response_group_list = self.client.get(GROUP_LIST)
        count_posts_group_list = len(response_group_list.context['page_obj'])
        # profile
        response_profile = self.client.get(PROFILE)
        count_posts_profile = len(response_profile.context['page_obj'])

        check_count_pages = [
            count_posts_index,
            count_posts_group_list,
            count_posts_profile
        ]
        for count_page in check_count_pages:
            with self.subTest(count_page=count_page):
                self.assertEqual(count_page, COUNT_POST)

    def test_second_page_contains_three_records(self):
        """Paginator на второй странице работает правильно"""
        # index
        response_index = self.client.get(MAIN + '?page=2')
        count_posts_index = len(response_index.context['page_obj'])
        # group_list
        response_group_list = self.client.get(GROUP_LIST + '?page=2')
        count_posts_group_list = len(response_group_list.context['page_obj'])
        # profile
        response_profile = self.client.get(PROFILE + '?page=2')
        count_posts_profile = len(response_profile.context['page_obj'])

        check_count_pages = [
            count_posts_index,
            count_posts_group_list,
            count_posts_profile
        ]
        for count_page in check_count_pages:
            with self.subTest(count_page=count_page):
                self.assertEqual(count_page, 3)


class CacheTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create(username=TEST_USERNAME)
        Post.objects.create(
            text=TEST_TEXT,
            author=User.objects.get(username=TEST_USERNAME),
        )

    def setUp(self):
        self.user = User.objects.get(username=TEST_USERNAME)
        self.guest_client = Client()
        self.post = Post.objects.get(author=self.user)

    def test_cache_index_page(self):
        response = self.guest_client.get(MAIN)
        Post.objects.all().delete()
        self.assertContains(response, self.post)
        cache.clear()
        self.assertNotIn(self.post, response.context['page_obj'])


class FollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create(username=TEST_USERNAME)
        User.objects.create(username='User_2')
        User.objects.create(username='User_3')
        Post.objects.create(
            text=TEST_TEXT,
            author=User.objects.get(username='User_2')
        )
        Follow.objects.create(
            user=User.objects.get(username=TEST_USERNAME),
            author=User.objects.get(username='User_2')
        )

    def setUp(self):
        self.user = User.objects.get(username=TEST_USERNAME)
        self.user_2 = User.objects.get(username='User_2')
        self.user_3 = User.objects.get(username='User_3')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.unfollow_client = Client()
        self.unfollow_client.force_login(self.user_2)
        self.post = Post.objects.get(author=self.user_2)

    def test_follow_user(self):
        """Авторизованный пользователь подписывается на автора"""
        count_follows = Follow.objects.filter(user=self.user).count()
        response = self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': 'User_3'}
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Follow.objects.count(), count_follows + 1)

    def test_unfollow_user(self):
        """Авторизованный пользователь отписывается от автора"""
        count_follows = Follow.objects.filter(user=self.user).count()
        response = self.authorized_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': 'User_2'}
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertTrue(Follow.objects.count() < count_follows)

    def test_follow_index(self):
        """Новая запись пользователя появляется в ленте подписчиков"""
        response_follow = self.authorized_client.get(FOLLOW_INDEX)
        text_in_page = response_follow.context['page_obj'][0].text
        self.assertEqual(text_in_page, self.post.text)
