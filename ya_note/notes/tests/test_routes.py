from http import HTTPStatus

from .common import (
    ADD_URL,
    HOME_URL,
    LIST_URL,
    LOGIN_URL,
    LOGOUT_URL,
    SIGNUP_URL,
    SUCCESS_URL,
    BaseNoteTestCase,
)


class TestRoutes(BaseNoteTestCase):

    def test_status_codes(self):
        cases = (
            ('anonymous', self.client, 'get', HOME_URL, HTTPStatus.OK),
            ('anonymous', self.client, 'get', LOGIN_URL, HTTPStatus.OK),
            ('anonymous', self.client, 'get', SIGNUP_URL, HTTPStatus.OK),
            ('anonymous', self.client, 'post', LOGOUT_URL, HTTPStatus.OK),
            ('author', self.author_client, 'get', LOGIN_URL, HTTPStatus.OK),
            ('author', self.author_client, 'get', SIGNUP_URL, HTTPStatus.OK),
            ('author', self.author_client, 'get', LIST_URL, HTTPStatus.OK),
            ('author', self.author_client, 'get', ADD_URL, HTTPStatus.OK),
            ('author', self.author_client, 'get', SUCCESS_URL, HTTPStatus.OK),
            (
                'author',
                self.author_client,
                'get',
                self.detail_url,
                HTTPStatus.OK,
            ),
            (
                'author',
                self.author_client,
                'get',
                self.edit_url,
                HTTPStatus.OK,
            ),
            (
                'author',
                self.author_client,
                'get',
                self.delete_url,
                HTTPStatus.OK,
            ),
            ('author', self.author_client, 'post', LOGOUT_URL, HTTPStatus.OK),
            (
                'reader',
                self.reader_client,
                'get',
                self.detail_url,
                HTTPStatus.NOT_FOUND,
            ),
            (
                'reader',
                self.reader_client,
                'get',
                self.edit_url,
                HTTPStatus.NOT_FOUND,
            ),
            (
                'reader',
                self.reader_client,
                'get',
                self.delete_url,
                HTTPStatus.NOT_FOUND,
            ),
        )
        for client_name, client, method, url, expected_status in cases:
            with self.subTest(
                client=client_name,
                method=method,
                url=url,
                expected_status=expected_status,
            ):
                response = getattr(client, method)(url)
                self.assertEqual(response.status_code, expected_status)

    def test_redirects(self):
        protected_urls = (
            LIST_URL,
            ADD_URL,
            SUCCESS_URL,
            self.detail_url,
            self.edit_url,
            self.delete_url,
        )
        for url in protected_urls:
            with self.subTest(
                client='anonymous',
                url=url,
                expected_redirect=f'{LOGIN_URL}?next={url}',
            ):
                response = self.client.get(url)
                self.assertRedirects(response, f'{LOGIN_URL}?next={url}')
