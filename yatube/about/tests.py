from http import HTTPStatus

from django.test import Client, TestCase

AUTHOR_URL = '/about/author/'
TECH_URL = '/about/tech/'


class AboutURLTest(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_static_pages(self):
        """Проверка доступности и соответствующего шаблона."""
        templates_url_names = {
            AUTHOR_URL: 'about/author.html',
            TECH_URL: 'about/tech.html',
        }
        for adress, template in templates_url_names.items():
            with self.subTest(template=template):
                response = self.guest_client.get(adress)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, HTTPStatus.OK)
