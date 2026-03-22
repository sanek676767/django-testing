from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'url_name, object_fixture',
    (
        ('news:home', None),
        ('news:detail', 'news'),
    ),
)
def test_pages_are_available_for_anonymous_user(
    client,
    request,
    url_name,
    object_fixture,
):
    kwargs = {}
    if object_fixture is not None:
        obj = request.getfixturevalue(object_fixture)
        kwargs = {'pk': obj.pk}
    response = client.get(reverse(url_name, kwargs=kwargs))
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize('url_fixture', ('edit_url', 'delete_url'))
def test_comment_pages_are_available_for_author(
    author_client,
    request,
    url_fixture,
):
    url = request.getfixturevalue(url_fixture)
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize('url_fixture', ('edit_url', 'delete_url'))
def test_anonymous_user_is_redirected_from_comment_pages(
    client,
    request,
    url_fixture,
):
    url = request.getfixturevalue(url_fixture)
    login_url = reverse('users:login')
    response = client.get(url)
    assertRedirects(response, f'{login_url}?next={url}')


@pytest.mark.parametrize('url_fixture', ('edit_url', 'delete_url'))
def test_not_author_gets_404_for_comment_pages(
    reader_client,
    request,
    url_fixture,
):
    url = request.getfixturevalue(url_fixture)
    response = reader_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize(
    'url_name, method',
    (
        ('users:login', 'get'),
        ('users:signup', 'get'),
        ('users:logout', 'post'),
    ),
)
def test_auth_pages_are_available_for_anonymous_user(
    client,
    url_name,
    method,
):
    url = reverse(url_name)
    response = getattr(client, method)(url)
    assert response.status_code == HTTPStatus.OK
