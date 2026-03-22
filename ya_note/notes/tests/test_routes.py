from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(username='note_author')
        cls.reader = User.objects.create_user(username='note_reader')
        cls.note = Note.objects.create(
            title='Заметка',
            text='Текст заметки',
            slug='note-slug',
            author=cls.author,
        )
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.login_url = reverse('users:login')
        cls.home_url = reverse('notes:home')
        cls.list_url = reverse('notes:list')
        cls.add_url = reverse('notes:add')
        cls.success_url = reverse('notes:success')
        cls.detail_url = reverse('notes:detail', args=(cls.note.slug,))
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))

    def test_home_page_is_available_for_anonymous_user(self):
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_auth_pages_are_available_for_all_users(self):
        pages = (
            (reverse('users:login'), 'get'),
            (reverse('users:signup'), 'get'),
            (reverse('users:logout'), 'post'),
        )
        for client_name, should_login in (
            ('anonymous', False),
            ('authorized', True),
        ):
            for url, method in pages:
                client = Client()
                if should_login:
                    client.force_login(self.author)
                with self.subTest(client=client_name, url=url, method=method):
                    response = getattr(client, method)(url)
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_list_add_and_success_are_available_for_authorized_user(self):
        for url in (self.list_url, self.add_url, self.success_url):
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_detail_edit_and_delete_are_available_for_author(self):
        for url in (self.detail_url, self.edit_url, self.delete_url):
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_other_user_gets_404_for_foreign_note_pages(self):
        for url in (self.detail_url, self.edit_url, self.delete_url):
            with self.subTest(url=url):
                response = self.reader_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_anonymous_user_is_redirected_from_protected_pages(self):
        protected_urls = (
            self.list_url,
            self.add_url,
            self.success_url,
            self.detail_url,
            self.edit_url,
            self.delete_url,
        )
        for url in protected_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(
                    response,
                    f'{self.login_url}?next={url}',
                )
