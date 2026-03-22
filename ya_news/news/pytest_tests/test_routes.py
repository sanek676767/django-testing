from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects


ANONYMOUS_CLIENT = pytest.lazy_fixture('client')
AUTHOR_CLIENT = pytest.lazy_fixture('author_client')
READER_CLIENT = pytest.lazy_fixture('reader_client')

HOME_URL = pytest.lazy_fixture('home_url')
DETAIL_URL = pytest.lazy_fixture('detail_url')
LOGIN_URL = pytest.lazy_fixture('login_url')
SIGNUP_URL = pytest.lazy_fixture('signup_url')
LOGOUT_URL = pytest.lazy_fixture('logout_url')
EDIT_URL = pytest.lazy_fixture('edit_url')
DELETE_URL = pytest.lazy_fixture('delete_url')

STATUS_CASES = (
    (ANONYMOUS_CLIENT, 'get', HOME_URL, HTTPStatus.OK),
    (ANONYMOUS_CLIENT, 'get', DETAIL_URL, HTTPStatus.OK),
    (ANONYMOUS_CLIENT, 'get', LOGIN_URL, HTTPStatus.OK),
    (ANONYMOUS_CLIENT, 'get', SIGNUP_URL, HTTPStatus.OK),
    (ANONYMOUS_CLIENT, 'post', LOGOUT_URL, HTTPStatus.OK),
    (AUTHOR_CLIENT, 'get', EDIT_URL, HTTPStatus.OK),
    (AUTHOR_CLIENT, 'get', DELETE_URL, HTTPStatus.OK),
    (READER_CLIENT, 'get', EDIT_URL, HTTPStatus.NOT_FOUND),
    (READER_CLIENT, 'get', DELETE_URL, HTTPStatus.NOT_FOUND),
)

REDIRECT_CASES = (
    EDIT_URL,
    DELETE_URL,
)


@pytest.mark.parametrize(
    'user_client, method, url, expected_status',
    STATUS_CASES,
)
def test_status_codes(user_client, method, url, expected_status):
    response = getattr(user_client, method)(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize('url', REDIRECT_CASES)
def test_redirects_to_login(client, login_url, url):
    response = client.get(url)
    assertRedirects(response, f'{login_url}?next={url}')
