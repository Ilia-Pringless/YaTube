from http import HTTPStatus

from django.test import Client, TestCase

from posts.models import Group, Post, User

TEST_USERNAME = 'HasNoName'
TEST_TITLE = 'test title'
TEST_SLUG = 'test-slug'
TEST_DESCRIPTION = 'test description'
TEST_TEXT = 'Тестовый текст'

MAIN = '/'
GROUP_LIST = f'/group/{TEST_SLUG}/'
PROFILE = f'/profile/{TEST_USERNAME}/'
CREATE = '/create/'
UNEXISTING = '/unexisting_page/'


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create(username=TEST_USERNAME)
        Group.objects.create(
            title=TEST_TITLE,
            slug=TEST_SLUG,
            description=TEST_DESCRIPTION,
        )
        Post.objects.create(
            text=TEST_TEXT,
            author=User.objects.get(username=TEST_USERNAME),
            pk=9,
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.get(username=TEST_USERNAME)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post = Post.objects.get(author=self.user)
        self.POST_DETAIL = f'/posts/{self.post.id}/'

    def test_urls_uses_correct_template(self):
        """URL-адрес доступен и использует соответствующий шаблон."""
        # Шаблоны по адресам
        templates_url_names = {
            MAIN: 'posts/index.html',
            GROUP_LIST: 'posts/group_list.html',
            PROFILE: 'posts/profile.html',
            self.POST_DETAIL: 'posts/post_detail.html',
        }
        for adress, template in templates_url_names.items():
            with self.subTest(template=template):
                response = self.guest_client.get(adress)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_post_id_uses_correct_template(self):
        """Страница по адресу post/post_id использует
           шаблон posts/post_detail.html"""
        creater = User.objects.get(username=TEST_USERNAME)
        if self.authorized_client == creater:
            response = self.authorized_client.get(self.POST_DETAIL)
            self.assertTemplateUsed(response, 'posts/post_detail.html')

    def test_create_correct_template(self):
        """Страница по адресу create/ использует
           шаблон posts/create_post.html"""
        response = self.authorized_client.get(CREATE)
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_unexesting_page_not_found(self):
        """Запрос к несуществующей страницу возвращает код 404"""
        response = self.guest_client.get(UNEXISTING)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
